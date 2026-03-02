"""CLI tests (Sprint 1, 09_PLAN.md)."""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SRC = PROJECT_ROOT / "src"


def test_cli_run_variant_exits_zero(tmp_path):
    """CLI accepts --variant R59W and exits 0; pipeline invoked."""
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    result = subprocess.run(
        [sys.executable, "-m", "psge.cli", "run", "--variant", "R59W", "--results-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=env,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_run_manifest_emitted(tmp_path):
    """run_manifest.json emitted with input_hash, timestamp, backend_status (M6a)."""
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    result = subprocess.run(
        [sys.executable, "-m", "psge.cli", "run", "--variant", "R59W", "--results-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=env,
    )
    assert result.returncode == 0
    manifest_path = tmp_path / "run_manifest.json"
    assert manifest_path.exists(), f"run_manifest.json not found in {tmp_path}"
    with open(manifest_path) as f:
        manifest = json.load(f)
    assert "input_hash" in manifest or "input" in manifest
    assert "timestamp" in manifest
    assert "backend_status" in manifest
    assert "structure_backend" in manifest["backend_status"]
