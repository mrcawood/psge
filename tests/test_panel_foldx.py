"""pdb_first + FoldX panel expectations (Phase 1.6d)."""

import json
from pathlib import Path

import pytest
import yaml

from psge.backends.foldx.runner import detect_foldx
from psge.core.models import Config
from psge.pipeline.runner import _sanitize_variant, run
from psge.utils.config import load_config

PROJECT_ROOT = Path(__file__).parent.parent
PANEL_PATH = PROJECT_ROOT / "data" / "testdata" / "variants" / "ppox_panel.yaml"
EXPECTED_PATH = (
    PROJECT_ROOT / "data" / "testdata" / "variants" / "ppox_panel_expected_pdb_first_foldx.yaml"
)


@pytest.mark.skipif(not detect_foldx(load_config().foldx_path), reason="FoldX not installed")
def test_panel_pdb_first_foldx_expectations(tmp_path):
    """Panel with pdb_first and real FoldX matches Phase 1.6d expectations."""
    with open(EXPECTED_PATH) as f:
        expected_rows = yaml.safe_load(f)

    config = load_config(
        overrides={
            "results_dir": str(tmp_path / "results"),
            "cache_dir": str(tmp_path / "cache"),
            "structure_source": "pdb_first",
        }
    )
    failures = []
    for row in expected_rows:
        variant = row["variant"]
        variant_results = tmp_path / "results" / _sanitize_variant(variant)
        variant_config = Config(
            results_dir=str(variant_results),
            gene=config.gene,
            structure_backend=config.structure_backend,
            stability_backend=config.stability_backend,
            cache_dir=config.cache_dir,
            structure_source="pdb_first",
            foldx_path=config.foldx_path,
        )
        run(variant, variant_config)
        with open(variant_results / "summary.json") as f:
            summary = json.load(f)

        if row.get("foldx_skipped"):
            assert summary["backend_status"]["stability_backend"] in ("mock", "not_available")
            continue

        assert summary["backend_status"]["stability_backend"] == "foldx"
        if row.get("expected_primary"):
            if summary.get("mechanism_class") != row["expected_primary"]:
                failures.append((variant, "primary", row["expected_primary"], summary.get("mechanism_class")))
        if row.get("expected_stability_signal_band"):
            band = summary.get("stability_signal_band")
            if band != row["expected_stability_signal_band"]:
                failures.append((variant, "band", row["expected_stability_signal_band"], band))
        for sec in row.get("expected_secondary_includes") or []:
            if sec not in summary.get("secondary_hypotheses", []):
                failures.append((variant, "secondary", sec, summary.get("secondary_hypotheses")))
        if row.get("audit_required"):
            prov = summary.get("foldx_provenance") or {}
            if not prov.get("audit_passed"):
                failures.append((variant, "audit", True, prov.get("audit_passed")))

    assert not failures, f"pdb_first FoldX panel failures: {failures}"
