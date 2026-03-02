"""Panel loader and runner tests (Sprint 2, 09_PLAN.md)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from psge.utils.panel import load_panel

PROJECT_ROOT = Path(__file__).parent.parent
SRC = PROJECT_ROOT / "src"


def test_panel_load():
    """Load panel YAML, get variant list with expected_class."""
    panel_path = Path(__file__).parent.parent / "data" / "testdata" / "variants" / "ppox_panel.yaml"
    panel = load_panel(panel_path)
    assert len(panel) >= 6  # All panel variants
    variants = {e["variant"]: e["expected_class"] for e in panel}
    assert variants.get("R59W") in ("unknown_mechanism", "cofactor_binding_perturbation")
    assert variants.get("78insC") == "truncation_misexpression"
    assert variants.get("IVS2-2 a→c") == "truncation_misexpression"
    assert variants.get("I12T") in ("unknown_mechanism", "folding_stability_hydrophobic_core")


def test_cli_run_panel(tmp_path):
    """CLI --panel runs all variants, creates per-variant result dirs."""
    panel = PROJECT_ROOT / "data" / "testdata" / "variants" / "ppox_panel.yaml"
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    result = subprocess.run(
        [sys.executable, "-m", "psge.cli", "run", "--panel", str(panel), "--results-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "R59W" / "run_manifest.json").exists()
    assert (tmp_path / "78insC" / "run_manifest.json").exists()
