"""Config loader."""

from pathlib import Path

import yaml

from psge.core.models import Config


def load_config(config_path: Path | None = None, overrides: dict | None = None) -> Config:
    """Load config from default or path, merge CLI overrides."""
    if config_path is None:
        # Project root: src/psge/utils/config.py -> psge/
        root = Path(__file__).parent.parent.parent.parent
        config_path = root / "configs" / "default.yaml"
    data = {}
    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
    if overrides:
        data = {**data, **overrides}
    return Config(
        results_dir=data.get("results_dir", "results"),
        gene=data.get("gene", "PPOX"),
        structure_backend=data.get("structure_backend", "alphafold"),
        stability_backend=data.get("stability_backend", "foldx"),
        cache_dir=data.get("cache_dir"),
        structure_source=data.get("structure_source", "pdb_first"),
    )
