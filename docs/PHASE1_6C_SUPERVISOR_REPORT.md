# PSGE Phase 1.6c Supervisor Report

**Date:** 2026-06-17  
**Worker scope:** Real FoldX validation and stability grounding (Phase 1.6c)  
**Host:** talos  
**Structure source:** pdb_first (3NKS)

---

## 1. Executive summary

Phase 1.6c is complete. FoldX 5.1 is installed locally (not in git), wired through PSGE via `foldx_path` in `configs/default.yaml`, and validated on the full PPOX panel. Real ΔΔG values now flow into `summary.json` and `report.md` with `stability_backend: foldx` and `foldx_version` in `run_manifest.json`.

The pipeline remains conservative: mock stability never drives primary `folding_stability_hydrophobic_core`; FoldX runs only on experimental PDB WT (`structure_backend == pdb`); failures surface as `foldx_failed`, not silent mock fallback.

---

## 2. Environment

| Item | Value |
|------|-------|
| OS | Linux (talos) |
| FoldX package | `foldX/foldx_Linux_1.zip` (labeled 5.1) |
| Executable | `foldX/foldx_20270131` (project-relative in config) |
| Reported version | `5` (FoldX banner) |
| WT reference | 3NKS (human PPOX + FAD + ACJ) |
| Workflow | CIF→PDB, RepairPDB (cached), BuildModel, parse `Dif_*.fxout` |

FoldX binary and zips are gitignored. License material must not be committed or redistributed.

---

## 3. Code changes (this checkpoint)

### FoldX runner (`src/psge/backends/foldx/runner.py`)

- Fixed `Dif_*.fxout` parser for FoldX 5.x banner lines before the tab header.
- Added RepairPDB step with per-structure cache under `data/public/structures/cache/foldx/repair/`.
- Fixed default cache path (was incorrectly under `src/data/`).
- Returns `foldx_failed` on mapping or run failure instead of mock.
- Reads `config.foldx_path` before `FOLDX_PATH` env / PATH.

### Stability backend (`src/psge/backends/stability.py`)

- FoldX only when `structure_backend == "pdb"` so `predict_first` tests and mock structures do not invoke FoldX when the binary is present.

### Config (`configs/default.yaml`, `Config`, `load_config`)

- Added `foldx_path: foldX/foldx_20270131` (resolved relative to project root).

### Reporting (`src/psge/reporting/summary.py`)

- Emits FoldX ΔΔG in evidence even when stability is not the primary mechanism driver (e.g. R152C below threshold).

### Classifier (`mechanism.py`)

- Treats `foldx_failed` like mock for primary folding classification.

### Tests

- Added `tests/fixtures/foldx_dif_repair.fxout` for real FoldX 5 output format.
- Integration test runs when FoldX is detectable.

---

## 4. Validation

```text
pytest: 33 passed, 1 skipped (FoldX integration when unavailable)
```

Panel command:

```bash
psge run --panel data/testdata/variants/ppox_panel.yaml \
  --structure-source pdb_first --results-dir results/foldx_panel
```

Example single variant (default config):

```bash
psge run --variant R59W --structure-source pdb_first --results-dir results
```

---

## 5. Panel results (real FoldX, pdb_first)

| Variant | mapping | foldx_status | ΔΔG (kcal/mol) | Primary | Secondary | Confidence |
|---------|---------|--------------|----------------|---------|-----------|------------|
| R59W | exact (A59) | foldx | 2.02 | cofactor_binding_perturbation | folding_stability_hydrophobic_core | plausible |
| I12T | exact (A12) | foldx | 3.78 | folding_stability_hydrophobic_core | targeting, cofactor | plausible |
| R152C | exact (A152) | foldx | 1.68 | unknown_mechanism | — | low |
| G358R | exact (A358) | foldx | 15.29 | folding_stability_hydrophobic_core | — | plausible |
| 78insC | n/a | skipped | — | truncation_misexpression | — | plausible |
| IVS2-2 a→c | n/a | skipped | — | truncation_misexpression | — | plausible |

Outputs: `results/foldx_panel/<variant>/` (local, gitignored).

---

## 6. Interpretation notes (for supervisor review)

**R59W.** Cofactor proximity remains primary per rule precedence. FoldX ΔΔG 2.02 kcal/mol is at the provisional ≥2.0 threshold; folding appears as secondary only. Consistent with handover intent: proximity evidence does not imply functional causation.

**I12T.** Real ΔΔG 3.78 drives `folding_stability_hydrophobic_core` as primary. This differs from pre-FoldX panel expectations (`unknown_mechanism` primary with targeting secondary). Per handover: do not overfit labels to expected outcomes; record raw ΔΔG and let rules fire. Targeting and cofactor proximity remain evidence-gated secondaries.

**R152C.** ΔΔG 1.68 is below the 2.0 kcal/mol provisional threshold. Primary is `unknown_mechanism` despite literature framing as destabilizing. Worth supervisor judgment on threshold bands, not forced relabeling.

**G358R.** Strong destabilization signal (15.29 kcal/mol). Primary folding class is expected and defensible.

**Truncation/splice.** FoldX skipped cleanly; no crash.

---

## 7. Example evidence (R59W, `results/report.md`)

- `stability_backend: foldx`, `foldx_version: 5`
- `ddg: 2.02263`, `flags: ['destabilizing']`
- Cofactor distances unchanged from Phase 1.5 (FAD 4.87 Å, inhibitor 8.41 Å)
- SASA local-only; `sasa_source_pairing: incomparable` (WT PDB vs predicted mutant)

---

## 8. Open items (unchanged from Phase 1.6 handover)

1. Evidence tiering schema (`evidence_tier`, `species_context`, structured `sources`) — §16 of worker handover; deferred post-FoldX.
2. Pete-endorsed FAD/active-site residue lists — still provisional.
3. ΔΔG threshold bands — provisional; R152C and R59W borderline cases need human review.
4. Stale docs (`M7_PETE_OVERVIEW.md`, `OUTPUT_SCHEMA.md`, panel examples with pre-SASA-fix global totals) — not updated in this checkpoint.
5. M7 milestone checkbox in `PROGRESS.md` — process bookkeeping only.

---

## 9. Recommendation

FoldX is ready as a real stability evidence source for `pdb_first` PPOX runs on 3NKS. Safe next steps for the supervisor:

1. Review panel table above, especially I12T primary shift and R152C below-threshold ΔΔG.
2. Decide whether to adjust ΔΔG bands or keep raw values with conservative classification.
3. Package `results/foldx_panel/` reports for Pete after evidence-tier fields are added (or with explicit `pdb_context_only` disclaimer in cover note).
4. Authorize commit push to GitHub when satisfied.

---

## 10. Rollback

Revert the Phase 1.6c commit. Remove or unset `foldx_path` in config; pipeline falls back to mock stability for classification. FoldX binary remains local under `foldX/` and does not affect git state.
