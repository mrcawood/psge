"""Mechanism classifier (PRD FR7, Phase 1.5 ClinGen-aligned taxonomy)."""

from psge.core.models import (
    Config,
    ContextFeatures,
    DeltaFeatures,
    MechanismHypothesis,
    StabilityResult,
    VariantRecord,
)
from psge.utils.variant_parse import variant_position

# 3D proximity thresholds (Å) — Phase 1.5
CONTACT_ANGSTROM = 6.0
NEAR_ANGSTROM = 8.0


def classify(
    variant_record: VariantRecord,
    delta: DeltaFeatures | None,
    stability_result: StabilityResult | None,
    context: ContextFeatures | None,
    config: Config,
    backend_status: dict | None = None,
) -> MechanismHypothesis:
    """
    Rules-based mechanism classification (Phase 1.5).
    Order: truncation -> targeting (secondary only) -> cofactor (3D Å) -> stability -> default.
    """
    # 1. non_structural_track -> truncation_misexpression
    if variant_record.track == "non_structural":
        return MechanismHypothesis(
            class_="truncation_misexpression",
            confidence="plausible",
            evidence_table=[{"signal": "variant_type", "value": variant_record.type}],
            interpretation="Variant classified as truncation/splice; structural modeling not applied.",
            limits="PSGE does not infer splice or expression effects; recommend transcript/annotation analysis.",
            decision_trace=["rule: non_structural_track → truncation_misexpression"],
        )

    # Build secondary hypotheses (targeting is never primary by default)
    # Only add a secondary if it has at least one concrete evidence item
    secondary = []
    if context and _has_secondary_evidence_targeting(context):
        secondary.append("targeting_signal_perturbation")

    _stab = (backend_status or {}).get("stability_backend", "mock")
    stability_mock = _stab in ("mock", "not_available", "foldx_failed")
    _destabilizing = (
        stability_result
        and (stability_result.ddg >= 2.0 or "destabilizing" in stability_result.flags)
    )

    # 2. cofactor_contact -> cofactor_binding_perturbation (FAD/ACJ distance or membership fallback)
    # In targeting region (e.g. I12T): cofactor is secondary only; primary is folding/unknown
    if context and _cofactor_contact(context) and not context.in_targeting_region:
        sec = secondary.copy()
        if _destabilizing:
            sec.append("folding_stability_hydrophobic_core")
        pos = variant_position(variant_record.parsed)
        evidence = _cofactor_evidence(context)
        interp = _cofactor_interpretation(context, pos)
        # Low confidence when membership-only (no real FAD/inhibitor distance)
        conf = "plausible" if _has_ligand_distance(context) else "low (membership-only)"
        return MechanismHypothesis(
            class_="cofactor_binding_perturbation",
            confidence=conf,
            evidence_table=evidence,
            interpretation=interp,
            limits="3D distance from PDB; static structure only.",
            decision_trace=["rule: cofactor_contact (≤ 6 Å) → cofactor_binding_perturbation"],
            secondary_hypotheses=sec,
        )
    # Targeting region + cofactor contact: add cofactor to secondary (if evidence), fall through
    if context and _cofactor_contact(context) and context.in_targeting_region:
        if _has_secondary_evidence_cofactor(context):
            secondary.append("cofactor_binding_perturbation")

    # 3. active_site_contact (3D Å, excluding self) -> active_site_region_perturbation
    # In targeting region: active_site may be secondary only (not primary)
    if context and _active_site_contact(context) and context.in_targeting_region:
        if _has_secondary_evidence_active_site(context):
            secondary.append("active_site_region_perturbation")
        # Fall through; primary cannot be active_site here
    elif context and _active_site_contact(context) and not context.in_targeting_region:
        sec = secondary.copy()
        if _destabilizing:
            sec.append("folding_stability_hydrophobic_core")
        evidence = _active_site_evidence(context)
        interp = _active_site_interpretation(context)
        return MechanismHypothesis(
            class_="active_site_region_perturbation",
            confidence="plausible",
            evidence_table=evidence,
            interpretation=interp,
            limits="3D distance from PDB; static structure only.",
            decision_trace=["rule: active_site_contact (≤ 8 Å) → active_site_region_perturbation"],
            secondary_hypotheses=sec,
        )

    # 4. stability_or_core -> folding_stability_hydrophobic_core
    # Phase 1.6: Only fire as PRIMARY when stability backend is real (foldx/rosetta).
    # Mock ddG must not drive primary classification; stability-derived hypotheses
    # remain secondary/unknown when stability is unavailable.
    if _destabilizing and not stability_mock:
        evidence = [
            {"signal": "ddg", "value": stability_result.ddg},
            {"signal": "flags", "value": stability_result.flags},
        ]
        sec = secondary.copy()
        return MechanismHypothesis(
            class_="folding_stability_hydrophobic_core",
            confidence="plausible",
            evidence_table=evidence,
            interpretation="Stability analysis suggests folding/core destabilization.",
            limits="3D structure and FoldX ΔΔG; static only.",
            decision_trace=["rule: stability_or_core → folding_stability_hydrophobic_core"],
            secondary_hypotheses=sec,
        )
    # Mock destabilizing: add folding_stability to secondaries only, fall through to default
    if _destabilizing and stability_mock:
        secondary.append("folding_stability_hydrophobic_core")

    # 5. default -> unknown_mechanism
    # Filter secondaries to those with evidence; build evidence table for report
    sec_filtered = _filter_secondaries_by_evidence(secondary, context, variant_record)
    evidence = _default_evidence(variant_record, context, sec_filtered)
    return MechanismHypothesis(
        class_="unknown_mechanism",
        confidence="low",
        evidence_table=evidence,
        interpretation="Insufficient evidence for specific mechanism; no rule matched.",
        limits="Limited structural/stability data; mechanism hypothesis tentative.",
        decision_trace=["rule: default_structural → unknown_mechanism (low confidence)"],
        secondary_hypotheses=sec_filtered,
    )


def _has_ligand_distance(ctx: ContextFeatures) -> bool:
    """True if we have real FAD or inhibitor distance (not just membership)."""
    if ctx.min_dist_to_fad_atoms_angstrom is not None:
        return True
    if getattr(ctx, "min_dist_to_inhibitor_atoms_angstrom", None) is not None:
        return True
    return False


def _cofactor_contact(ctx: ContextFeatures) -> bool:
    """Within 6 Å of FAD/inhibitor (contact) or is_in_fad_residue_set fallback when ligand atoms missing."""
    if ctx.min_dist_to_fad_atoms_angstrom is not None and ctx.min_dist_to_fad_atoms_angstrom <= CONTACT_ANGSTROM:
        return True
    d_inhib = getattr(ctx, "min_dist_to_inhibitor_atoms_angstrom", None)
    if d_inhib is not None and d_inhib <= CONTACT_ANGSTROM:
        return True
    # Membership fallback: only when NOT in targeting region (avoids I12T in 9-14 FAD motif)
    if getattr(ctx, "is_in_fad_residue_set", False) and not getattr(ctx, "in_targeting_region", True):
        return True
    return False


def _active_site_contact(ctx: ContextFeatures) -> bool:
    """Within 8 Å of other active-site residues (excluding self). FAD/ACJ contact takes precedence."""
    if _cofactor_contact(ctx):
        return False
    d = getattr(ctx, "min_dist_to_active_site_residue_atoms_angstrom_excl_self", None)
    if d is not None and d <= NEAR_ANGSTROM:
        return True
    return False


def _cofactor_evidence(ctx: ContextFeatures) -> list[dict]:
    """Evidence table for cofactor rule."""
    ev = [
        {"signal": "contact_threshold_angstrom", "value": CONTACT_ANGSTROM},
        {"signal": "near_threshold_angstrom", "value": NEAR_ANGSTROM},
    ]
    if ctx.min_dist_to_fad_atoms_angstrom is not None:
        ev.append({"signal": "min_dist_to_fad_atoms_angstrom", "value": round(ctx.min_dist_to_fad_atoms_angstrom, 2)})
    d_inhib = getattr(ctx, "min_dist_to_inhibitor_atoms_angstrom", None)
    if d_inhib is not None:
        ev.append({"signal": "min_dist_to_inhibitor_atoms_angstrom", "value": round(d_inhib, 2)})
    ev.append({"signal": "is_in_fad_residue_set", "value": getattr(ctx, "is_in_fad_residue_set", False)})
    d_site = getattr(ctx, "min_dist_to_active_site_residue_atoms_angstrom_excl_self", None)
    if d_site is not None:
        ev.append({"signal": "min_dist_to_active_site_residue_atoms_angstrom_excl_self", "value": round(d_site, 2)})
    return ev


def _cofactor_interpretation(ctx: ContextFeatures, pos: int | None) -> str:
    """Interpretation text for cofactor rule. Includes caveat to avoid implying causality."""
    pos_str = f"Residue {pos}" if pos is not None else "Residue"
    d_fad = ctx.min_dist_to_fad_atoms_angstrom
    d_inhib = getattr(ctx, "min_dist_to_inhibitor_atoms_angstrom", None)
    caveat = "; this is consistent with a potential cofactor-environment perturbation, but does not establish functional impact."
    if d_fad is not None and d_inhib is not None:
        return f"{pos_str} lies within {d_fad:.1f} Å of FAD atoms (3NKS reference) and {d_inhib:.1f} Å of the bound inhibitor{caveat}"
    if d_fad is not None:
        return f"{pos_str} lies within {d_fad:.1f} Å of FAD atoms (3NKS reference){caveat}"
    if d_inhib is not None:
        return f"{pos_str} lies within {d_inhib:.1f} Å of the bound inhibitor{caveat}"
    if getattr(ctx, "is_in_fad_residue_set", False):
        return f"{pos_str} in FAD-binding set; this is consistent with a potential cofactor-environment perturbation (low confidence, membership-only), but does not establish functional impact."
    return "Cofactor-binding region perturbation plausible."


def _active_site_evidence(ctx: ContextFeatures) -> list[dict]:
    """Evidence table for active-site rule."""
    ev = [
        {"signal": "contact_threshold_angstrom", "value": CONTACT_ANGSTROM},
        {"signal": "near_threshold_angstrom", "value": NEAR_ANGSTROM},
    ]
    d = getattr(ctx, "min_dist_to_active_site_residue_atoms_angstrom_excl_self", None)
    if d is not None:
        ev.append({"signal": "min_dist_to_active_site_residue_atoms_angstrom_excl_self", "value": round(d, 2)})
    ev.append({"signal": "is_in_active_site_residue_set", "value": getattr(ctx, "is_in_active_site_residue_set", False)})
    return ev


def _active_site_interpretation(ctx: ContextFeatures) -> str:
    """Interpretation text for active-site rule."""
    d = getattr(ctx, "min_dist_to_active_site_residue_atoms_angstrom_excl_self", None)
    if d is not None:
        return f"Variant within {d:.1f} Å of active-site residues (excluding self); catalytic region perturbation plausible."
    return "Variant in active-site residue set; catalytic region perturbation plausible."


# --- Secondary evidence requirements (no secondary without evidence) ---


def _has_secondary_evidence_targeting(ctx: ContextFeatures) -> bool:
    """targeting_signal_perturbation requires in_targeting_region."""
    return bool(ctx.in_targeting_region)


def _has_secondary_evidence_cofactor(ctx: ContextFeatures) -> bool:
    """cofactor_binding_perturbation requires FAD distance or FAD membership fallback."""
    if ctx.min_dist_to_fad_atoms_angstrom is not None:
        return True
    if getattr(ctx, "min_dist_to_inhibitor_atoms_angstrom", None) is not None:
        return True
    return bool(getattr(ctx, "is_in_fad_residue_set", False))


def _has_secondary_evidence_active_site(ctx: ContextFeatures) -> bool:
    """active_site_region_perturbation requires site distance or membership."""
    d = getattr(ctx, "min_dist_to_active_site_residue_atoms_angstrom_excl_self", None)
    if d is not None and d <= NEAR_ANGSTROM:
        return True
    return bool(getattr(ctx, "is_in_active_site_residue_set", False))


def _filter_secondaries_by_evidence(
    secondaries: list[str],
    context: ContextFeatures | None,
    variant_record: VariantRecord,
) -> list[str]:
    """Retain only secondaries that have at least one concrete evidence item."""
    if not context:
        return [s for s in secondaries if s == "folding_stability_hydrophobic_core"]
    out = []
    for s in secondaries:
        if s == "targeting_signal_perturbation" and _has_secondary_evidence_targeting(context):
            out.append(s)
        elif s == "cofactor_binding_perturbation" and _has_secondary_evidence_cofactor(context):
            out.append(s)
        elif s == "active_site_region_perturbation" and _has_secondary_evidence_active_site(context):
            out.append(s)
        elif s == "folding_stability_hydrophobic_core":
            out.append(s)  # Evidence comes from stability_result, not context
        else:
            pass  # drop if no evidence
    return out


def _default_evidence(
    variant_record: VariantRecord,
    context: ContextFeatures | None,
    secondaries: list[str],
) -> list[dict]:
    """Build evidence table for default (unknown) branch from context and secondaries."""
    ev: list[dict] = []
    if not context:
        return ev
    pos = variant_position(variant_record.parsed)
    # Evidence for each secondary we emit
    if "targeting_signal_perturbation" in secondaries:
        ev.append({"signal": "in_targeting_region", "value": context.in_targeting_region})
        if pos is not None:
            ev.append({"signal": "pos", "value": pos})
        if context.n_terminal_targeting_signal_end is not None:
            ev.append({"signal": "n_terminal_targeting_signal_end", "value": context.n_terminal_targeting_signal_end})
    if "cofactor_binding_perturbation" in secondaries:
        if context.min_dist_to_fad_atoms_angstrom is not None:
            ev.append({"signal": "min_dist_to_fad_atoms_angstrom", "value": round(context.min_dist_to_fad_atoms_angstrom, 2)})
        d_inhib = getattr(context, "min_dist_to_inhibitor_atoms_angstrom", None)
        if d_inhib is not None:
            ev.append({"signal": "min_dist_to_inhibitor_atoms_angstrom", "value": round(d_inhib, 2)})
        ev.append({"signal": "is_in_fad_residue_set", "value": getattr(context, "is_in_fad_residue_set", False)})
    if "active_site_region_perturbation" in secondaries:
        d = getattr(context, "min_dist_to_active_site_residue_atoms_angstrom_excl_self", None)
        if d is not None:
            ev.append({"signal": "min_dist_to_active_site_residue_atoms_angstrom_excl_self", "value": round(d, 2)})
        ev.append({"signal": "is_in_active_site_residue_set", "value": getattr(context, "is_in_active_site_residue_set", False)})
    return ev
