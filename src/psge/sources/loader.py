"""Load and validate PPOX evidence source registry (Phase 1.6e)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ALLOWED_SOURCE_TYPES = {
    "pdb_structure",
    "computational_prediction",
    "literature",
    "functional_assay",
    "database",
    "internal_report",
}

ALLOWED_EVIDENCE_TIERS = {
    "not_applicable",
    "variant_class_rule",
    "pdb_context_only",
    "foldx_stability_prediction",
    "literature_mechanistic",
    "functional_assay",
    "replicated_multi_source",
}

ALLOWED_VERIFICATION_STATUSES = {
    "bibliography_verified",
    "primary_text_verified",
    "pending_primary_verification",
}

ALLOWED_CLAIM_SCOPES = {
    "direct_variant_evidence",
    "structural_context",
    "mechanistic_inference",
    "computational_prediction",
    "background_context",
    "unsupported_or_speculative",
}

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCES_DIR = PROJECT_ROOT / "data" / "sources"
SOURCES_FILE = SOURCES_DIR / "ppox_sources.yaml"
VARIANT_EVIDENCE_FILE = SOURCES_DIR / "ppox_variant_evidence.yaml"


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing evidence file: {path}")
    with open(path) as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def load_source_registry(path: Path | None = None) -> dict[str, dict]:
    data = _load_yaml(path or SOURCES_FILE)
    registry = {s["source_id"]: s for s in data.get("sources", [])}
    validate_registry(registry)
    return registry


@lru_cache(maxsize=1)
def load_variant_evidence_map(path: Path | None = None) -> dict[str, dict]:
    data = _load_yaml(path or VARIANT_EVIDENCE_FILE)
    variants = data.get("variants", {})
    validate_variant_map(variants, load_source_registry())
    return variants


def validate_registry(registry: dict[str, dict]) -> None:
    if not registry:
        raise ValueError("Source registry is empty")
    ids = list(registry.keys())
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate source_id in registry")
    for sid, src in registry.items():
        if src.get("source_id") != sid:
            raise ValueError(f"source_id mismatch for {sid}")
        st = src.get("source_type")
        if st not in ALLOWED_SOURCE_TYPES:
            raise ValueError(f"Invalid source_type for {sid}: {st}")
        et = src.get("evidence_tier")
        if et not in ALLOWED_EVIDENCE_TIERS:
            raise ValueError(f"Invalid evidence_tier for {sid}: {et}")
        cs = src.get("claim_scope")
        if cs is not None and cs not in ALLOWED_CLAIM_SCOPES:
            raise ValueError(f"Invalid claim_scope for {sid}: {cs}")
        vs = src.get("verification_status")
        if vs is not None and vs not in ALLOWED_VERIFICATION_STATUSES:
            raise ValueError(f"Invalid verification_status for {sid}: {vs}")


def validate_variant_map(variants: dict[str, dict], registry: dict[str, dict]) -> None:
    for variant, entry in variants.items():
        for sid in entry.get("psge_computed_evidence", []):
            if sid not in registry:
                raise ValueError(f"{variant}: unknown psge_computed source {sid}")
        for ext in entry.get("external_evidence", []):
            ref = ext.get("source_id")
            if ref not in registry:
                raise ValueError(f"{variant}: unknown external source {ref}")
            cs = ext.get("claim_scope")
            if cs and cs not in ALLOWED_CLAIM_SCOPES:
                raise ValueError(f"{variant}: invalid claim_scope {cs}")
            et = ext.get("evidence_tier")
            if et and et not in ALLOWED_EVIDENCE_TIERS:
                raise ValueError(f"{variant}: invalid evidence_tier {et}")
        het = entry.get("highest_evidence_tier")
        if het and het not in ALLOWED_EVIDENCE_TIERS:
            raise ValueError(f"{variant}: invalid highest_evidence_tier {het}")


def get_source(source_id: str) -> dict | None:
    return load_source_registry().get(source_id)


def get_variant_evidence(variant: str) -> dict[str, Any]:
    return load_variant_evidence_map().get(variant, {
        "psge_computed_evidence": [],
        "external_evidence": [],
        "evidence_gap": ["No variant evidence map entry."],
    })


def highest_tier_for_variant(variant: str, backend_status: dict | None) -> str:
    """Highest evidence tier from variant map override, computed, and external sources."""
    ve = get_variant_evidence(variant)
    if ve.get("highest_evidence_tier"):
        return ve["highest_evidence_tier"]

    rank = [
        "not_applicable",
        "variant_class_rule",
        "pdb_context_only",
        "foldx_stability_prediction",
        "literature_mechanistic",
        "functional_assay",
        "replicated_multi_source",
    ]
    tiers: set[str] = set()
    registry = load_source_registry()
    for sid in ve.get("psge_computed_evidence", []):
        tiers.add(registry[sid]["evidence_tier"])
    for ext in ve.get("external_evidence", []):
        tiers.add(ext.get("evidence_tier") or registry[ext["source_id"]]["evidence_tier"])
    if not tiers:
        return "not_applicable"
    return max(tiers, key=lambda t: rank.index(t))
