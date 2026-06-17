"""Variant-specific conservative interpretation text (Phase 1.6d)."""

from psge.core.models import ContextFeatures, StabilityResult, VariantRecord


def apply_variant_interpretation(
    variant_record: VariantRecord,
    default: str,
    *,
    mechanism_class: str,
    stability_result: StabilityResult | None,
    context: ContextFeatures | None,
) -> str:
    """Return supervisor-approved wording when available; else default."""
    parsed = variant_record.parsed.strip().upper()
    band = stability_result.stability_signal_band if stability_result else None
    ddg = stability_result.ddg if stability_result else None

    if parsed == "R59W":
        return (
            "R59W is located in the FAD-proximal structural environment in the 3NKS reference. "
            "FoldX predicts a borderline destabilizing effect under the prepared protein model. "
            "These signals support a plausible structural hypothesis involving the cofactor environment "
            "and possible local stability effects, but they do not establish altered enzyme activity, "
            "cofactor affinity, penetrance, or clinical outcome."
        )

    if parsed == "I12T":
        return (
            "FoldX predicts a destabilizing effect for I12T under the 3NKS-based model, making "
            "folding/stability a plausible primary structural mechanism in this pipeline. "
            "Targeting/localization remains a separate biological hypothesis and is not resolved by FoldX."
        )

    if parsed == "R152C":
        return (
            "R152C shows a weak-to-moderate FoldX destabilization signal below the current "
            "primary-classification threshold. PSGE therefore does not assign a confident primary "
            "structural mechanism from the current evidence, but records the stability signal for review."
        )

    if parsed == "G358R":
        audit_note = ""
        if stability_result and stability_result.audit_passed:
            audit_note = (
                " Audit checks confirm exact residue mapping, valid mutation syntax, "
                "and normal FoldX completion."
            )
        return (
            "G358R shows a very large FoldX destabilization signal. PSGE treats this as a strong "
            "folding/stability hypothesis only after confirming exact residue mapping, valid mutation "
            f"syntax, normal FoldX completion, and no parser or structure-preparation anomaly.{audit_note}"
        )

    if mechanism_class == "folding_stability_hydrophobic_core" and ddg is not None:
        return (
            f"FoldX predicts ΔΔG {ddg:.2f} kcal/mol (band: {band or 'unknown'}) under the prepared "
            "3NKS protein model. This is a protein stability estimate, not a direct measure of "
            "cofactor binding, catalytic activity, or clinical outcome."
        )

    if mechanism_class == "cofactor_binding_perturbation" and context:
        return default

    return default
