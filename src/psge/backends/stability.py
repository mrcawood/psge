"""Stability backends (PRD FR5)."""

from psge.core.models import Config, StabilityResult, StructurePair
from psge.utils.variant_parse import variant_position


def get_stability_backend(backend: str):
    """Return stability backend. M4: mock only (FoldX/Rosetta need external install)."""
    return _mock_stability


def _mock_stability(
    struct_pair: StructurePair,
    pos: int | None,
    config: Config,
) -> StabilityResult:
    """
    Mock stability: return placeholder ΔΔG.
    R152C, G358R are destabilizing per 04_VARIANT_PANEL; R59W is binding impairment.
    """
    if pos is None:
        return StabilityResult(ddg=0.0, flags=[])
    if pos in (152, 358):
        return StabilityResult(ddg=2.5, flags=["destabilizing"])
    if pos == 59:
        return StabilityResult(ddg=0.3, flags=[])  # R59W: modest, primarily binding
    return StabilityResult(ddg=0.0, flags=[])
