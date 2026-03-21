"""Pipeline stages."""

from pathlib import Path

from psge.core.models import (
    Config,
    ContextFeatures,
    DeltaFeatures,
    MechanismHypothesis,
    SequencePair,
    StabilityResult,
    StructurePair,
    VariantRecord,
)
from psge.utils.variant_parse import classify_variant


def preflight(variant: str, config: Config) -> VariantRecord:
    """Preflight: parse variant, classify type, route (PRD FR1)."""
    vtype, track = classify_variant(variant)
    return VariantRecord(
        raw=variant,
        parsed=variant.strip(),
        type=vtype,
        track=track,
    )


def sequence(variant_record: VariantRecord, config: Config) -> SequencePair | None:
    """Sequence: WT + mutant for missense. Skips for non-structural (PRD FR2)."""
    if variant_record.track != "structural":
        return None
    from psge.backends.sequence import apply_missense_variant, fetch_canonical_sequence

    wt = fetch_canonical_sequence(config.gene)
    mutant = apply_missense_variant(wt, variant_record.parsed)
    return SequencePair(wt_sequence=wt, mutant_sequence=mutant)


def structure(
    variant_record: VariantRecord,
    sequence_pair: SequencePair | None,
    config: Config,
) -> StructurePair | None:
    """Structure: PDB-first or predict. Uses cache. Skips if no sequence (PRD FR3)."""
    if sequence_pair is None:
        return None
    from psge.utils.structure_cache import get_or_compute_structure

    src = getattr(config, "structure_source", "predict_first")
    if src == "pdb_first":
        from psge.backends.structure_pdb import pdb_first_structure
        backend_fn = lambda sp, cfg, cd: pdb_first_structure(sp, cfg, cd)
    else:
        from psge.backends.structure import get_structure_backend
        backend = get_structure_backend(config.structure_backend)
        backend_fn = lambda sp, cfg, cd: backend(sp, cfg, cd)

    return get_or_compute_structure(
        variant_record.parsed,
        sequence_pair,
        config,
        backend_fn,
    )


def alignment_delta(
    variant_record: VariantRecord,
    structure_pair: StructurePair | None,
    config: Config,
) -> DeltaFeatures | None:
    """Alignment + delta features (PRD FR4). Skips if no structure."""
    if structure_pair is None:
        return None
    from psge.backends.alignment import compute_delta
    return compute_delta(variant_record, structure_pair, config)


def stability(
    variant_record: VariantRecord,
    structure_pair: StructurePair | None,
    config: Config,
) -> StabilityResult | None:
    """Stability: ΔΔG (PRD FR5). Skips if no structure."""
    if structure_pair is None:
        return None
    from psge.backends.stability import get_stability_backend
    backend = get_stability_backend(config.stability_backend)
    from psge.utils.variant_parse import variant_position
    pos = variant_position(variant_record.parsed)
    return backend(structure_pair, pos, config, variant_record.parsed)


def context_mapping(
    variant_record: VariantRecord,
    structure_pair: StructurePair | None,
    config: Config,
) -> ContextFeatures | None:
    """Context mapping (PRD FR6). Skips if no structure."""
    if structure_pair is None:
        return None
    from psge.backends.context import map_context
    return map_context(variant_record, structure_pair, config)


def mechanism_classifier(
    variant_record: VariantRecord,
    delta: DeltaFeatures | None,
    stability_result: StabilityResult | None,
    context: ContextFeatures | None,
    config: Config,
    backend_status: dict | None = None,
) -> MechanismHypothesis:
    """Mechanism classifier (PRD FR7)."""
    from psge.pipeline.mechanism import classify
    return classify(variant_record, delta, stability_result, context, config, backend_status)


def reporting(
    variant_record: VariantRecord,
    hypothesis: MechanismHypothesis,
    config: Config,
    skipped_steps: list[str] | None = None,
    backend_status: dict | None = None,
    delta: DeltaFeatures | None = None,
) -> None:
    """Reporting: summary.json, report.md (PRD §6). Phase 1.6: delta for SASA evidence."""
    from psge.reporting.summary import emit_report, emit_summary
    from psge.utils.backend_status import get_backend_status

    results_dir = Path(config.results_dir)
    skipped = skipped_steps or []
    backend_status = backend_status or get_backend_status()
    emit_summary(
        results_dir,
        variant_record.raw,
        hypothesis,
        variant_record,
        skipped,
        backend_status,
        delta,
    )
    emit_report(
        results_dir,
        variant_record.raw,
        hypothesis,
        skipped,
        backend_status,
        delta,
    )
