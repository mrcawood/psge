"""Preflight tests (Sprint 2, 09_PLAN.md, T1)."""

from psge.core.models import Config
from psge.pipeline.stages import preflight


def _config():
    return Config(results_dir="/tmp")


def test_preflight_r59w_structural():
    """R59W → track=structural (missense)."""
    rec = preflight("R59W", _config())
    assert rec.type == "missense"
    assert rec.track == "structural"


def test_preflight_78insc_non_structural():
    """78insC → track=non_structural (truncation/frameshift)."""
    rec = preflight("78insC", _config())
    assert rec.type == "truncation"
    assert rec.track == "non_structural"


def test_preflight_ivs2_non_structural():
    """IVS2-2 a→c → track=non_structural (splice)."""
    rec = preflight("IVS2-2 a→c", _config())
    assert rec.type == "splice"
    assert rec.track == "non_structural"


def test_preflight_i12t_structural():
    """I12T → track=structural (missense)."""
    rec = preflight("I12T", _config())
    assert rec.type == "missense"
    assert rec.track == "structural"


def test_preflight_r152c_structural():
    """R152C → structural (missense)."""
    rec = preflight("R152C", _config())
    assert rec.type == "missense"
    assert rec.track == "structural"


def test_preflight_g358r_structural():
    """G358R → structural (missense)."""
    rec = preflight("G358R", _config())
    assert rec.type == "missense"
    assert rec.track == "structural"
