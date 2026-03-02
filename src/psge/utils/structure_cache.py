"""Structure cache (PRD §9, 09_PLAN)."""

import hashlib
from pathlib import Path

from psge.core.models import Config, SequencePair, StructurePair


def get_cache_dir(config: Config, variant: str) -> Path:
    """Resolve cache directory. Key includes variant, config, backend."""
    if config.cache_dir:
        base = Path(config.cache_dir)
    else:
        # Default: project data/public/structures/cache
        base = Path(__file__).parent.parent.parent.parent / "data" / "public" / "structures" / "cache"
    key = _cache_key(variant, config)
    return base / key


def _cache_key(variant: str, config: Config) -> str:
    """Cache key: variant + config hash + backend + structure_source."""
    cfg = f"{config.gene}:{config.structure_backend}:{getattr(config, 'structure_source', 'predict_first')}"
    h = hashlib.sha256(f"{variant}:{cfg}".encode()).hexdigest()
    return h[:16]


def get_or_compute_structure(
    variant: str,
    seq_pair: SequencePair,
    config: Config,
    predict_fn,
) -> StructurePair:
    """
    Get StructurePair from cache or compute and store.
    """
    cache_dir = get_cache_dir(config, variant)
    manifest_path = cache_dir / "manifest.json"
    if manifest_path.exists():
        import json
        with open(manifest_path) as f:
            d = json.load(f)
        return StructurePair(
            wt_pdb_path=d["wt_pdb_path"],
            mutant_pdb_path=d["mutant_pdb_path"],
            backend=d["backend"],
        )
    pair = predict_fn(seq_pair, config, cache_dir)
    _write_cache_manifest(cache_dir, pair)
    return pair


def _write_cache_manifest(cache_dir: Path, pair: StructurePair) -> None:
    import json
    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(cache_dir / "manifest.json", "w") as f:
        json.dump({
            "wt_pdb_path": pair.wt_pdb_path,
            "mutant_pdb_path": pair.mutant_pdb_path,
            "backend": pair.backend,
        }, f, indent=2)
