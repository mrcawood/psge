"""Backend status for reporting (M6a/M6b)."""


def get_backend_status(
    structure_backend: str | None = None,
    delta_metrics: str = "real_rmsd",
    sasa: str = "not_implemented",
) -> dict:
    """
    Return backend status for run_manifest and summary.
    M6b: real RMSD; structure_backend from StructurePair when provided.
    SASA and stability remain not implemented / mock.
    """
    return {
        "structure_backend": structure_backend or "mock",
        "stability_backend": "mock",
        "delta_metrics": delta_metrics,
        "sasa": sasa,
    }
