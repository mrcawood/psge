"""Load knowledge/ppox domain config."""

from pathlib import Path

import yaml


def load_ppox_sites() -> dict:
    """Load PPOX sites.yaml from knowledge/ppox."""
    path = Path(__file__).parent.parent / "knowledge" / "ppox" / "sites.yaml"
    if not path.exists():
        return _default_sites()
    with open(path) as f:
        return yaml.safe_load(f) or _default_sites()


def _default_sites() -> dict:
    return {
        "fad_residues": list(range(50, 63)),
        "active_site_residues": list(range(55, 66)),
        "n_terminal_targeting_signal_end": 28,
        "n_terminal_targeting_minimal_end": 17,
        "membrane_region_start": None,
        "membrane_region_end": None,
    }
