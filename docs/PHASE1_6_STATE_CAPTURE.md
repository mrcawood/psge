# Phase 1.6 State Capture (Pre-Implementation)

## 0. Current Schemas

### ContextFeatures (src/psge/core/models.py)
```python
@dataclass
class ContextFeatures:
    min_dist_to_fad_atoms_angstrom: float | None = None
    min_dist_to_inhibitor_atoms_angstrom: float | None = None
    min_dist_to_active_site_residue_atoms_angstrom_excl_self: float | None = None
    is_in_fad_residue_set: bool = False
    is_in_active_site_residue_set: bool = False
    distance_fad: float | None = None
    distance_active_site: float | None = None
    in_targeting_region: bool = False
    in_membrane_region: bool = False
    n_terminal_targeting_signal_end: int | None = None
```

### StabilityResult (src/psge/core/models.py)
```python
@dataclass
class StabilityResult:
    ddg: float
    flags: list[str]
```
No `backend` field yet.

### DeltaFeatures (src/psge/core/models.py)
```python
@dataclass
class DeltaFeatures:
    global_rmsd: float
    local_rmsd: float
    sasa_delta: float
    contact_deltas: dict
```

### run_manifest.json keys
- `timestamp`, `input`, `input_hash`, `config_hash`, `compute_profile`
- `backend_status`: `structure_backend`, `stability_backend`, `delta_metrics`, `sasa`
- `mechanism_thresholds`: `contact_threshold_angstrom`, `near_threshold_angstrom`

---

## Where Stability and SASA Are Produced

| Metric | Stage | Module | Current Output |
|--------|-------|--------|----------------|
| Stability (ΔΔG) | `stages.stability` | `backends/stability.py` | `_mock_stability`: R152C/G358R→2.5, R59W→0.3, else 0.0 |
| SASA | `stages.alignment_delta` → `compute_delta` | `backends/alignment.py` → `utils/pdb_rmsd.py` | `compute_sasa_delta` returns 0.0 (placeholder) |

---

## Structure Inputs

- **PDB-first WT:** 3NKS (human PPOX + FAD + ACJ). Path from `pdb_fetch.get_pdb_path(PPOX_WT_PDB_ID, pdb_base)`.
- **Mutant structure:** ESMFold prediction or mock. **NOT** applied mutation to PDB. Mutant is generated via `_predict_mutant()` in `structure_pdb.py` (ESMFold or `_mock_predict`).
- **Residue mapping:** `pdb_distances._build_uniprot_to_pdb_map()` aligns UniProt sequence to PDB chain sequence; UniProt 1-based pos → (chain_id, res). PDB residue ID = `res.id[1]`.
- **Chain selection:** First chain in first model (3NKS typically chain A).
- **Heteroatoms:** FAD, ACJ (acifluorfen) present in 3NKS; context mapping extracts them via `extract_ligand_atoms(structure, resname)`.

---

## Mutant Structure for FoldX

**Approach B (preferred):** Use experimental 3NKS (WT) directly. FoldX BuildModel takes:
- WT PDB path
- Mutation list (format: `WTaa+Chain+PDBresnum+Mutaa`, e.g. `RA59W`)

FoldX applies the mutation internally and outputs ΔΔG. No pre-built mutant structure needed.

**Tradeoffs:**
- **B (PDB WT + FoldX mutation):** Uses experimental structure; FoldX handles in-silico mutation. Requires UniProt→PDB residue mapping.
- **A (predicted mutant):** Would use ESMFold mutant; less accurate for stability (predicted structure ≠ FoldX's internal mutant model).
