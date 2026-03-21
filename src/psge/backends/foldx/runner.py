"""FoldX runner for ΔΔG stability (Phase 1.6b)."""

import hashlib
import re
import shutil
import subprocess
from pathlib import Path

from psge.core.models import Config, StabilityResult, StructurePair
from psge.utils.pdb_distances import get_pdb_residue_for_foldx
from psge.utils.variant_parse import variant_position


def detect_foldx(foldx_path: str | None = None) -> str | None:
    """
    Detect FoldX executable. Checks foldx_path, FOLDX_PATH env, then PATH.
    Returns path to executable or None if not found.
    """
    if foldx_path and Path(foldx_path).exists():
        return foldx_path
    import os
    env_path = os.environ.get("FOLDX_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    which = shutil.which("foldx") or shutil.which("FoldX")
    return which


def get_foldx_version(executable: str) -> str | None:
    """Run FoldX --help or similar to capture version. Returns version string or None."""
    try:
        result = subprocess.run(
            [executable, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = (result.stdout or "") + (result.stderr or "")
        # Common patterns: "FoldX 5", "Version 5.0", etc.
        m = re.search(r"FoldX\s+(\d[\d.]*)", out, re.I)
        if m:
            return m.group(1)
        m = re.search(r"version\s+(\d[\d.]*)", out, re.I)
        if m:
            return m.group(1)
        return "unknown"
    except Exception:
        return None


def _ensure_pdb(structure_path: Path, work_dir: Path) -> Path:
    """
    Ensure structure is in PDB format. FoldX typically expects PDB.
    Converts mmCIF to PDB if needed.
    """
    if structure_path.suffix.lower() == ".pdb":
        return structure_path
    # Convert CIF to PDB
    from Bio.PDB import MMCIFParser, PDBIO

    parser = MMCIFParser(QUIET=True)
    struct = parser.get_structure("s", str(structure_path))
    out_pdb = work_dir / f"{structure_path.stem}.pdb"
    io = PDBIO()
    io.set_structure(struct)
    io.save(str(out_pdb))
    return out_pdb


def run_foldx_buildmodel(
    wt_pdb_path: Path,
    mutation_foldx: str,
    work_dir: Path,
    foldx_executable: str,
) -> tuple[float | None, list[Path]]:
    """
    Run FoldX BuildModel for a single mutation.

    mutation_foldx: format WTaa+Chain+PDBresnum+Mutaa, e.g. RA59W

    Returns (ddg_kcal_mol, list of output file paths for audit).
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    mut_file = work_dir / "individual_list.txt"
    mut_file.write_text(f"{mutation_foldx};\n")

    pdb_name = wt_pdb_path.name
    # FoldX 5: FoldX --command=BuildModel --pdb=... --mutant-file=...
    # pdb-dir must contain the PDB file (work_dir after _ensure_pdb)
    cmd = [
        foldx_executable,
        "--command=BuildModel",
        f"--pdb={pdb_name}",
        f"--mutant-file=individual_list.txt",
        f"--pdb-dir={work_dir}",
        f"--output-dir={work_dir}",
    ]

    try:
        subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=300,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        return (None, [])
    except Exception:
        return (None, [])

    # Parse Dif_*.fxout
    dif_files = list(work_dir.glob("Dif_*_BM.fxout"))
    if not dif_files:
        dif_files = list(work_dir.glob("Dif_*.fxout"))
    ddg = None
    for df in dif_files:
        ddg = _parse_dif_fxout(df)
        if ddg is not None:
            break

    output_paths = list(work_dir.glob("*.fxout")) + [mut_file]
    return (ddg, output_paths)


def _parse_dif_fxout(path: Path) -> float | None:
    """
    Parse FoldX Dif_*.fxout for Total Energy (ddG).
    Format: tab-separated, header row, data rows. Total Energy column.
    """
    try:
        text = path.read_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if len(lines) < 2:
            return None
        headers = lines[0].split("\t")
        # Find Total Energy column (case-insensitive)
        idx = None
        for i, h in enumerate(headers):
            if "total" in h.lower() and "energy" in h.lower():
                idx = i
                break
        if idx is None:
            # Try "DDG" or "ddG"
            for i, h in enumerate(headers):
                if h.strip().upper() in ("DDG", "TOTAL ENERGY"):
                    idx = i
                    break
        if idx is None:
            idx = 1  # Often second column
        # First data row (after header)
        parts = lines[1].split("\t")
        if idx >= len(parts):
            return None
        return float(parts[idx])
    except Exception:
        return None


def compute_foldx_ddg(
    struct_pair: StructurePair,
    pos: int | None,
    variant_parsed: str,
    config: Config,
    cache_dir: Path | None = None,
) -> tuple[StabilityResult, str | None, list[Path]]:
    """
    Compute ΔΔG via FoldX. Uses WT structure (3NKS) and applies mutation.

    Returns (StabilityResult, foldx_version, intermediates_paths).
    """
    foldx_exe = detect_foldx()
    if not foldx_exe:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="not_available"),
            None,
            [],
        )

    version = get_foldx_version(foldx_exe)
    if pos is None:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="mock"),
            version,
            [],
        )

    wt_path = Path(struct_pair.wt_pdb_path)
    if not wt_path.exists():
        return (
            StabilityResult(ddg=0.0, flags=[], backend="mock"),
            version,
            [],
        )

    from psge.backends.sequence import fetch_canonical_sequence

    uniprot_seq = fetch_canonical_sequence(config.gene)
    info = get_pdb_residue_for_foldx(pos, wt_path, uniprot_seq)
    if not info:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="mock"),
            version,
            [],
        )

    chain_id, pdb_resnum, wt_aa = info
    m = re.match(r"^([A-Z])(\d+)([A-Z])$", variant_parsed.strip(), re.I)
    if not m:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="mock"),
            version,
            [],
        )
    _, _, mut_aa = m.groups()
    mut_aa = mut_aa.upper()
    wt_aa = wt_aa.upper()
    mutation_foldx = f"{wt_aa}{chain_id}{pdb_resnum}{mut_aa}"

    base_cache = cache_dir or Path(__file__).parent.parent.parent.parent / "data" / "public" / "structures" / "cache"
    cache_key = hashlib.sha256(
        f"{wt_path}:{mutation_foldx}:{version}".encode()
    ).hexdigest()[:16]
    work_dir = base_cache / "foldx" / cache_key

    wt_pdb = _ensure_pdb(wt_path, work_dir)
    if not wt_pdb.exists():
        return (
            StabilityResult(ddg=0.0, flags=[], backend="mock"),
            version,
            [],
        )

    ddg, intermediates = run_foldx_buildmodel(
        wt_pdb, mutation_foldx, work_dir, foldx_exe
    )

    if ddg is None:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="mock"),
            version,
            intermediates,
        )

    flags = ["destabilizing"] if ddg >= 2.0 else []
    return (
        StabilityResult(ddg=ddg, flags=flags, backend="foldx", foldx_version=version),
        version,
        intermediates,
    )
