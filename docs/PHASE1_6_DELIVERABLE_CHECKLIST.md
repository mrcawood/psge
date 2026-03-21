# Phase 1.6 Deliverable Checklist

## Files Changed

### New Files
- `src/psge/utils/sasa.py` — BioPython Shrake-Rupley SASA computation
- `src/psge/backends/foldx/__init__.py` — FoldX package init
- `src/psge/backends/foldx/runner.py` — FoldX detection, BuildModel, ΔΔG parsing
- `src/psge/utils/pdb_distances.py` — `get_pdb_residue_for_foldx()` helper
- `tests/test_sasa.py` — SASA unit tests (3 tests)
- `tests/test_foldx.py` — FoldX parsing + skip-if-missing integration test
- `tests/fixtures/minimal.pdb` — Minimal PDB for SASA tests
- `tests/fixtures/foldx_dif_sample.fxout` — Sample FoldX Dif output for parsing test
- `docs/PHASE1_6_STATE_CAPTURE.md` — Pre-implementation state capture
- `docs/PHASE1_6_DELIVERABLE_CHECKLIST.md` — This file

### Modified Files
- `src/psge/core/models.py` — DeltaFeatures extended (SASA fields), StabilityResult (backend, foldx_version)
- `src/psge/backends/alignment.py` — Real SASA via sasa module, extended DeltaFeatures
- `src/psge/backends/stability.py` — FoldX backend when available, variant_parsed for mutation
- `src/psge/pipeline/stages.py` — stability passes variant_parsed; reporting passes delta
- `src/psge/pipeline/runner.py` — backend_status from actual backends (sasa, stability), foldx_version
- `src/psge/pipeline/mechanism.py` — folding_stability primary only when stability_backend is foldx
- `src/psge/utils/backend_status.py` — stability_backend, sasa, foldx_version params
- `src/psge/reporting/summary.py` — SASA evidence in summary/report when available
- `src/psge/utils/pdb_rmsd.py` — (unchanged; compute_sasa_delta remains placeholder for legacy)
- `data/testdata/variants/ppox_panel.yaml` — R152C/G358R expected_class → unknown_mechanism
- `data/testdata/variants/ppox_panel_expected.yaml` — Phase 1.6 expected outcomes
- `tests/test_panel_t2.py` — EXPECTED dict updated for mock-stability policy
- `docs/VALIDATION_SCIENCE.md` — Phase 1.6 metrics, FoldX, SASA, classifier policy

---

## How to Run

### Basic (pdb_first, SASA real, stability mock)
```bash
psge run --variant R59W --structure-source pdb_first --results-dir results/
psge run --variant I12T --structure-source pdb_first --results-dir results/
```

### With FoldX (when installed)
```bash
# Ensure FoldX is on PATH or set FOLDX_PATH
export FOLDX_PATH=/path/to/foldx  # optional
psge run --variant R59W --structure-source pdb_first --results-dir results/
# stability_backend in config defaults to foldx; will use FoldX if executable found
```

---

## Example summary.json Evidence (SASA and ΔΔG)

### R59W (pdb_first, SASA real)
```json
{
  "evidence_table": [
    {"signal": "min_dist_to_fad_atoms_angstrom", "value": 4.87},
    {"signal": "sasa_total_wt", "value": 18696.75},
    {"signal": "sasa_total_mut", "value": 457.69},
    {"signal": "delta_sasa_total", "value": -18239.06},
    {"signal": "sasa_patch_8A", "value": 0.0},
    {"signal": "sasa_mapping_status", "value": "mapped"}
  ],
  "backend_status": {
    "structure_backend": "pdb",
    "stability_backend": "mock",
    "sasa": "biopython_shrake_rupley"
  },
  "sasa": {
    "sasa_total_wt": 18696.75,
    "sasa_total_mut": 457.69,
    "delta_sasa_total": -18239.06,
    "sasa_patch_8A": 0.0,
    "sasa_mapping_status": "mapped"
  }
}
```

### I12T (pdb_first, SASA real)
```json
{
  "evidence_table": [
    {"signal": "in_targeting_region", "value": true},
    {"signal": "sasa_total_wt", "value": 18696.75},
    {"signal": "sasa_total_mut", "value": 457.69},
    {"signal": "delta_sasa_total", "value": -18239.06},
    {"signal": "sasa_patch_8A", "value": 3.62},
    {"signal": "sasa_mapping_status", "value": "mapped"}
  ],
  "backend_status": {
    "structure_backend": "pdb",
    "stability_backend": "mock",
    "sasa": "biopython_shrake_rupley"
  }
}
```

### With FoldX (when available)
```json
{
  "backend_status": {
    "structure_backend": "pdb",
    "stability_backend": "foldx",
    "foldx_version": "5.0",
    "sasa": "biopython_shrake_rupley"
  }
}
```
Evidence table would include `{"signal": "ddg", "value": <real ΔΔG>}` when folding_stability fires.

---

## Test Results

```
30 passed, 1 skipped in ~32s
```

- **SASA:** `test_sasa_total_returns_non_null_for_known_structure`, `test_sasa_identical_inputs_delta_near_zero`, `test_sasa_residue_returns_for_mapped_position`
- **FoldX:** `test_parse_dif_fxout` (fixture), `test_foldx_integration_skip_if_missing` (skipped when FoldX not installed)
- **Panel:** `test_panel_t2_assertions` — R152C/G358R → unknown_mechanism (mock stability)

---

## Mutant Structure Approach (Resolved)

**Approach B:** Use experimental 3NKS (WT) directly. FoldX BuildModel takes WT PDB + mutation list (e.g. `RA59W`). FoldX applies the mutation internally. No pre-built mutant structure needed for stability.

- **Chain selection:** First chain in first model (3NKS chain A)
- **Residue mapping:** UniProt 1-based → PDB residue ID via `_build_uniprot_to_pdb_map` (sequence alignment)
- **Missing residue:** Returns `StabilityResult(backend="mock")` when mapping fails
- **Heteroatoms (FAD, ACJ):** Present in 3NKS; context mapping uses them; FoldX typically ignores non-protein for BuildModel
