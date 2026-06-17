"""FoldX runner for ΔΔG stability (Phase 1.6b/1.6c)."""

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
    Ensure structure is in PDB format inside work_dir. FoldX expects PDB in pdb-dir.
    Converts mmCIF to PDB if needed.
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    if structure_path.suffix.lower() == ".pdb":
        out_pdb = work_dir / structure_path.name
        if structure_path.resolve() != out_pdb.resolve():
            shutil.copy2(structure_path, out_pdb)
        return out_pdb

    from Bio.PDB import MMCIFParser, PDBIO

    parser = MMCIFParser(QUIET=True)
    struct = parser.get_structure("s", str(structure_path))
    out_pdb = work_dir / f"{structure_path.stem}.pdb"
    io = PDBIO()
    io.set_structure(struct)
    io.save(str(out_pdb))
    return out_pdb


def run_foldx_repair(
    pdb_path: Path,
    work_dir: Path,
    foldx_executable: str,
    timeout: int = 600,
) -> Path | None:
    """
    Run FoldX RepairPDB. Returns path to repaired PDB or None on failure.
    Skips repair when output already exists in work_dir.
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    pdb_name = pdb_path.name
    repaired_name = f"{pdb_path.stem}_Repair.pdb"
    repaired_path = work_dir / repaired_name
    if repaired_path.exists():
        return repaired_path

    cmd = [
        foldx_executable,
        "--command=RepairPDB",
        f"--pdb={pdb_name}",
        f"--pdb-dir={work_dir}",
        f"--output-dir={work_dir}",
    ]
    try:
        subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None

    return repaired_path if repaired_path.exists() else None


def run_foldx_buildmodel(
    wt_pdb_path: Path,
    mutation_foldx: str,
    work_dir: Path,
    foldx_executable: str,
) -> tuple[float | None, list[Path], str | None]:
    """
    Run FoldX BuildModel for a single mutation.

    mutation_foldx: format WTaa+Chain+PDBresnum+Mutaa, e.g. RA59W

    Returns (ddg_kcal_mol, output paths for audit, error message if any).
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    mut_file = work_dir / "individual_list.txt"
    mut_file.write_text(f"{mutation_foldx};\n")

    pdb_name = wt_pdb_path.name
    cmd = [
        foldx_executable,
        "--command=BuildModel",
        f"--pdb={pdb_name}",
        "--mutant-file=individual_list.txt",
        f"--pdb-dir={work_dir}",
        f"--output-dir={work_dir}",
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=300,
            check=True,
        )
        _ = result
    except subprocess.CalledProcessError as e:
        err = (e.stderr or e.stdout or str(e))[:500]
        return (None, [mut_file], err)
    except subprocess.TimeoutExpired:
        return (None, [mut_file], "FoldX BuildModel timed out")
    except OSError as e:
        return (None, [mut_file], str(e))

    dif_files = list(work_dir.glob("Dif_*_BM.fxout"))
    if not dif_files:
        dif_files = list(work_dir.glob("Dif_*.fxout"))
    ddg = None
    for df in dif_files:
        ddg = _parse_dif_fxout(df)
        if ddg is not None:
            break

    output_paths = list(work_dir.glob("*.fxout")) + [mut_file]
    if ddg is None:
        return (None, output_paths, "Could not parse FoldX Dif output")
    return (ddg, output_paths, None)


def _parse_dif_fxout(path: Path) -> float | None:
    """
    Parse FoldX Dif_*.fxout for Total Energy (ddG).
    Handles banner lines before the tab-separated header (FoldX 5.x).
    """
    try:
        text = path.read_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        header_idx = None
        for i, line in enumerate(lines):
            if "\t" not in line:
                continue
            lower = line.lower()
            if "total" in lower and "energy" in lower:
                header_idx = i
                break
        if header_idx is None or header_idx + 1 >= len(lines):
            return None
        headers = lines[header_idx].split("\t")
        idx = None
        for i, h in enumerate(headers):
            hl = h.strip().lower()
            if hl in ("ddg", "total energy") or ("total" in hl and "energy" in hl):
                idx = i
                break
        if idx is None:
            idx = 1
        parts = lines[header_idx + 1].split("\t")
        if idx >= len(parts):
            return None
        return float(parts[idx])
    except Exception:
        return None


def _cache_base(cache_dir: Path | str | None) -> Path:
    if cache_dir:
        return Path(cache_dir)
    return Path(__file__).resolve().parents[4] / "data" / "public" / "structures" / "cache"


def compute_foldx_ddg(
    struct_pair: StructurePair,
    pos: int | None,
    variant_parsed: str,
    config: Config,
    cache_dir: Path | str | None = None,
) -> tuple[StabilityResult, str | None, list[Path]]:
    """
    Compute ΔΔG via FoldX. Uses WT structure (3NKS) and applies mutation.

    Returns (StabilityResult, foldx_version, intermediates_paths).
    """
    foldx_exe = detect_foldx(getattr(config, "foldx_path", None))
    if not foldx_exe:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="not_available"),
            None,
            [],
        )

    version = get_foldx_version(foldx_exe)
    if pos is None:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="foldx_failed", foldx_version=version),
            version,
            [],
        )

    wt_path = Path(struct_pair.wt_pdb_path)
    if not wt_path.exists():
        return (
            StabilityResult(ddg=0.0, flags=[], backend="foldx_failed", foldx_version=version),
            version,
            [],
        )

    from psge.backends.sequence import fetch_canonical_sequence

    uniprot_seq = fetch_canonical_sequence(config.gene)
    info = get_pdb_residue_for_foldx(pos, wt_path, uniprot_seq)
    if not info:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="foldx_failed", foldx_version=version),
            version,
            [],
        )

    chain_id, pdb_resnum, wt_aa = info
    m = re.match(r"^([A-Z])(\d+)([A-Z])$", variant_parsed.strip(), re.I)
    if not m:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="foldx_failed", foldx_version=version),
            version,
            [],
        )
    _, _, mut_aa = m.groups()
    mut_aa = mut_aa.upper()
    wt_aa = wt_aa.upper()
    mutation_foldx = f"{wt_aa}{chain_id}{pdb_resnum}{mut_aa}"

    base_cache = _cache_base(cache_dir)
    wt_hash = hashlib.sha256(str(wt_path.resolve()).encode()).hexdigest()[:16]
    repair_dir = base_cache / "foldx" / "repair" / wt_hash
    repair_dir.mkdir(parents=True, exist_ok=True)
    wt_pdb = _ensure_pdb(wt_path, repair_dir)

    repaired_pdb = run_foldx_repair(wt_pdb, repair_dir, foldx_exe)
    if not repaired_pdb:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="foldx_failed", foldx_version=version),
            version,
            list(repair_dir.glob("*.pdb")),
        )

    cache_key = hashlib.sha256(
        f"{wt_path}:{mutation_foldx}:{version}".encode()
    ).hexdigest()[:16]
    work_dir = base_cache / "foldx" / cache_key
    work_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repaired_pdb, work_dir / repaired_pdb.name)
    build_pdb = work_dir / repaired_pdb.name

    ddg, intermediates, err = run_foldx_buildmodel(
        build_pdb, mutation_foldx, work_dir, foldx_exe
    )

    if ddg is None:
        return (
            StabilityResult(ddg=0.0, flags=[], backend="foldx_failed", foldx_version=version),
            version,
            intermediates,
        )

    flags = ["destabilizing"] if ddg >= 2.0 else []
    return (
        StabilityResult(ddg=ddg, flags=flags, backend="foldx", foldx_version=version),
        version,
        intermediates,
    )
