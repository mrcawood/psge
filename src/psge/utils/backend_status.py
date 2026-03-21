"""Backend status for reporting (M6a/M6b)."""


def get_backend_status(
    structure_backend: str | None = None,
    stability_backend: str | None = None,
    delta_metrics: str = "real_rmsd",
    sasa: str = "not_implemented",
    foldx_version: str | None = None,
) -> dict:
    """
    Return backend status for run_manifest and summary.
    M6b: real RMSD; structure_backend from StructurePair when provided.
    Phase 1.6: stability_backend from StabilityResult; sasa from SASA; foldx_version when FoldX used.
    """
    out = {
        "structure_backend": structure_backend or "mock",
        "stability_backend": stability_backend or "mock",
        "delta_metrics": delta_metrics,
        "sasa": sasa,
    }
    if foldx_version:
        out["foldx_version"] = foldx_version
    return out
