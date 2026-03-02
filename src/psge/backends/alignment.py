"""Alignment and structural delta (PRD FR4, M6b)."""

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
    M6b: real RMSD from coordinates; SASA placeholder until freesasa/DSSP.
    """
    wt_path = Path(struct_pair.wt_pdb_path)
    mut_path = Path(struct_pair.mutant_pdb_path)
    pos = variant_position(variant_record.parsed)

    try:
        from psge.utils.pdb_rmsd import compute_local_rmsd, compute_rmsd, compute_sasa_delta

        global_rmsd = compute_rmsd(wt_path, mut_path)
        local_rmsd = float("nan")
        if pos is not None:
            local_rmsd = compute_local_rmsd(wt_path, mut_path, pos)
        sasa_delta = compute_sasa_delta(wt_path, mut_path, pos or 0) if pos else 0.0
    except Exception:
        global_rmsd = float("nan")
        local_rmsd = float("nan")
        sasa_delta = 0.0

    return DeltaFeatures(
        global_rmsd=global_rmsd,
        local_rmsd=local_rmsd,
        sasa_delta=sasa_delta,
        contact_deltas={},
    )
