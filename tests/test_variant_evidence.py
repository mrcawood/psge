"""Variant evidence map validation (Phase 1.6e)."""

from psge.sources.loader import (
    get_variant_evidence,
    highest_tier_for_variant,
    load_variant_evidence_map,
)


def test_variant_map_loads():
    variants = load_variant_evidence_map()
    assert "R59W" in variants
    assert "I12T" in variants


def test_variant_references_valid_sources():
    variants = load_variant_evidence_map()
    for variant, entry in variants.items():
        for sid in entry.get("psge_computed_evidence", []):
            assert isinstance(sid, str)
        for ext in entry.get("external_evidence", []):
            assert "source_id" in ext


def test_r59w_has_external_evidence():
    ve = get_variant_evidence("R59W")
    assert len(ve.get("external_evidence", [])) >= 1
    ids = {e["source_id"] for e in ve["external_evidence"]}
    assert "MEISSNER_1996_R59W" in ids


def test_i12t_has_evidence_gap():
    ve = get_variant_evidence("I12T")
    assert ve.get("evidence_gap")


def test_highest_tier_r59w():
    tier = highest_tier_for_variant("R59W", None)
    assert tier == "functional_assay"


def test_highest_tier_i12t():
    tier = highest_tier_for_variant("I12T", None)
    assert tier == "foldx_stability_prediction"
