"""Source registry validation (Phase 1.6e)."""

import pytest

from psge.sources.loader import (
    ALLOWED_EVIDENCE_TIERS,
    ALLOWED_SOURCE_TYPES,
    load_source_registry,
    validate_registry,
)


def test_source_registry_loads():
    registry = load_source_registry()
    assert "PDB_3NKS" in registry
    assert "FOLDX_5_3NKS" in registry
    assert "SASA_BIOPYTHON_3NKS" in registry


def test_source_ids_unique():
    registry = load_source_registry()
    ids = list(registry.keys())
    assert len(ids) == len(set(ids))


def test_allowed_enums_enforced():
    registry = load_source_registry()
    for src in registry.values():
        assert src["source_type"] in ALLOWED_SOURCE_TYPES
        assert src["evidence_tier"] in ALLOWED_EVIDENCE_TIERS


def test_invalid_source_type_rejected():
    bad = {"BAD": {"source_id": "BAD", "source_type": "nope", "evidence_tier": "pdb_context_only"}}
    with pytest.raises(ValueError, match="source_type"):
        validate_registry(bad)
