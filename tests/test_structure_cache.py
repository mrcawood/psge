"""Structure cache tests (Sprint 3, 09_PLAN.md)."""

from pathlib import Path

from psge.core.models import Config
from psge.pipeline.stages import preflight, sequence, structure


def test_cache_hit(tmp_path):
    """Second run reuses structure (cache hit)."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    config = Config(results_dir=str(tmp_path / "results"), cache_dir=str(cache_dir))
    rec = preflight("R59W", config)
    seq_pair = sequence(rec, config)
    assert seq_pair is not None

    struct1 = structure(rec, seq_pair, config)
    assert struct1 is not None
    assert struct1.wt_pdb_path
    assert struct1.mutant_pdb_path
    path1 = struct1.wt_pdb_path

    struct2 = structure(rec, seq_pair, config)
    assert struct2 is not None
    assert struct2.wt_pdb_path == path1  # Same path = cache hit
