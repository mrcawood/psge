"""Evidence source registry (Phase 1.6e)."""

from psge.sources.loader import (
    get_source,
    get_variant_evidence,
    load_source_registry,
    load_variant_evidence_map,
    validate_registry,
    validate_variant_map,
)

__all__ = [
    "get_source",
    "get_variant_evidence",
    "load_source_registry",
    "load_variant_evidence_map",
    "validate_registry",
    "validate_variant_map",
]
