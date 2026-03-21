"""3D distance metrics (Å) from PDB/mmCIF (Phase 1.5)."""

from pathlib import Path

from Bio.PDB import MMCIFParser, PDBParser
from Bio.PDB.Polypeptide import is_aa


def _get_parser(path: Path):
    """Return appropriate parser for file format."""
    suf = path.suffix.lower()
    if suf == ".cif":
        return MMCIFParser(QUIET=True)
    return PDBParser(QUIET=True)


def load_structure(path: Path):
    """Load structure from PDB or mmCIF."""
    parser = _get_parser(path)
    return parser.get_structure("s", str(path))


def extract_ligand_atoms(structure, resname: str) -> list:
    """
    Extract all atoms from HETATM residues with given resname.
    Returns list of Atom objects.
    mmCIF uses res.id[0] like 'H_FAD', 'H_ACJ'; PDB uses 'H'. Accept any hetero (non-space).
    """
    atoms = []
    for model in structure:
        for chain in model:
            for res in chain:
                hetflag = res.id[0] if len(res.id) else " "
                if isinstance(hetflag, str) and hetflag.strip() == "":
                    continue  # Skip standard ATOM residues
                try:
                    rn = res.get_resname()
                except (AttributeError, KeyError):
                    rn = getattr(res, "resname", "")
                rn_str = (rn if isinstance(rn, str) else str(rn)).strip().upper()
                if rn_str == resname.upper():
                    for atom in res:
                        atoms.append(atom)
    return atoms


def min_distance_atoms(set_a: list, set_b: list) -> float | None:
    """
    Minimum 3D distance (Å) between any atom in set_a and any in set_b.
    """
    if not set_a or not set_b:
        return None
    min_d = float("inf")
    for a in set_a:
        va = a.get_vector()
        for b in set_b:
            vb = b.get_vector()
            d = (va - vb).norm()
            if d < min_d:
                min_d = d
    return min_d if min_d != float("inf") else None


def _residue_atoms(res) -> list:
    """Atoms from a residue (CA preferred for distance to point)."""
    if "CA" in res:
        return [res["CA"]]
    return list(res.get_atoms())


def _build_uniprot_to_pdb_map(structure, uniprot_seq: str) -> dict[int, tuple]:
    """
    Build mapping: UniProt 1-based position -> (chain_id, res_id) in structure.
    Uses simple alignment: extract chain sequence, align to UniProt.
    Gap handling: missing positions return None.
    """
    from Bio.SeqUtils import seq1

    # Get first model, first chain (3NKS typically single chain A)
    model = structure[0]
    chain = None
    for c in model:
        chain = c
        break
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
            mapping[ui + 1] = (chain.id, pdb_residues[pi]) if pi < len(pdb_residues) else None
            ui += 1
            pi += 1
        elif u == "-":
            pi += 1
        else:
            ui += 1
    return mapping


def get_pdb_residue_for_uniprot(
    uniprot_pos: int,
    structure_path: Path,
    uniprot_sequence: str,
) -> tuple[str, int] | None:
    """
    Return (chain_id, pdb_residue_number) for UniProt position.
    For FoldX mutation format: WTaa + chain + pdb_num + Mutaa (e.g. RA59W).
    Returns None if position not in structure.
    """
    structure = load_structure(structure_path)
    mapping = _build_uniprot_to_pdb_map(structure, uniprot_sequence)
    if uniprot_pos not in mapping or mapping[uniprot_pos] is None:
        return None
    chain_id, res = mapping[uniprot_pos]
    pdb_resnum = res.id[1]
    return (str(chain_id), int(pdb_resnum))


def min_distance_residue_to_ligand(
    uniprot_pos: int,
    structure_path: Path,
    ligand_resname: str,
    uniprot_sequence: str,
) -> float | None:
    """
    Minimum 3D distance (Å) from residue at UniProt position to ligand atoms.
    Returns None if position not in structure or ligand absent.
    """
    structure = load_structure(structure_path)
    ligand_atoms = extract_ligand_atoms(structure, ligand_resname)
    if not ligand_atoms:
        return None

    mapping = _build_uniprot_to_pdb_map(structure, uniprot_sequence)
    if uniprot_pos not in mapping:
        return None
    entry = mapping[uniprot_pos]
    if entry is None:
        return None
    chain_id, res = entry
    res_atoms = _residue_atoms(res)
    return min_distance_atoms(res_atoms, ligand_atoms)


def compute_context_distances_angstrom(
    uniprot_pos: int,
    structure_path: Path,
    uniprot_sequence: str,
    site_residues: list[int] | None = None,
) -> dict[str, float | None]:
    """
    Compute 3D distances (Å) for context mapping.
    Returns: min_dist_to_fad_atoms_angstrom, min_dist_to_acj_atoms_angstrom, min_dist_to_site_residues_angstrom.
    """
    structure = load_structure(structure_path)
    fad_atoms = extract_ligand_atoms(structure, "FAD")
    acj_atoms = extract_ligand_atoms(structure, "ACJ")
    mapping = _build_uniprot_to_pdb_map(structure, uniprot_sequence)
    if uniprot_pos not in mapping:
        return {
            "min_dist_to_fad_atoms_angstrom": None,
            "min_dist_to_acj_atoms_angstrom": None,
            "min_dist_to_site_residues_angstrom": None,
        }
    entry = mapping[uniprot_pos]
    if entry is None:
        return {
            "min_dist_to_fad_atoms_angstrom": None,
            "min_dist_to_acj_atoms_angstrom": None,
            "min_dist_to_site_residues_angstrom": None,
        }
    _, res = entry
    res_atoms = _residue_atoms(res)

    dist_fad = min_distance_atoms(res_atoms, fad_atoms) if fad_atoms else None
    dist_acj = min_distance_atoms(res_atoms, acj_atoms) if acj_atoms else None

    dist_site = None
    if site_residues:
        site_excl_self = [r for r in site_residues if r != uniprot_pos]
        min_d = float("inf")
        for site_pos in site_excl_self:
            if site_pos not in mapping or mapping[site_pos] is None:
                continue
            _, site_res = mapping[site_pos]
            site_atoms = _residue_atoms(site_res)
            d = min_distance_atoms(res_atoms, site_atoms)
            if d is not None and d < min_d:
                min_d = d
        dist_site = min_d if min_d != float("inf") else None

    return {
        "min_dist_to_fad_atoms_angstrom": dist_fad,
        "min_dist_to_acj_atoms_angstrom": dist_acj,
        "min_dist_to_site_residues_angstrom": dist_site,
    }


def min_distance_residue_to_site_residues(
    uniprot_pos: int,
    structure_path: Path,
    site_residues: list[int],
    uniprot_sequence: str,
) -> float | None:
    """
    Minimum 3D distance (Å) from residue at uniprot_pos to any site residue.
    site_residues: list of UniProt 1-based positions.
    """
    structure = load_structure(structure_path)
    mapping = _build_uniprot_to_pdb_map(structure, uniprot_sequence)
    if uniprot_pos not in mapping:
        return None
    entry = mapping[uniprot_pos]
    if entry is None:
        return None
    _, res = entry
    res_atoms = _residue_atoms(res)

    min_d = float("inf")
    for site_pos in site_residues:
        if site_pos not in mapping:
            continue
        site_entry = mapping[site_pos]
        if site_entry is None:
            continue
        _, site_res = site_entry
        site_atoms = _residue_atoms(site_res)
        d = min_distance_atoms(res_atoms, site_atoms)
        if d is not None and d < min_d:
            min_d = d
    return min_d if min_d != float("inf") else None


def get_pdb_residue_for_foldx(
    uniprot_pos: int,
    structure_path: Path,
    uniprot_sequence: str,
) -> tuple[str, int, str] | None:
    """
    Return (chain_id, pdb_residue_number, wt_one_letter_aa) for FoldX mutation format.
    Returns None if position not in structure.
    """
    from Bio.SeqUtils import seq1

    structure = load_structure(structure_path)
    mapping = _build_uniprot_to_pdb_map(structure, uniprot_sequence)
    if uniprot_pos not in mapping or mapping[uniprot_pos] is None:
        return None
    chain_id, res = mapping[uniprot_pos]
    pdb_resnum = res.id[1]
    wt_aa = seq1(res.get_resname())
    return (str(chain_id), int(pdb_resnum), wt_aa)
