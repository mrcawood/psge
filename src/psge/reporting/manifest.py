"""Run manifest emission (PRD §9)."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def emit_run_manifest(
    results_dir: Path,
    variant: str,
    config_hash: str,
    backend_status: dict | None = None,
    mechanism_thresholds: dict | None = None,
) -> Path:
    """Emit run_manifest.json with timestamp, input, config hash, backend_status, thresholds."""
    from psge.utils.backend_status import get_backend_status

    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    input_hash = hashlib.sha256(variant.encode()).hexdigest()
    manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": variant,
        "input_hash": input_hash,
        "config_hash": config_hash,
        "compute_profile": "local",
        "backend_status": backend_status or get_backend_status(),
    }
    if mechanism_thresholds:
        manifest["mechanism_thresholds"] = mechanism_thresholds
    path = results_dir / "run_manifest.json"
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    return path
