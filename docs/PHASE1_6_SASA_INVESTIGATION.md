# Phase 1.6 SASA Investigation Report

## 1. R59W Run – Paths and Structure Details

### WT structure
- **Path:** `{cache_base}/pdb/3NKS.cif` (from `pdb_fetch.get_pdb_path`)
- **Atoms (protein, standard AA):** 3460
- **Residues (standard AA):** 465
- **Chain IDs:** A
- **Heteroatoms:** FAD, ACJ (acifluorfen) present in 3NKS

### Mutant structure
- **Path:** `{cache_base}/{hash}/mutant/mutant.pdb`
- **Source:** `_predict_mutant()` → ESMFold or `_mock_predict`
- **Mock case:** 10 residues only, single-letter AA codes (M, G, R) instead of 3-letter (MET, GLY, ARG)
- **Atoms (protein, standard AA):** 0 (mock uses invalid PDB residue names; `is_aa(res, standard=True)` filters all)
- **Residues (standard AA):** 0
- **Chain ID:** space `' '` in mock output

### Root cause
- WT: full 3NKS (~477 residues, experimental)
- Mutant: mock with 10 residues and invalid residue names
- ShrakeRupley still ran on the mutant and produced ~457 Å² from 10 CA atoms
- Global totals were therefore comparing full protein vs tiny mock → impossible delta of -18239 Å²

## 2. Why sasa_patch_8A Was 0.0

Patch SASA is computed on the WT structure only. For 3NKS, residue 59 should map and have neighbors within 8 Å. A value of 0.0 is unexpected and may indicate:
- Patch selection or distance logic failing
- Chain/model selection issues with mmCIF
- Residue SASA not being attached correctly

**Fix:** Patch computation now returns `(value, status)`. If `patch_sasa == 0.0` but `n_in_patch > 0` and `center_sasa > 0`, we return `(None, "patch_zero_suspicious")` instead of reporting 0.0.

## 3. Corrected Approach (Option A)

**Design:** SASA is local-only; no global totals.

- **Compute:** Residue SASA at the mutation site (WT and mutant) and 8 Å patch SASA (WT only).
- **Do not compute:** `sasa_total_wt`, `sasa_total_mut`, `delta_sasa_total`.
- **Same-backend guard:** `delta_sasa_residue` is only computed when both structures come from the same backend (both ESMFold or both mock). When `backend == "pdb"`, WT is experimental and mutant is predicted → not comparable → `delta_sasa_residue = None`.
- **Atom selection:** Protein standard AAs only (excludes HETATMs) for consistency.
- **Patch validation:** If patch is 0.0 but center has SASA and neighbors exist, return null with status instead of 0.0.

## 4. Sanity Test

Added `test_sasa_sanity_single_mutation_delta_bounded`: when structures are comparable and identical, `delta_sasa_residue` must be ~0; when different but comparable, `abs(delta_sasa_residue[pos]) < 500` Å². This would fail if we compared full PDB to mock.
