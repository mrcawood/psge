"""SASA computation via BioPython Shrake-Rupley (Phase 1.6a).

Option A (local-only): We compute SASA for the mutation residue and an 8 Å patch.
We do NOT compute or report global sasa_total_wt/mut deltas, because they are
noisy and meaningless when WT and mutant come from different structure sources
(e.g. experimental PDB vs mock/ESMFold).

Atom selection: protein standard AAs only (excludes HETATMs) for consistency.
"""

from pathlib import Path

from Bio.PDB import MMCIFParser, PDBParser
from Bio.PDB.Polypeptide import is_aa
from Bio.PDB.SASA import ShrakeRupley


def _get_parser(path: Path):
    """Return appropriate parser for file format."""
    suf = path.suffix.lower()
    if suf == ".cif":
        return MMCIFParser(QUIET=True)
    return PDBParser(QUIET=True)


def _build_uniprot_to_residue_map(structure, uniprot_seq: str) -> dict[int, object]:
    """
    Map UniProt 1-based position -> residue object in structure.
    Uses sequence alignment. Protein standard AAs only.
    """
    from Bio.SeqUtils import seq1

    model = structure[0]
    chain = next(iter(model), None)
    if chain is None:
        return {}

    pdb_seq = []
    pdb_residues = []
    for res in chain:
        if not is_aa(res, standard=True):
            continue
        try:
            pdb_seq.append(seq1(res.get_resname()))
            pdb_residues.append(res)
        except (KeyError, IndexError):
            continue

    pdb_str = "".join(pdb_seq)
    from Bio.Align import PairwiseAligner

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligns = list(aligner.align(uniprot_seq, pdb_str))
    if not aligns:
        return {}

    a = aligns[0]
    ui, pi = 0, 0
    mapping = {}
    for u, p in zip(a[0], a[1]):
        if u != "-" and p != "-":
            mapping[ui + 1] = pdb_residues[pi] if pi < len(pdb_residues) else None
            ui += 1
            pi += 1
        elif u == "-":
            pi += 1
        else:
            ui += 1
    return mapping


def compute_sasa_total(structure_path: Path, n_points: int = 100) -> float | None:
    """
    Compute total SASA (Å²) for structure. Used for sanity tests only.
    Option A: not reported in main pipeline (local-only).
    """
    try:
        parser = _get_parser(structure_path)
        struct = parser.get_structure("s", str(structure_path))
        sr = ShrakeRupley(n_points=n_points)
        sr.compute(struct, level="S")
        return float(struct.sasa)
    except Exception:
        return None


def _count_protein_residues(structure) -> int:
    """Count standard AA residues in first chain of first model."""
    model = structure[0]
    chain = next(iter(model), None)
    if chain is None:
        return 0
    return sum(1 for res in chain if is_aa(res, standard=True))


def _structures_comparable(struct_pair: "StructurePair") -> bool:
    """
    True when WT and mutant come from same backend (both ESMFold or both mock).
    When backend is 'pdb', WT is experimental and mutant is predicted - NOT comparable.
    """
    backend = getattr(struct_pair, "backend", "mock")
    return backend in ("esmfold", "mock")


def compute_sasa_residue(
    structure_path: Path,
    uniprot_pos: int,
    uniprot_seq: str,
    n_points: int = 100,
) -> float | None:
    """
    Compute SASA (Å²) for residue at UniProt position.
    Uses protein standard AAs only. Returns None if mapping fails.
    """
    try:
        parser = _get_parser(structure_path)
        struct = parser.get_structure("s", str(structure_path))
        mapping = _build_uniprot_to_residue_map(struct, uniprot_seq)
        if uniprot_pos not in mapping or mapping[uniprot_pos] is None:
            return None
        res = mapping[uniprot_pos]
        sr = ShrakeRupley(n_points=n_points)
        sr.compute(struct, level="R")
        return float(res.sasa)
    except Exception:
        return None


def compute_sasa_patch(
    structure_path: Path,
    uniprot_pos: int,
    uniprot_seq: str,
    radius_angstrom: float = 8.0,
    n_points: int = 100,
) -> tuple[float | None, str | None]:
    """
    Compute SASA (Å²) for residues within radius of variant position (WT only).
    Uses CA-CA distance. Returns (patch_sasa, status).
    status is "mapped" or "residue_not_in_structure" or "patch_zero_suspicious".

    Neighbor selection: center_res comes from mapping (first chain, standard AAs).
    We iterate the same chain, so center_res is always in the patch (d=0 from self).
    n_in_patch >= 1 when mapping succeeds; empty patch implies mapping/chain mismatch.
    """
    try:
        parser = _get_parser(structure_path)
        struct = parser.get_structure("s", str(structure_path))
        mapping = _build_uniprot_to_residue_map(struct, uniprot_seq)
        if uniprot_pos not in mapping or mapping[uniprot_pos] is None:
            return (None, "residue_not_in_structure")
        center_res = mapping[uniprot_pos]
        if "CA" not in center_res:
            return (None, "residue_no_ca")

        sr = ShrakeRupley(n_points=n_points)
        sr.compute(struct, level="R")
        center_sasa = float(getattr(center_res, "sasa", 0.0))
        center_vec = center_res["CA"].get_vector()

        patch_sasa = 0.0
        n_in_patch = 0
        model = struct[0]
        chain = next(iter(model), None)
        if chain is None:
            return (None, "no_chain")

        # Same chain as mapping; center_res is in this chain, so n_in_patch >= 1
        for res in chain:
            if not is_aa(res, standard=True) or "CA" not in res:
                continue
            d = (res["CA"].get_vector() - center_vec).norm()
            if d <= radius_angstrom:
                patch_sasa += float(getattr(res, "sasa", 0.0))
                n_in_patch += 1

        if patch_sasa == 0.0 and n_in_patch > 0 and center_sasa > 0:
            return (None, "patch_zero_suspicious")
        if patch_sasa == 0.0 and n_in_patch == 0:
            return (None, "patch_empty")
        # center_res is from mapping built from this same chain; we always include self (d=0)
        assert n_in_patch >= 1, "patch must contain center residue (same chain)"
        return (patch_sasa, "mapped")
    except Exception:
        return (None, "compute_error")


def compute_sasa_local(
    wt_pdb: Path,
    mut_pdb: Path,
    variant_position: int,
    uniprot_seq: str,
    struct_pair: "StructurePair",
    n_points: int = 100,
) -> tuple[
    dict[int, float] | None,
    dict[int, float] | None,
    dict[int, float] | None,
    float | None,
    str | None,
    str | None,
]:
    """
    Compute local SASA only (Option A): residue at mutation site, 8 Å patch.
    No global totals.

    Returns:
        (sasa_residue_wt, sasa_residue_mut, delta_sasa_residue,
         sasa_patch_8A, mapping_status, sasa_source_pairing)
    delta_sasa_residue is only set when both structures are from same backend.
    sasa_source_pairing: "same_backend" | "incomparable" (WT PDB vs predicted mutant)
    """
    sasa_res_wt = compute_sasa_residue(wt_pdb, variant_position, uniprot_seq, n_points)
    sasa_res_mut = compute_sasa_residue(mut_pdb, variant_position, uniprot_seq, n_points)
    sasa_residue_wt = {variant_position: sasa_res_wt} if sasa_res_wt is not None else None
    sasa_residue_mut = {variant_position: sasa_res_mut} if sasa_res_mut is not None else None

    comparable = _structures_comparable(struct_pair)
    delta_sasa_residue = None
    if comparable and sasa_res_wt is not None and sasa_res_mut is not None:
        delta_sasa_residue = {variant_position: sasa_res_mut - sasa_res_wt}
    sasa_source_pairing = "same_backend" if comparable else "incomparable"

    patch_val, patch_status = compute_sasa_patch(
        wt_pdb, variant_position, uniprot_seq, radius_angstrom=8.0, n_points=n_points
    )
    sasa_patch_8A = patch_val

    mapping_status = "mapped" if (sasa_res_wt is not None or sasa_res_mut is not None) else "residue_not_in_structure"
    if patch_status not in ("mapped", "residue_not_in_structure"):
        mapping_status = mapping_status + f";patch:{patch_status}"

    return (
        sasa_residue_wt,
        sasa_residue_mut,
        delta_sasa_residue,
        sasa_patch_8A,
        mapping_status,
        sasa_source_pairing,
    )
