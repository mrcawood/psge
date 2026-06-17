"""Pipeline orchestrator."""

from pathlib import Path

from psge.core.models import Config, VariantRecord
from psge.pipeline import stages
from psge.reporting.manifest import emit_run_manifest


def run(variant: str, config: Config) -> VariantRecord:
    """Run pipeline: stages in order, emit manifest."""
    variant_record = stages.preflight(variant, config)
    sequence_pair = stages.sequence(variant_record, config)
    structure_pair = stages.structure(variant_record, sequence_pair, config)
    delta = stages.alignment_delta(variant_record, structure_pair, config)
    stability_result = stages.stability(variant_record, structure_pair, config)
    context = stages.context_mapping(variant_record, structure_pair, config)
    from psge.utils.backend_status import get_backend_status
    struct_backend = structure_pair.backend if structure_pair else "mock"
    stab_backend = stability_result.backend if stability_result else "mock"
    sasa_backend = (
        "biopython_shrake_rupley"
        if delta
        and (
            getattr(delta, "sasa_residue_wt", None)
            or getattr(delta, "sasa_patch_8A", None) is not None
        )
        else "not_implemented"
    )
    foldx_ver = getattr(stability_result, "foldx_version", None) if stability_result else None
    backend_status = get_backend_status(
        structure_backend=struct_backend,
        stability_backend=stab_backend,
        sasa=sasa_backend,
        foldx_version=foldx_ver,
    )
    hypothesis = stages.mechanism_classifier(
        variant_record, delta, stability_result, context, config, backend_status
    )
    skipped = _skipped_steps(variant_record, structure_pair)
    stages.reporting(variant_record, hypothesis, config, skipped, backend_status, delta, stability_result)

    config_hash = _config_hash(config)
    results_path = Path(config.results_dir).resolve()
    from psge.pipeline.mechanism import CONTACT_ANGSTROM, NEAR_ANGSTROM
    mechanism_thresholds = {
        "contact_threshold_angstrom": CONTACT_ANGSTROM,
        "near_threshold_angstrom": NEAR_ANGSTROM,
    }
    emit_run_manifest(results_path, variant, config_hash, backend_status, mechanism_thresholds)

    return variant_record


def run_panel(panel_path: Path, config: Config) -> list[VariantRecord]:
    """Run pipeline for each variant in panel."""
    from psge.utils.panel import load_panel

    panel = load_panel(panel_path)
    records = []
    base_results = Path(config.results_dir)
    for entry in panel:
        variant = entry["variant"]
        variant_results = base_results / _sanitize_variant(variant)
        variant_config = Config(
            results_dir=str(variant_results),
            gene=config.gene,
            structure_backend=config.structure_backend,
            stability_backend=config.stability_backend,
            cache_dir=config.cache_dir,
            structure_source=getattr(config, "structure_source", "predict_first"),
            foldx_path=config.foldx_path,
        )
        rec = run(variant, variant_config)
        records.append(rec)
    return records


def _sanitize_variant(variant: str) -> str:
    """Safe dir name for variant string."""
    return variant.replace(" ", "_").replace("→", "to").replace("/", "_")


def _skipped_steps(variant_record, structure_pair) -> list[str]:
    """Build skipped-steps list for reporting."""
    skipped = []
    if variant_record.track == "non_structural":
        skipped.append("Structure, alignment, stability, context: variant is truncation/splice")
    return skipped


def _config_hash(config: Config) -> str:
    """Simple config hash for manifest."""
    import hashlib
    src = getattr(config, "structure_source", "predict_first")
    s = f"{config.gene}:{config.structure_backend}:{config.stability_backend}:{src}"
    return hashlib.sha256(s.encode()).hexdigest()
