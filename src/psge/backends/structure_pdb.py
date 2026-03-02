"""PDB-first structure backend (Phase 1.5)."""

from pathlib import Path

from psge.core.models import Config, SequencePair, StructurePair
from psge.utils.pdb_fetch import PPOX_WT_PDB_ID, get_pdb_path


def _pdb_cache_base(config: Config, cache_dir: Path) -> Path:
    """Directory for cached PDB files."""
    if config.cache_dir:
        return Path(config.cache_dir) / "pdb"
    return cache_dir.parent.parent / "pdb"


def pdb_first_structure(
    seq_pair: SequencePair,
    config: Config,
    cache_dir: Path,
) -> StructurePair:
    """
    PDB-first: WT from 3NKS, mutant from prediction fallback.
    For PPOX, 3NKS is human PPOX with FAD and acifluorfen (ACJ).
    """
    pdb_base = _pdb_cache_base(config, cache_dir)
    wt_path = get_pdb_path(PPOX_WT_PDB_ID, pdb_base)
    # Mutant: predict (ESMFold or mock)
    mut_dir = cache_dir / "mutant"
    mut_dir.mkdir(parents=True, exist_ok=True)
    mut_pair = _predict_mutant(seq_pair, config, mut_dir)
    return StructurePair(
        wt_pdb_path=str(wt_path),
        mutant_pdb_path=mut_pair.mutant_pdb_path,
        backend="pdb",
    )


def _predict_mutant(seq_pair: SequencePair, config: Config, mut_dir: Path) -> StructurePair:
    """Get mutant structure via ESMFold or mock. Only mutant path is used (WT = 3NKS)."""
    try:
        from psge.backends.structure_esmfold import try_esmfold_predict
        result = try_esmfold_predict(seq_pair, config, mut_dir)
        if result is not None:
            return StructurePair(
                wt_pdb_path="",  # Not used; caller uses 3NKS for WT
                mutant_pdb_path=result.mutant_pdb_path,
                backend="esmfold",
            )
    except Exception:
        pass
    from psge.backends.structure import _mock_predict
    pair = _mock_predict(seq_pair, config, mut_dir)
    return StructurePair(wt_pdb_path="", mutant_pdb_path=pair.mutant_pdb_path, backend="mock")
