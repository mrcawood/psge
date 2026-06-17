"""Config loader."""

from pathlib import Path

import yaml

from psge.core.models import Config


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _resolve_foldx_path(path: str | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = _project_root() / p
    return str(p) if p.exists() else None


def load_config(config_path: Path | None = None, overrides: dict | None = None) -> Config:
    """Load config from default or path, merge CLI overrides."""
    if config_path is None:
        config_path = _project_root() / "configs" / "default.yaml"
    data = {}
    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
    if overrides:
        data = {**data, **overrides}
    foldx_path = _resolve_foldx_path(data.get("foldx_path"))
    return Config(
        results_dir=data.get("results_dir", "results"),
        gene=data.get("gene", "PPOX"),
        structure_backend=data.get("structure_backend", "alphafold"),
        stability_backend=data.get("stability_backend", "foldx"),
        cache_dir=data.get("cache_dir"),
        structure_source=data.get("structure_source", "pdb_first"),
        foldx_path=foldx_path,
    )
