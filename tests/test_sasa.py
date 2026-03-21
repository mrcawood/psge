"""SASA unit tests (Phase 1.6a)."""

from pathlib import Path

import pytest

from psge.core.models import StructurePair
from psge.utils.sasa import (
    compute_sasa_local,
    compute_sasa_residue,
    compute_sasa_total,
)


FIXTURES = Path(__file__).parent / "fixtures"
MINIMAL_PDB = FIXTURES / "minimal.pdb"


def test_sasa_total_returns_non_null_for_known_structure():
    """SASA runs and returns non-null for a known structure."""
    if not MINIMAL_PDB.exists():
        pytest.skip("fixtures/minimal.pdb not found")
    result = compute_sasa_total(MINIMAL_PDB)
    assert result is not None
    assert isinstance(result, (int, float))
    assert result > 0


def test_sasa_identical_inputs_delta_near_zero():
    """For identical WT and mutant (same structure), delta_sasa_residue ~ 0 (sanity)."""
    if not MINIMAL_PDB.exists():
        pytest.skip("fixtures/minimal.pdb not found")
    struct_pair = StructurePair(
        wt_pdb_path=str(MINIMAL_PDB),
        mutant_pdb_path=str(MINIMAL_PDB),
        backend="mock",
    )
    result = compute_sasa_local(
        MINIMAL_PDB,
        MINIMAL_PDB,
        variant_position=1,
        uniprot_seq="AGI",
        struct_pair=struct_pair,
        n_points=100,
    )
    sasa_res_wt, sasa_res_mut, delta_res, patch, mapping_status, pairing = result
    assert delta_res is not None, "same_backend (mock) should produce delta_sasa_residue"
    assert 1 in delta_res
    assert abs(delta_res[1]) < 0.01, "identical structures -> delta ~ 0"


def test_sasa_residue_returns_for_mapped_position():
    """SASA residue returns value when position maps to structure."""
    if not MINIMAL_PDB.exists():
        pytest.skip("fixtures/minimal.pdb not found")
    result = compute_sasa_residue(MINIMAL_PDB, 1, "AGI", n_points=100)
    assert result is not None
    assert result >= 0


def test_sasa_sanity_single_mutation_delta_bounded():
    """
    Sanity: when structures are comparable, delta_sasa_residue for single
    missense should not exceed plausible threshold (~500 Å²).
    """
    if not MINIMAL_PDB.exists():
        pytest.skip("fixtures/minimal.pdb not found")
    struct_pair = StructurePair(
        wt_pdb_path=str(MINIMAL_PDB),
        mutant_pdb_path=str(MINIMAL_PDB),
        backend="mock",
    )
    result = compute_sasa_local(
        MINIMAL_PDB,
        MINIMAL_PDB,
        variant_position=1,
        uniprot_seq="AGI",
        struct_pair=struct_pair,
        n_points=100,
    )
    _, _, delta_res, _, _, _ = result
    if delta_res:
        for pos, val in delta_res.items():
            assert abs(val) < 500, (
                f"Single-residue SASA delta {val} at pos {pos} exceeds sanity threshold 500 Å². "
                "Likely comparing incompatible structures (e.g. full PDB vs mock)."
            )
