"""T2 assertions: panel mechanism classes match 04_VARIANT_PANEL (Sprint 6, M6a)."""

import json
from pathlib import Path

from psge.core.models import Config
from psge.pipeline.runner import _sanitize_variant, run
from psge.utils.panel import load_panel

PROJECT_ROOT = Path(__file__).parent.parent
PANEL_PATH = PROJECT_ROOT / "data" / "testdata" / "variants" / "ppox_panel.yaml"

# Expected mechanism classes per docs/PHASE1_5_REMAP.md (predict_first mode)
EXPECTED = {
    "R59W": "cofactor_binding_perturbation",  # is_in_fad_residue_set fallback (pos 59 in FAD set)
    "R152C": "folding_stability_hydrophobic_core",
    "G358R": "folding_stability_hydrophobic_core",
    "I12T": "unknown_mechanism",  # targeting region excludes cofactor fallback; folding_stability needs FoldX
    "78insC": "truncation_misexpression",
    "IVS2-2 a→c": "truncation_misexpression",
}


def test_panel_t2_assertions(tmp_path):
    """Full panel run: each variant produces expected mechanism class."""
    config = Config(
        results_dir=str(tmp_path / "results"),
        cache_dir=str(tmp_path / "cache"),
        structure_source="predict_first",
    )
    panel = load_panel(PANEL_PATH)
    failures = []
    for entry in panel:
        variant = entry["variant"]
        expected = entry.get("expected_class") or EXPECTED.get(variant)
        if not expected:
            continue
        variant_results = tmp_path / "results" / _sanitize_variant(variant)
        variant_config = Config(
            results_dir=str(variant_results),
            gene=config.gene,
            structure_backend=config.structure_backend,
            stability_backend=config.stability_backend,
            cache_dir=config.cache_dir,
            structure_source=config.structure_source,
        )
        run(variant, variant_config)
        summary_path = variant_results / "summary.json"
        assert summary_path.exists(), f"No summary for {variant}"
        with open(summary_path) as f:
            summary = json.load(f)
        actual = summary.get("mechanism_class")
        if actual != expected:
            failures.append((variant, expected, actual))
    assert not failures, f"T2 failures: {failures}"
