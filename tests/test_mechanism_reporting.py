"""Mechanism classifier and reporting tests (Sprint 5, 09_PLAN.md)."""

import json
from pathlib import Path

from psge.core.models import Config
from psge.pipeline.stages import (
    alignment_delta,
    context_mapping,
    mechanism_classifier,
    preflight,
    reporting,
    sequence,
    stability,
    structure,
)


def test_mechanism_output_structure(tmp_path):
    """MechanismHypothesis has class, confidence, evidence_table, limits."""
    config = Config(
        results_dir=str(tmp_path / "results"),
        cache_dir=str(tmp_path / "cache"),
        structure_source="predict_first",
    )
    rec = preflight("R59W", config)
    seq = sequence(rec, config)
    struct = structure(rec, seq, config)
    delta = alignment_delta(rec, struct, config)
    stab = stability(rec, struct, config)
    ctx = context_mapping(rec, struct, config)

    hypothesis = mechanism_classifier(rec, delta, stab, ctx, config)
    assert hypothesis is not None
    assert hasattr(hypothesis, "class_")
    assert hasattr(hypothesis, "confidence")
    assert hasattr(hypothesis, "evidence_table")
    assert hasattr(hypothesis, "interpretation")
    assert hasattr(hypothesis, "limits")
    assert hasattr(hypothesis, "decision_trace")
    assert isinstance(hypothesis.decision_trace, list)
    assert hypothesis.class_ in (
        "cofactor_binding_perturbation",
        "active_site_region_perturbation",
        "folding_stability_hydrophobic_core",
        "targeting_signal_perturbation",
        "truncation_misexpression",
        "unknown_mechanism",
    )


def test_mechanism_r59w_cofactor_or_unknown(tmp_path):
    """R59W → cofactor_binding_perturbation with pdb_first, or unknown with predict_first."""
    config = Config(
        results_dir=str(tmp_path / "results"),
        cache_dir=str(tmp_path / "cache"),
        structure_source="predict_first",
    )
    rec = preflight("R59W", config)
    seq = sequence(rec, config)
    struct = structure(rec, seq, config)
    delta = alignment_delta(rec, struct, config)
    stab = stability(rec, struct, config)
    ctx = context_mapping(rec, struct, config)

    hypothesis = mechanism_classifier(rec, delta, stab, ctx, config)
    assert hypothesis.class_ in ("cofactor_binding_perturbation", "unknown_mechanism")


def test_mechanism_truncation_for_non_structural():
    """78insC → truncation_misexpression (non-structural track)."""
    config = Config(results_dir="/tmp")
    rec = preflight("78insC", config)
    hypothesis = mechanism_classifier(rec, None, None, None, config)
    assert hypothesis.class_ == "truncation_misexpression"


def test_mechanism_i12t_targeting_secondary(tmp_path):
    """I12T → targeting_signal_perturbation as secondary (Phase 1.5)."""
    config = Config(
        results_dir=str(tmp_path / "results"),
        cache_dir=str(tmp_path / "cache"),
        structure_source="predict_first",
    )
    rec = preflight("I12T", config)
    seq = sequence(rec, config)
    struct = structure(rec, seq, config)
    delta = alignment_delta(rec, struct, config)
    stab = stability(rec, struct, config)
    ctx = context_mapping(rec, struct, config)

    hypothesis = mechanism_classifier(rec, delta, stab, ctx, config)
    # Primary: folding_stability (if mock destab) or unknown; secondary: targeting_signal_perturbation
    assert "targeting_signal_perturbation" in hypothesis.secondary_hypotheses


def test_reporting_emits_summary_and_report(tmp_path):
    """Reporting emits summary.json and report.md with required fields."""
    config = Config(
        results_dir=str(tmp_path / "results"),
        cache_dir=str(tmp_path / "cache"),
        structure_source="predict_first",
    )
    rec = preflight("R59W", config)
    seq = sequence(rec, config)
    struct = structure(rec, seq, config)
    delta = alignment_delta(rec, struct, config)
    stab = stability(rec, struct, config)
    ctx = context_mapping(rec, struct, config)
    hypothesis = mechanism_classifier(rec, delta, stab, ctx, config)

    reporting(rec, hypothesis, config, skipped_steps=[])

    summary_path = Path(config.results_dir) / "summary.json"
    report_path = Path(config.results_dir) / "report.md"
    assert summary_path.exists()
    assert report_path.exists()

    with open(summary_path) as f:
        summary = json.load(f)
    assert "mechanism_class" in summary
    assert "input" in summary or "variant" in summary
    assert "limits" in summary or "mechanism" in summary
