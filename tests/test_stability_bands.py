"""Stability band policy tests (Phase 1.6d)."""

from psge.utils.stability_bands import (
    qualifies_folding_primary,
    qualifies_folding_secondary,
    stability_signal_band,
)


def test_stability_signal_bands():
    assert stability_signal_band(0.5) == "none_or_weak"
    assert stability_signal_band(1.5) == "weak_to_moderate"
    assert stability_signal_band(2.02) == "borderline_destabilizing"
    assert stability_signal_band(3.0) == "destabilizing"
    assert stability_signal_band(7.0) == "strong_destabilizing"
    assert stability_signal_band(15.0) == "extreme_destabilizing_requires_audit"


def test_borderline_not_primary_without_audit():
    assert not qualifies_folding_primary("borderline_destabilizing", True)
    assert qualifies_folding_secondary("borderline_destabilizing")


def test_extreme_requires_audit_for_primary():
    assert not qualifies_folding_primary("extreme_destabilizing_requires_audit", False)
    assert qualifies_folding_primary("extreme_destabilizing_requires_audit", True)
