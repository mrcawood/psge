"""Real RMSD and structural metrics (M6b)."""

from pathlib import Path

from Bio.PDB import PDBParser, Superimposer
from Bio.PDB.Polypeptide import is_aa


def compute_rmsd(wt_pdb: Path, mut_pdb: Path, use_ca_only: bool = True) -> float:
    """
    Compute global backbone RMSD between WT and mutant structures.
    Uses BioPython Superimposer.
    """
    parser = PDBParser(QUIET=True)
    wt_struct = parser.get_structure("wt", str(wt_pdb))
    mut_struct = parser.get_structure("mut", str(mut_pdb))
    wt_atoms = _get_atoms(wt_struct, use_ca_only)
    mut_atoms = _get_atoms(mut_struct, use_ca_only)
    if len(wt_atoms) != len(mut_atoms) or len(wt_atoms) == 0:
        return float("nan")
    sup = Superimposer()
    sup.set_atoms(wt_atoms, mut_atoms)
    sup.run()
    return sup.rms


def compute_local_rmsd(
    wt_pdb: Path,
    mut_pdb: Path,
    center_residue: int,
    radius: int = 5,
) -> float:
    """RMSD for residues within radius of center_residue."""
    parser = PDBParser(QUIET=True)
    wt_struct = parser.get_structure("wt", str(wt_pdb))
    mut_struct = parser.get_structure("mut", str(mut_pdb))
    wt_atoms = _get_atoms_in_range(wt_struct, center_residue, radius)
    mut_atoms = _get_atoms_in_range(mut_struct, center_residue, radius)
    if len(wt_atoms) != len(mut_atoms) or len(wt_atoms) == 0:
        return float("nan")
    sup = Superimposer()
    sup.set_atoms(wt_atoms, mut_atoms)
    sup.run()
    return sup.rms


def _get_atoms(struct, ca_only: bool):
    """Extract CA or backbone atoms in order."""
    atoms = []
    for model in struct:
        for chain in model:
            for res in chain:
                if not is_aa(res, standard=True):
                    continue
                if ca_only:
                    if "CA" in res:
                        atoms.append(res["CA"])
                else:
                    for name in ["N", "CA", "C", "O"]:
                        if name in res:
                            atoms.append(res[name])
    return atoms


def _get_atoms_in_range(struct, center: int, radius: int):
    """Atoms from residues in [center-radius, center+radius]."""
    atoms = []
    for model in struct:
        for chain in model:
            for res in chain:
                if not is_aa(res, standard=True):
                    continue
                try:
                    res_id = res.id[1]
                except (IndexError, TypeError):
                    continue
                if abs(res_id - center) <= radius:
                    if "CA" in res:
                        atoms.append(res["CA"])
    return atoms


def compute_sasa_delta(wt_pdb: Path, mut_pdb: Path, variant_position: int) -> float:
    """
    Placeholder: SASA delta. Real impl would use freesasa or DSSP.
    Returns 0.0 until integrated; documented in backend_status.
    """
    return 0.0
