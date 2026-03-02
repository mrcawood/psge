"""Stability, context mapping, alignment/delta tests (Sprint 4, 09_PLAN.md)."""

from psge.core.models import Config
from psge.pipeline.stages import (
    alignment_delta,
    context_mapping,
    preflight,
    sequence,
    stability,
    structure,
)


def test_stability_returns_ddg(tmp_path):
    """Stability stage returns StabilityResult with ddg, flags."""
    config = Config(results_dir=str(tmp_path / "results"), cache_dir=str(tmp_path / "cache"))
    rec = preflight("R59W", config)
    seq_pair = sequence(rec, config)
    struct_pair = structure(rec, seq_pair, config)
    assert struct_pair is not None

    result = stability(rec, struct_pair, config)
    assert result is not None
    assert hasattr(result, "ddg")
    assert hasattr(result, "flags")
    assert isinstance(result.ddg, (int, float))


def test_context_returns_features(tmp_path):
    """Context mapping returns ContextFeatures with distance/site flags."""
    config = Config(results_dir=str(tmp_path / "results"), cache_dir=str(tmp_path / "cache"))
    rec = preflight("R59W", config)
    seq_pair = sequence(rec, config)
    struct_pair = structure(rec, seq_pair, config)
    assert struct_pair is not None

    features = context_mapping(rec, struct_pair, config)
    assert features is not None
    assert hasattr(features, "distance_fad") or hasattr(features, "in_targeting_region")
    assert hasattr(features, "in_targeting_region")


def test_context_i12t_in_targeting_region(tmp_path):
    """I12T (position 12) is in mitochondrial targeting region."""
    config = Config(results_dir=str(tmp_path / "results"), cache_dir=str(tmp_path / "cache"))
    rec = preflight("I12T", config)
    seq_pair = sequence(rec, config)
    struct_pair = structure(rec, seq_pair, config)
    assert struct_pair is not None

    features = context_mapping(rec, struct_pair, config)
    assert features is not None
    assert features.in_targeting_region is True


def test_stability_skips_for_non_structural():
    """Stability returns None when no structure (non-structural track)."""
    config = Config(results_dir="/tmp")
    rec = preflight("78insC", config)
    result = stability(rec, None, config)
    assert result is None


def test_context_skips_for_non_structural():
    """Context mapping returns None when no structure."""
    config = Config(results_dir="/tmp")
    rec = preflight("78insC", config)
    features = context_mapping(rec, None, config)
    assert features is None


def test_alignment_delta_returns_features(tmp_path):
    """Alignment/delta stage returns DeltaFeatures."""
    config = Config(results_dir=str(tmp_path / "results"), cache_dir=str(tmp_path / "cache"))
    rec = preflight("R59W", config)
    seq_pair = sequence(rec, config)
    struct_pair = structure(rec, seq_pair, config)
    assert struct_pair is not None

    delta = alignment_delta(rec, struct_pair, config)
    assert delta is not None
    assert hasattr(delta, "global_rmsd")
    assert hasattr(delta, "local_rmsd")
