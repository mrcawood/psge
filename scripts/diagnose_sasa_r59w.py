#!/usr/bin/env python3
"""
Diagnostic script: trace SASA paths and structure details for R59W.
Run: python scripts/diagnose_sasa_r59w.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from psge.core.models import Config
from psge.pipeline.stages import preflight, sequence, structure


def _count_atoms_residues(path: Path) -> tuple[int, int]:
    """Count atoms and standard AA residues in structure."""
    try:
        from Bio.PDB import MMCIFParser, PDBParser
        from Bio.PDB.Polypeptide import is_aa

        suf = path.suffix.lower()
        parser = MMCIFParser(QUIET=True) if suf == ".cif" else PDBParser(QUIET=True)
        struct = parser.get_structure("s", str(path))
        n_atoms = 0
        n_residues = 0
        for model in struct:
            for chain in model:
                for res in chain:
                    if is_aa(res, standard=True):
                        n_residues += 1
                        n_atoms += len(list(res.get_atoms()))
        return n_atoms, n_residues
    except Exception as e:
        return -1, -1


def main():
    config = Config(
        results_dir="/tmp/sasa_diag",
        cache_dir="/tmp/sasa_diag_cache",
        structure_source="pdb_first",
    )
    rec = preflight("R59W", config)
    seq = sequence(rec, config)
    struct_pair = structure(rec, seq, config)

    if not struct_pair:
        print("No structure pair")
        return

    wt_path = Path(struct_pair.wt_pdb_path)
    mut_path = Path(struct_pair.mutant_pdb_path)

    print("=== SASA Diagnostic for R59W (pdb_first) ===\n")
    print(f"structure_pair.backend: {struct_pair.backend}")
    print(f"\nWT structure path: {wt_path}")
    print(f"  exists: {wt_path.exists()}")
    if wt_path.exists():
        n_atoms, n_res = _count_atoms_residues(wt_path)
        print(f"  atoms (protein): {n_atoms}")
        print(f"  residues (standard AA): {n_res}")

    print(f"\nMutant structure path: {mut_path}")
    print(f"  exists: {mut_path.exists()}")
    if mut_path.exists():
        n_atoms, n_res = _count_atoms_residues(mut_path)
        print(f"  atoms (protein): {n_atoms}")
        print(f"  residues (standard AA): {n_res}")
        if mut_path.exists():
            lines = mut_path.read_text().splitlines()
            print(f"  first 5 lines: {lines[:5]}")

    print("\n=== Chain IDs (first model) ===")
    for label, path in [("WT", wt_path), ("Mutant", mut_path)]:
        if not path.exists():
            continue
        try:
            from Bio.PDB import MMCIFParser, PDBParser
            suf = path.suffix.lower()
            parser = MMCIFParser(QUIET=True) if suf == ".cif" else PDBParser(QUIET=True)
            struct = parser.get_structure("s", str(path))
            chains = list(struct[0].get_chains())
            print(f"  {label}: {[c.id for c in chains]}")
        except Exception as e:
            print(f"  {label}: error {e}")

    print("\n=== Heteroatoms (WT) ===")
    if wt_path.exists():
        try:
            from Bio.PDB import MMCIFParser
            parser = MMCIFParser(QUIET=True)
            struct = parser.get_structure("s", str(wt_path))
            het_residues = []
            for model in struct:
                for chain in model:
                    for res in chain:
                        if not is_aa(res, standard=True) if hasattr(res, 'get_resname') else True:
                            try:
                                rn = res.get_resname()
                                het_residues.append(rn)
                            except Exception:
                                pass
            from Bio.PDB.Polypeptide import is_aa
            het = []
            for model in struct:
                for chain in model:
                    for res in chain:
                        if not is_aa(res, standard=True):
                            try:
                                het.append(res.get_resname())
                            except Exception:
                                pass
            print(f"  HETATM resnames: {set(het)}")
        except Exception as e:
            print(f"  error: {e}")


if __name__ == "__main__":
    main()
