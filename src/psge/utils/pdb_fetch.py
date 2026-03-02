"""RCSB PDB fetch and cache (Phase 1.5)."""

from pathlib import Path

RCSB_DOWNLOAD_URL = "https://files.rcsb.org/download/{pdb_id}.cif"
PPOX_WT_PDB_ID = "3NKS"  # Human PPOX, 1.9 Å, FAD + acifluorfen (ACJ)


def get_pdb_path(pdb_id: str, cache_base: Path) -> Path:
    """
    Return path to PDB file. Download from RCSB if not cached.
    Uses mmCIF format (standard RCSB download).
    """
    cache_base = Path(cache_base)
    cache_base.mkdir(parents=True, exist_ok=True)
    out_path = cache_base / f"{pdb_id}.cif"
    if out_path.exists():
        return out_path
    _download_pdb(pdb_id, out_path)
    return out_path


def _download_pdb(pdb_id: str, out_path: Path) -> None:
    """Download PDB mmCIF from RCSB."""
    import urllib.request

    url = RCSB_DOWNLOAD_URL.format(pdb_id=pdb_id.upper())
    req = urllib.request.Request(url, headers={"User-Agent": "PSGE/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        out_path.write_bytes(resp.read())
