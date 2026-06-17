"""Evidence tiering and enriched evidence rows (Phase 1.6d)."""

from __future__ import annotations

from typing import Any

from psge.core.models import ContextFeatures, DeltaFeatures, StabilityResult
from psge.utils.stability_bands import BAND_ORDER

PDB_ID = "3NKS"
FOLDX_SOURCE_ID = "FoldX_5_on_3NKS"
STRUCTURE_SOURCE_ID = "3NKS_Qin2011"


def _row(
    signal: str,
    value: Any,
    *,
    evidence_type: str,
    evidence_tier: str,
    species_context: str = "human",
    source_id: str | None = None,
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
        if signal == "ddg" or signal == "stability_signal_band" or signal == "flags":
            continue  # handled via stability block
        if signal.startswith("sasa_") or signal == "sasa_source_pairing":
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="sasa_context",
                    evidence_tier="pdb_context_only",
                    source_id=PDB_ID,
                )
            )
        elif signal in (
            "min_dist_to_fad_atoms_angstrom",
            "min_dist_to_inhibitor_atoms_angstrom",
            "min_dist_to_active_site_residue_atoms_angstrom_excl_self",
        ):
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="structural_proximity",
                    evidence_tier="pdb_context_only",
                    source_id=PDB_ID,
                    interpretation="3D distance from experimental structure; not functional proof",
                )
            )
        elif signal in ("is_in_fad_residue_set", "is_in_active_site_residue_set"):
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="curated_site_membership",
                    evidence_tier="pdb_context_only",
                    source_id="sites_yaml_provisional",
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
                    source_id="sites_yaml_provisional",
                )
            )
        elif signal == "variant_type":
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="variant_class_rule",
                    evidence_tier="pdb_context_only",
                    species_context="not_applicable",
                )
            )
        else:
            out.append(
                _row(
                    signal,
                    value,
                    evidence_type="structural_proximity",
                    evidence_tier="pdb_context_only",
                    source_id=PDB_ID,
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
                source_id=FOLDX_SOURCE_ID,
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
                    source_id=FOLDX_SOURCE_ID,
                )
            )

    return out


def build_evidence_summary(
    enriched_rows: list[dict],
    backend_status: dict | None,
) -> dict:
    """Report-level evidence basis block."""
    tiers: set[str] = {"pdb_context_only"}
    if (backend_status or {}).get("stability_backend") == "foldx":
        tiers.add("foldx_stability_prediction")

    tier_rank = {t: i for i, t in enumerate(
        [
            "pdb_context_only",
            "foldx_stability_prediction",
            "literature_mechanistic",
            "functional_assay",
            "replicated_multi_source",
        ]
    )}
    highest = max(tiers, key=lambda t: tier_rank.get(t, 0))

    sources = [
        {
            "source_id": PDB_ID,
            "source_type": "pdb_structure",
            "species_context": "human",
        }
    ]
    if "foldx_stability_prediction" in tiers:
        sources.append(
            {
                "source_id": FOLDX_SOURCE_ID,
                "source_type": "foldx_buildmodel",
                "species_context": "human",
                "note": "Protein-only 3NKS RepairPDB input; FAD/ACJ not included in FoldX run",
            }
        )

    return {
        "overall_evidence_basis": sorted(tiers, key=lambda t: tier_rank.get(t, 0)),
        "highest_evidence_tier": highest,
        "species_context": "human",
        "clinical_interpretation": False,
        "sources": sources,
        "threshold_policy": "provisional_bands_v1_6d",
        "stability_bands": BAND_ORDER,
    }
