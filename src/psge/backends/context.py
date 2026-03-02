"""Context mapping (PRD FR6, Phase 1.5)."""

from pathlib import Path

from psge.core.models import Config, StructurePair, VariantRecord
from psge.utils.knowledge_loader import load_ppox_sites


def map_context(
    variant_record: VariantRecord,
    struct_pair: StructurePair,
    config: Config,
):
    """Compute context features from variant and structure. Uses 3D Å when PDB available."""
    from psge.core.models import ContextFeatures

    sites = load_ppox_sites()
    pos = _variant_position(variant_record.parsed)
    if pos is None:
        return ContextFeatures()

    targeting_end = sites.get("n_terminal_targeting_signal_end") or sites.get("targeting_region_end", 28)
    in_targeting = 1 <= pos <= targeting_end

    fad_residues = sites.get("fad_residues", [])
    active_residues = sites.get("active_site_residues", [])
    seq_dist_fad = _min_distance_to_residues(pos, fad_residues)
    seq_dist_active = _min_distance_to_residues(pos, active_residues)

    mem_start = sites.get("membrane_region_start")
    mem_end = sites.get("membrane_region_end")
    in_membrane = (
        mem_start is not None
        and mem_end is not None
        and mem_start <= pos <= mem_end
    )

    # Membership (residue in curated sets)
    is_in_fad = pos in fad_residues
    is_in_active = pos in active_residues

    # 3D Å metrics when WT structure is real PDB (e.g. 3NKS)
    dist_fad_a = None
    dist_inhibitor_a = None
    dist_site_excl_self_a = None
    wt_path = Path(struct_pair.wt_pdb_path)
    if wt_path.exists() and struct_pair.backend == "pdb":
        try:
            from psge.backends.sequence import fetch_canonical_sequence
            from psge.utils.pdb_distances import compute_context_distances_angstrom
            uniprot_seq = fetch_canonical_sequence(config.gene)
            site_res = list(set(fad_residues + active_residues))
            dists = compute_context_distances_angstrom(
                pos, wt_path, uniprot_seq, site_residues=site_res
            )
            dist_fad_a = dists["min_dist_to_fad_atoms_angstrom"]
            dist_inhibitor_a = dists["min_dist_to_acj_atoms_angstrom"]
            dist_site_excl_self_a = dists["min_dist_to_site_residues_angstrom"]
        except Exception:
            pass

    return ContextFeatures(
        min_dist_to_fad_atoms_angstrom=dist_fad_a,
        min_dist_to_inhibitor_atoms_angstrom=dist_inhibitor_a,
        min_dist_to_active_site_residue_atoms_angstrom_excl_self=dist_site_excl_self_a,
        is_in_fad_residue_set=is_in_fad,
        is_in_active_site_residue_set=is_in_active,
        distance_fad=seq_dist_fad,
        distance_active_site=seq_dist_active,
        in_targeting_region=in_targeting,
        in_membrane_region=in_membrane,
        n_terminal_targeting_signal_end=targeting_end,
    )


def _variant_position(variant: str) -> int | None:
    """Extract residue position from missense variant."""
    from psge.utils.variant_parse import variant_position
    return variant_position(variant)


def _min_distance_to_residues(pos: int, residues: list[int]) -> float | None:
    """Sequence distance to nearest residue in list (residue difference)."""
    if not residues:
        return None
    return float(min(abs(pos - r) for r in residues))
