"""FoldX ΔΔG threshold bands (Phase 1.6d; provisional)."""


def stability_signal_band(ddg: float) -> str:
    """Map FoldX ΔΔG (kcal/mol) to a stability signal band."""
    if ddg < 1.0:
        return "none_or_weak"
    if ddg < 2.0:
        return "weak_to_moderate"
    if ddg < 2.5:
        return "borderline_destabilizing"
    if ddg < 5.0:
        return "destabilizing"
    if ddg < 10.0:
        return "strong_destabilizing"
    return "extreme_destabilizing_requires_audit"


def qualifies_folding_primary(band: str | None, audit_passed: bool = False) -> bool:
    """True when band supports primary folding_stability_hydrophobic_core."""
    if not band:
        return False
    if band in ("destabilizing", "strong_destabilizing"):
        return True
    if band == "extreme_destabilizing_requires_audit":
        return audit_passed
    return False


def qualifies_folding_secondary(band: str | None) -> bool:
    """True when stability may appear as secondary hypothesis or evidence note."""
    if not band:
        return False
    return band in (
        "weak_to_moderate",
        "borderline_destabilizing",
        "destabilizing",
        "strong_destabilizing",
        "extreme_destabilizing_requires_audit",
    )


BAND_ORDER = [
    "none_or_weak",
    "weak_to_moderate",
    "borderline_destabilizing",
    "destabilizing",
    "strong_destabilizing",
    "extreme_destabilizing_requires_audit",
]
