"""Stability backends (PRD FR5, Phase 1.6b)."""

from pathlib import Path

from psge.core.models import Config, StabilityResult, StructurePair
from psge.utils.variant_parse import variant_position


def get_stability_backend(backend: str):
    """Return stability backend. Phase 1.6b: FoldX when available and requested."""
    if backend == "foldx":
        try:
            from psge.backends.foldx.runner import detect_foldx
            if detect_foldx():
                return _foldx_stability
        except Exception:
            pass
    return _mock_stability


def _mock_stability(
    struct_pair: StructurePair,
    pos: int | None,
    config: Config,
    variant_parsed: str = "",
) -> StabilityResult:
    """
    Mock stability: return placeholder ΔΔG when FoldX unavailable.
    R152C, G358R are destabilizing per 04_VARIANT_PANEL; R59W is binding impairment.
    """
    if pos is None:
        return StabilityResult(ddg=0.0, flags=[], backend="mock")
    if pos in (152, 358):
        return StabilityResult(ddg=2.5, flags=["destabilizing"], backend="mock")
    if pos == 59:
        return StabilityResult(ddg=0.3, flags=[], backend="mock")  # R59W: modest
    return StabilityResult(ddg=0.0, flags=[], backend="mock")


def _foldx_stability(
    struct_pair: StructurePair,
    pos: int | None,
    config: Config,
    variant_parsed: str = "",
) -> StabilityResult:
    """FoldX stability: real ΔΔG when executable available."""
    from psge.backends.foldx.runner import compute_foldx_ddg

    cache_dir = Path(config.cache_dir) if config.cache_dir else None
    result, _version, _intermediates = compute_foldx_ddg(
        struct_pair, pos, variant_parsed, config, cache_dir
    )
    return result
