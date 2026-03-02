"""Structure prediction backends (PRD FR3, M6b)."""

from pathlib import Path

from psge.core.models import Config, SequencePair, StructurePair


def get_structure_backend(backend: str):
    """Return backend callable. Uses ESMFold if available and requested, else mock."""
    if backend in ("alphafold", "esmfold"):
        return _predict_with_fallback
    return _mock_predict


def _predict_with_fallback(seq_pair: SequencePair, config: Config, cache_dir: Path) -> StructurePair:
    """Try ESMFold first, fall back to mock."""
    try:
        from psge.backends.structure_esmfold import try_esmfold_predict
        result = try_esmfold_predict(seq_pair, config, cache_dir)
        if result is not None:
            return result
    except Exception:
        pass
    return _mock_predict(seq_pair, config, cache_dir)


def _mock_predict(seq_pair: SequencePair, config: Config, cache_dir: Path) -> StructurePair:
    """
    Mock structure prediction: write minimal placeholder PDBs.
    Used when AlphaFold/ESMFold not available (09_PLAN: mock for CI).
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    wt_path = cache_dir / "wt.pdb"
    mut_path = cache_dir / "mutant.pdb"
    _write_minimal_pdb(wt_path, seq_pair.wt_sequence)
    _write_minimal_pdb(mut_path, seq_pair.mutant_sequence)
    return StructurePair(
        wt_pdb_path=str(wt_path),
        mutant_pdb_path=str(mut_path),
        backend="mock",
    )


def _write_minimal_pdb(path: Path, sequence: str) -> None:
    """Write minimal valid PDB with CA trace."""
    lines = ["REMARK PSGE mock structure", "MODEL 1"]
    for i, aa in enumerate(sequence[:10], start=1):  # First 10 residues only for minimal
        x, y, z = float(i * 2), 0.0, 0.0
        lines.append(f"ATOM  {i:5d}  CA  {aa} A{i:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C")
    lines.extend(["ENDMDL", "END"])
    path.write_text("\n".join(lines))
