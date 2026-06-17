"""FoldX audit helpers (Phase 1.6d)."""

from __future__ import annotations

import re
from pathlib import Path

from psge.utils.stability_bands import stability_signal_band


def audit_foldx_run(
    *,
    variant_parsed: str,
    uniprot_pos: int,
    chain_id: str,
    pdb_resnum: int,
    wt_aa: str,
    mutation_foldx: str,
    ddg: float | None,
    dif_path: Path | None,
    repaired_pdb_path: Path | None,
    mutant_glob: list[Path],
) -> tuple[bool, list[str]]:
    """
    Validate FoldX run for extreme or primary-classification use.
    Returns (audit_passed, list of check notes).
    """
    notes: list[str] = []
    passed = True

    m = re.match(r"^([A-Z])(\d+)([A-Z])$", variant_parsed.strip(), re.I)
    if not m:
        notes.append("variant_parse: failed")
        return False, notes
    v_wt, v_pos, v_mut = m.groups()
    v_pos = int(v_pos)
    if v_pos != uniprot_pos:
        notes.append(f"uniprot_position: mismatch {v_pos} vs {uniprot_pos}")
        passed = False
    else:
        notes.append("uniprot_position: exact")

    expected_mut = f"{wt_aa.upper()}{chain_id}{pdb_resnum}{v_mut.upper()}"
    if mutation_foldx != expected_mut:
        notes.append(f"foldx_mutation_string: expected {expected_mut}, got {mutation_foldx}")
        passed = False
    else:
        notes.append("foldx_mutation_string: valid")

    if repaired_pdb_path and repaired_pdb_path.exists():
        notes.append("repair_pdb: completed")
    else:
        notes.append("repair_pdb: missing")
        passed = False

    if ddg is None:
        notes.append("ddg_parse: failed")
        passed = False
    else:
        notes.append(f"ddg_parse: ok ({ddg:.5f})")

    if dif_path and dif_path.exists():
        notes.append(f"dif_output: {dif_path.name}")
    else:
        notes.append("dif_output: missing")
        passed = False

    if mutant_glob:
        notes.append(f"mutant_model: {mutant_glob[0].name}")
    else:
        notes.append("mutant_model: not found")

    band = stability_signal_band(ddg) if ddg is not None else None
    if band == "extreme_destabilizing_requires_audit" and ddg is not None and ddg > 50:
        notes.append("ddg_magnitude: unusually large; manual review recommended")

    return passed, notes


def build_foldx_provenance(
    *,
    wt_path: Path,
    structure_source: str,
    chain_id: str,
    uniprot_pos: int,
    pdb_resnum: int,
    mapping_status: str,
    mutation_foldx: str,
    foldx_version: str | None,
    foldx_status: str,
    repaired_pdb_path: Path | None,
    dif_path: Path | None,
    mutant_paths: list[Path],
    ddg: float | None,
    audit_passed: bool | None,
    audit_notes: list[str],
) -> dict:
    pdb_id = wt_path.stem.upper()
    band = stability_signal_band(ddg) if ddg is not None else None
    return {
        "pdb_id": pdb_id,
        "structure_source": structure_source,
        "chain_id": chain_id,
        "uniprot_position": uniprot_pos,
        "pdb_residue_id": pdb_resnum,
        "mapping_status": mapping_status,
        "foldx_mutation_string": mutation_foldx,
        "foldx_version": foldx_version,
        "foldx_status": foldx_status,
        "repair_pdb_used": repaired_pdb_path is not None and repaired_pdb_path.exists(),
        "foldx_input_policy": "protein_only_repaired_pdb",
        "ligands_included_for_foldx": False,
        "protein_only_for_foldx": True,
        "repaired_pdb_path": str(repaired_pdb_path) if repaired_pdb_path else None,
        "raw_foldx_output_path": str(dif_path) if dif_path else None,
        "mutant_model_path": str(mutant_paths[0]) if mutant_paths else None,
        "stability_signal_band": band,
        "audit_passed": audit_passed,
        "audit_notes": audit_notes,
        "ddg_kcal_mol": round(ddg, 5) if ddg is not None else None,
    }
