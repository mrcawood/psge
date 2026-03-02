"""ESMFold structure backend (M6b, optional)."""

from pathlib import Path

from psge.core.models import Config, SequencePair, StructurePair


def try_esmfold_predict(
    seq_pair: SequencePair,
    config: Config,
    cache_dir: Path,
) -> StructurePair | None:
    """
    Run ESMFold if available. Returns None to fall back to mock.
    Requires: pip install "fair-esm[esmfold]"
    """
    try:
        import torch
        esmfold = _load_esmfold()
    except ImportError:
        return None
    cache_dir.mkdir(parents=True, exist_ok=True)
    wt_path = cache_dir / "wt_esmfold.pdb"
    mut_path = cache_dir / "mutant_esmfold.pdb"
    if not _predict_and_save(esmfold, seq_pair.wt_sequence, wt_path):
        return None
    if not _predict_and_save(esmfold, seq_pair.mutant_sequence, mut_path):
        return None
    return StructurePair(
        wt_pdb_path=str(wt_path),
        mutant_pdb_path=str(mut_path),
        backend="esmfold",
    )


def _load_esmfold():
    import esm
    model, alphabet = esm.pretrained.esmfold_v1()
    model.eval()
    return model


def _predict_and_save(model, sequence: str, out_path: Path) -> bool:
    try:
        import torch
        with torch.no_grad():
            output = model.infer_pdb(sequence)
        if output:
            out_path.write_text(output)
            return True
    except Exception:
        pass
    return False
