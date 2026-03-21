"""Alignment and structural delta (PRD FR4, M6b, Phase 1.6a)."""

from pathlib import Path

from psge.core.models import Config, DeltaFeatures, StructurePair, VariantRecord
from psge.utils.variant_parse import variant_position


def compute_delta(
    variant_record: VariantRecord,
    struct_pair: StructurePair,
    config: Config,
) -> DeltaFeatures:
    """
    Compute structural delta features.
    M6b: real RMSD; Phase 1.6a: real SASA via BioPython Shrake-Rupley.
    """
    wt_path = Path(struct_pair.wt_pdb_path)
    mut_path = Path(struct_pair.mutant_pdb_path)
    pos = variant_position(variant_record.parsed)

    try:
        from psge.utils.pdb_rmsd import compute_local_rmsd, compute_rmsd

        global_rmsd = compute_rmsd(wt_path, mut_path)
        local_rmsd = float("nan")
        if pos is not None:
            local_rmsd = compute_local_rmsd(wt_path, mut_path, pos)
    except Exception:
        global_rmsd = float("nan")
        local_rmsd = float("nan")

    sasa_delta = 0.0
    sasa_total_wt = None
    sasa_total_mut = None
    delta_sasa_total = None
    sasa_residue_wt = None
    sasa_residue_mut = None
    delta_sasa_residue = None
    sasa_patch_8A = None
    sasa_mapping_status = None

    if pos is not None and wt_path.exists() and mut_path.exists():
        try:
            from psge.backends.sequence import fetch_canonical_sequence
            from psge.utils.sasa import compute_sasa_local

            uniprot_seq = fetch_canonical_sequence(config.gene)
            (
                sasa_residue_wt,
                sasa_residue_mut,
                delta_sasa_residue,
                sasa_patch_8A,
                sasa_mapping_status,
                sasa_source_pairing,
            ) = compute_sasa_local(wt_path, mut_path, pos, uniprot_seq, struct_pair)
            if delta_sasa_residue and pos in delta_sasa_residue:
                sasa_delta = delta_sasa_residue[pos]
        except Exception:
            sasa_mapping_status = "compute_error"
    elif pos is None:
        sasa_mapping_status = "no_variant_position"

    return DeltaFeatures(
        global_rmsd=global_rmsd,
        local_rmsd=local_rmsd,
        sasa_delta=sasa_delta,
        contact_deltas={},
        sasa_total_wt=None,  # Option A: not reported (incomparable when pdb_first)
        sasa_total_mut=None,
        delta_sasa_total=None,
        sasa_residue_wt=sasa_residue_wt,
        sasa_residue_mut=sasa_residue_mut,
        delta_sasa_residue=delta_sasa_residue,
        sasa_patch_8A=sasa_patch_8A,
        sasa_mapping_status=sasa_mapping_status,
        sasa_source_pairing=sasa_source_pairing if pos else None,
    )
