"""FoldX tests (Phase 1.6b)."""

from pathlib import Path

import pytest

from psge.backends.foldx.runner import _parse_dif_fxout, detect_foldx

FIXTURES = Path(__file__).parent / "fixtures"
FOLDX_DIF_SAMPLE = FIXTURES / "foldx_dif_sample.fxout"
FOLDX_DIF_REPAIR = FIXTURES / "foldx_dif_repair.fxout"


def test_parse_dif_fxout():
    """Parsing unit test using stored sample FoldX output fixture."""
    if not FOLDX_DIF_SAMPLE.exists():
        pytest.skip("fixtures/foldx_dif_sample.fxout not found")
    ddg = _parse_dif_fxout(FOLDX_DIF_SAMPLE)
    assert ddg is not None
    assert abs(ddg - 1.23) < 0.01


def test_parse_dif_fxout_foldx5_banner():
    """Parse real FoldX 5.x Dif output with header banner lines."""
    if not FOLDX_DIF_REPAIR.exists():
        pytest.skip("fixtures/foldx_dif_repair.fxout not found")
    ddg = _parse_dif_fxout(FOLDX_DIF_REPAIR)
    assert ddg is not None
    assert abs(ddg - 2.02263) < 0.0001


def test_parse_dif_fxout_missing_file():
    """Parse returns None for missing file."""
    ddg = _parse_dif_fxout(Path("/nonexistent/file.fxout"))
    assert ddg is None


@pytest.mark.skipif(not detect_foldx(), reason="FoldX not installed")
def test_foldx_integration_skip_if_missing(tmp_path):
    """Integration test: skip if FoldX missing. Runs when FoldX is available."""
    from psge.backends.foldx.runner import compute_foldx_ddg
    from psge.core.models import Config, StructurePair

    # Use 3NKS if available
    pdb_path = Path(__file__).parent.parent / "data" / "public" / "structures" / "pdb" / "3NKS.cif"
    if not pdb_path.exists():
        pytest.skip("3NKS.cif not found")
    config = Config(results_dir=str(tmp_path), gene="PPOX")
    struct = StructurePair(
        wt_pdb_path=str(pdb_path),
        mutant_pdb_path=str(pdb_path),  # Not used by FoldX
        backend="pdb",
    )
    result, version, intermediates = compute_foldx_ddg(
        struct, 59, "R59W", config, cache_dir=str(tmp_path / "cache")
    )
    assert result.backend in ("foldx", "mock")
    if result.backend == "foldx":
        assert isinstance(result.ddg, (int, float))
