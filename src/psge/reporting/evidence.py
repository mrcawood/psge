"""Evidence tiering and enriched evidence rows (Phase 1.6d/1.6e)."""

from __future__ import annotations

from typing import Any

from psge.core.models import DeltaFeatures, StabilityResult
from psge.sources.loader import (
    get_variant_evidence,
    highest_tier_for_variant,
    load_source_registry,
)
from psge.utils.stability_bands import BAND_ORDER

SOURCE_PDB = "PDB_3NKS"
SOURCE_FOLDX = "FOLDX_5_3NKS"
SOURCE_SASA = "SASA_BIOPYTHON_3NKS"
SOURCE_SITES = "sites_yaml_provisional"


def _row(
    signal: str,
    value: Any,
    *,
    evidence_type: str,
    evidence_tier: str,
    species_context: str = "human",
    source_id: str | None = None,
    claim_scope: str | None = None,
    interpretation: str | None = None,
) -> dict:
    row: dict[str, Any] = {
        "signal": signal,
        "value": value,
        "evidence_type": evidence_type,
        "evidence_tier": evidence_tier,
        "species_context": species_context,
    }
    if source_id:
        row["source_id"] = source_id
    if claim_scope:
        row["claim_scope"] = claim_scope
    if interpretation:
        row["interpretation"] = interpretation
    return row


def enrich_evidence_rows(
    raw_rows: list[dict],
    *,
    stability_result: StabilityResult | None,
    delta: DeltaFeatures | None,
    backend_status: dict | None,
) -> list[dict]:
    """Attach per-row evidence metadata to classifier/context rows."""
    out: list[dict] = []
    stab_backend = (backend_status or {}).get("stability_backend")

    for row in raw_rows:
        signal = row.get("signal", "")
        value = row.get("value")
        if signal in ("ddg", "stability_signal_band", "flags"):
            continue
        if signal.startswith("sasa_") or signal == "sasa_source_pairing":
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="sasa_context",
                    evidence_tier="pdb_context_only",
                    source_id=SOURCE_SASA,
                    claim_scope="structural_context",
                )
            )
        elif signal in (
            "min_dist_to_fad_atoms_angstrom",
            "min_dist_to_inhibitor_atoms_angstrom",
            "min_dist_to_active_site_residue_atoms_angstrom_excl_self",
        ):
            interp = "FAD-environment proximity" if "fad" in signal else "inhibitor-pocket proxy proximity"
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="structural_proximity",
                    evidence_tier="pdb_context_only",
                    source_id=SOURCE_PDB,
                    claim_scope="structural_context",
                    interpretation=interp,
                )
            )
        elif signal in ("is_in_fad_residue_set", "is_in_active_site_residue_set"):
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="curated_site_membership",
                    evidence_tier="pdb_context_only",
                    source_id=SOURCE_SITES,
                    claim_scope="structural_context",
                    interpretation="Curated residue set; Pete has not formally endorsed exact lists",
                )
            )
        elif signal in ("in_targeting_region", "pos", "n_terminal_targeting_signal_end"):
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="curated_site_membership",
                    evidence_tier="pdb_context_only",
                    source_id=SOURCE_SITES,
                    claim_scope="structural_context",
                )
            )
        elif signal == "variant_type":
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="variant_class_rule",
                    evidence_tier="variant_class_rule",
                    species_context="not_applicable",
                    claim_scope="structural_context",
                )
            )
        else:
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="structural_proximity",
                    evidence_tier="pdb_context_only",
                    source_id=SOURCE_PDB,
                    claim_scope="structural_context",
                )
            )

    if stability_result and stab_backend == "foldx":
        band = stability_result.stability_signal_band
        out.append(
            _row(
                "ddg",
                round(stability_result.ddg, 5),
                evidence_type="foldx_ddg",
                evidence_tier="foldx_stability_prediction",
                source_id=SOURCE_FOLDX,
                claim_scope="computational_prediction",
                interpretation=band,
            )
        )
        if band:
            out.append(
                _row(
                    "stability_signal_band",
                    band,
                    evidence_type="foldx_ddg",
                    evidence_tier="foldx_stability_prediction",
                    source_id=SOURCE_FOLDX,
                    claim_scope="computational_prediction",
                )
            )

    return out


def build_evidence_summary(
    enriched_rows: list[dict],
    backend_status: dict | None,
    variant: str,
) -> dict:
    """Report-level evidence basis block including variant map."""
    registry = load_source_registry()
    ve = get_variant_evidence(variant)

    tier_rank = {
        "not_applicable": -1,
        "variant_class_rule": 0,
        "pdb_context_only": 1,
        "foldx_stability_prediction": 2,
        "literature_mechanistic": 3,
        "functional_assay": 4,
        "replicated_multi_source": 5,
    }
    tiers: set[str] = set()
    sources: list[dict] = []

    for sid in ve.get("psge_computed_evidence", []):
        src = registry[sid]
        tiers.add(src["evidence_tier"])
        sources.append({
            "source_id": sid,
            "source_type": src["source_type"],
            "species_context": src.get("species_context", "human"),
        })

    external_rows = []
    for ext in ve.get("external_evidence", []):
        sid = ext["source_id"]
        src = registry[sid]
        et = ext.get("evidence_tier") or src["evidence_tier"]
        tiers.add(et)
        external_rows.append({
            "source_id": sid,
            "evidence_tier": et,
            "claim_scope": ext.get("claim_scope"),
            "claim": ext.get("claim"),
            "confidence": ext.get("confidence"),
            "verification_status": src.get("verification_status"),
        })
        sources.append({
            "source_id": sid,
            "source_type": src["source_type"],
            "species_context": src.get("species_context", "human"),
            "title": src.get("title"),
            "verification_status": src.get("verification_status"),
        })

    highest = highest_tier_for_variant(variant, backend_status)
    if highest not in tiers:
        tiers.add(highest)

    return {
        "overall_evidence_basis": sorted(tiers, key=lambda t: tier_rank.get(t, 0)),
        "highest_evidence_tier": highest,
        "evidence_basis_description": ve.get("evidence_basis"),
        "structural_evidence_status": ve.get("structural_evidence_status"),
        "species_context": "human",
        "clinical_interpretation": False,
        "sources": sources,
        "computed_evidence_source_ids": list(ve.get("psge_computed_evidence", [])),
        "external_evidence": external_rows,
        "evidence_gaps": list(ve.get("evidence_gap", [])),
        "threshold_policy": "provisional_bands_v1_6d",
        "stability_bands": BAND_ORDER,
    }


def evidence_basis_intro(variant: str | None = None) -> str:
    if variant:
        ve = get_variant_evidence(variant)
        if ve.get("evidence_basis"):
            return (
                f"Evidence basis for this variant: {ve['evidence_basis']}. "
                "Structural, FoldX, and SASA backends were not applied. "
                "Mechanism assignment follows variant-class routing rules only."
            )
    return (
        "This report combines PSGE-computed structural context from 3NKS, local SASA context, "
        "and FoldX ΔΔG stability prediction when available. External literature evidence is "
        "listed separately when curated sources are available. FoldX values are computational "
        "predictions and do not establish enzyme activity, cofactor affinity, penetrance, or "
        "clinical outcome."
    )


VERIFICATION_LABELS = {
    "bibliography_verified": (
        "curated from project bibliography/reference notes; "
        "primary-paper verification recommended before external circulation"
    ),
    "primary_text_verified": "verified against primary paper text",
    "pending_primary_verification": "pending primary-paper verification",
}


def external_evidence_rows(variant: str) -> list[dict]:
    """Per-row external evidence from variant map (Phase 1.6e)."""
    registry = load_source_registry()
    rows: list[dict] = []
    for ext in get_variant_evidence(variant).get("external_evidence", []):
        sid = ext["source_id"]
        src = registry[sid]
        et = ext.get("evidence_tier") or src["evidence_tier"]
        src_type = src.get("source_type", "literature")
        evidence_type = (
            "functional_assay"
            if et == "functional_assay" or src_type == "functional_assay"
            else "literature_claim"
        )
        rows.append(
            _row(
                f"external_{sid}",
                ext.get("claim") or src.get("claim_text", ""),
                evidence_type=evidence_type,
                evidence_tier=et,
                source_id=sid,
                species_context=src.get("species_context", "human"),
                claim_scope=ext.get("claim_scope"),
                interpretation="external functional evidence exists"
                if et == "functional_assay"
                else "external literature context",
            )
        )
    return rows


def format_external_evidence_section(variant: str) -> str:
    registry = load_source_registry()
    ve = get_variant_evidence(variant)
    external = ve.get("external_evidence", [])
    if not external:
        return (
            "No curated external functional evidence is currently linked for this variant in PSGE. "
            "Interpretation is therefore limited to computed structural context and FoldX prediction."
        )
    if variant == "R59W":
        lines = [
            "R59W has curated literature evidence reporting reduced PPOX enzyme activity "
            "(Meissner et al. 1996). Qin et al. (2011) discuss R59W in relation to the "
            "FAD/cofactor environment as mechanistic context.",
            "",
            "Literature verification: external sources are "
            + VERIFICATION_LABELS["bibliography_verified"]
            + ".",
            "",
            "PSGE treats external sources as supporting biological relevance and mechanistic "
            "context. PSGE mechanism assignment remains a hypothesis based on structural context "
            "and FoldX prediction unless explicitly stated otherwise.",
            "",
        ]
        for ext in external:
            src = registry[ext["source_id"]]
            vs = src.get("verification_status")
            label = VERIFICATION_LABELS.get(vs, vs or "unknown")
            lines.append(
                f"- [{ext['source_id']}] {ext.get('claim', '').strip()} "
                f"(verification: {label})"
            )
        return "\n".join(lines)
    lines = []
    for ext in external:
        lines.append(f"- [{ext['source_id']}] {ext.get('claim', '').strip()}")
    lines.append(
        "PSGE treats external sources as supporting context. PSGE mechanism assignment remains "
        "a hypothesis based on computed structural context and FoldX prediction unless "
        "explicitly stated otherwise."
    )
    return "\n".join(lines)
