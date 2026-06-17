"""Report evidence source integration (Phase 1.6e)."""

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
from psge.reporting.evidence import enrich_evidence_rows, external_evidence_rows


def test_enriched_rows_have_source_ids():
    rows = enrich_evidence_rows(
        [{"signal": "min_dist_to_fad_atoms_angstrom", "value": 4.5}],
        stability_result=None,
        delta=None,
        backend_status={"stability_backend": "foldx"},
    )
    assert any(r.get("source_id") == "PDB_3NKS" for r in rows)


def test_external_rows_for_r59w():
    rows = external_evidence_rows("R59W")
    assert any(r.get("source_id") == "MEISSNER_1996_R59W" for r in rows)
    assert all(r.get("claim_scope") for r in rows)


def test_report_sections(tmp_path):
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

    report = (Path(config.results_dir) / "report.md").read_text()
    for section in (
        "## Evidence basis",
        "## Computed evidence",
        "## External evidence",
        "## Evidence gaps",
        "## Interpretation limits",
    ):
        assert section in report

    summary = json.loads((Path(config.results_dir) / "summary.json").read_text())
    es = summary["evidence_summary"]
    assert "computed_evidence_source_ids" in es
    assert "external_evidence" in es
    assert es.get("highest_evidence_tier") == "functional_assay"


def test_i12t_reports_evidence_gap(tmp_path):
    config = Config(
        results_dir=str(tmp_path / "results_i12t"),
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
    reporting(rec, hypothesis, config, skipped_steps=[])

    summary = json.loads((Path(config.results_dir) / "summary.json").read_text())
    assert summary["evidence_summary"].get("evidence_gaps")
