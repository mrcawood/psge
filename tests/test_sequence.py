"""Sequence stage tests (Sprint 3, 09_PLAN.md)."""

from psge.core.models import Config
from psge.pipeline.stages import preflight, sequence


def test_sequence_returns_pair_for_r59w():
    """Sequence stage returns WT + mutant for R59W (missense)."""
    config = Config(results_dir="/tmp")
    rec = preflight("R59W", config)
    pair = sequence(rec, config)
    assert pair is not None
    assert hasattr(pair, "wt_sequence")
    assert hasattr(pair, "mutant_sequence")
    assert len(pair.wt_sequence) > 0
    assert len(pair.mutant_sequence) == len(pair.wt_sequence)
    # R59W: position 59 (1-based) should be W instead of R
    assert pair.mutant_sequence[58] == "W"  # 0-based index 58
    assert pair.wt_sequence[58] == "R"


def test_sequence_skips_for_non_structural():
    """Sequence stage returns None for truncation/splice (non-structural)."""
    config = Config(results_dir="/tmp")
    rec = preflight("78insC", config)
    pair = sequence(rec, config)
    assert pair is None
