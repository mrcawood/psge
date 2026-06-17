# PSGE Phase 1.6d Supervisor Report

**Date:** 2026-06-17  
**Scope:** Evidence hardening, threshold bands, FoldX provenance, report readiness  
**Host:** talos

---

## 1. Executive summary

Phase 1.6d is complete. PSGE now emits evidence tiers at report and per-row level, uses provisional ΔΔG bands (including `borderline_destabilizing` for 2.0–2.5 kcal/mol), records full FoldX provenance, applies conservative variant-specific interpretation text, and updates stale documentation. Panel validation on `pdb_first` + FoldX matches supervisor expectations without hardcoding per-variant classifier exceptions.

---

## 2. Environment

| Item | Value |
|------|-------|
| OS | Linux (talos) |
| FoldX path | `foldX/foldx_20270131` (via `configs/default.yaml`) |
| FoldX version | `5` |
| Config | `configs/default.yaml` |
| Structure source | `pdb_first` (3NKS) |
| FoldX input policy | Protein-only repaired PDB; FAD/ACJ not included |

---

## 3. Code changes

| File | Change |
|------|--------|
| `src/psge/utils/stability_bands.py` | Provisional ΔΔG bands and primary/secondary qualification |
| `src/psge/backends/foldx/audit.py` | G358R-style audit checks and provenance builder |
| `src/psge/backends/foldx/runner.py` | Bands, provenance, audit on successful runs |
| `src/psge/pipeline/mechanism.py` | Band-based classifier; cofactor precedence preserved |
| `src/psge/reporting/evidence.py` | Per-row and report-level evidence tiering |
| `src/psge/reporting/interpretation.py` | R59W, I12T, R152C, G358R wording |
| `src/psge/reporting/summary.py` | Enriched evidence, FoldX provenance section |
| `src/psge/reporting/manifest.py` | Threshold bands + foldx_provenance in manifest |
| `src/psge/core/models.py` | `StabilityResult` extended (band, provenance, audit) |
| `data/testdata/variants/ppox_panel_expected_pdb_first_foldx.yaml` | FoldX panel expectations |
| `tests/test_stability_bands.py`, `tests/test_panel_foldx.py` | Band and panel tests |
| Docs | `M7_PETE_OVERVIEW.md`, `OUTPUT_SCHEMA.md`, `VALIDATION_SCIENCE.md`, `PROGRESS.md` |

---

## 4. Test results

```text
pytest: 36 passed, 1 skipped
ruff check: pass
FoldX integration: runs when binary detectable; skips in CI otherwise
test_panel_pdb_first_foldx_expectations: pass on talos
```

---

## 5. Panel results (`results/foldx_panel_1_6d/`)

| variant | mapping | foldx_status | ddg | band | primary | secondaries | confidence | notes |
|---------|---------|--------------|-----|------|---------|-------------|------------|-------|
| R59W | exact | success | 2.02 | borderline_destabilizing | cofactor_binding_perturbation | folding_stability | plausible | Cofactor primary; borderline FoldX secondary |
| I12T | exact | success | 3.78 | destabilizing | folding_stability_hydrophobic_core | targeting, cofactor | plausible | Targeting unresolved by FoldX |
| R152C | exact | success | 1.68 | weak_to_moderate | unknown_mechanism | folding_stability | low | Signal recorded; not primary |
| G358R | exact | success | 15.29 | extreme_destabilizing_requires_audit | folding_stability_hydrophobic_core | — | plausible | audit_passed: true |
| 78insC | n/a | skipped | — | — | truncation_misexpression | — | plausible | Clean skip |
| IVS2-2 a→c | n/a | skipped | — | — | truncation_misexpression | — | plausible | Clean skip |

---

## 6. Interpretation review

**R59W.** Cofactor/FAD-environment remains primary by rule precedence. ΔΔG 2.02 is `borderline_destabilizing`; folding appears as secondary only. Interpretation states possible local stability contribution without claiming folding mutation or clinical effect.

**I12T.** FoldX `destabilizing` band supports folding primary. Targeting/localization remains secondary and explicitly unresolved by FoldX.

**R152C.** `weak_to_moderate` band visible in evidence; primary stays `unknown_mechanism`. Interpretation records signal for review without forced destabilization label.

**G358R.** Extreme ΔΔG with `audit_passed: true` (mapping, mutation string, RepairPDB, Dif parse, mutant model). Manual review still warranted for magnitude.

**Non-missense.** FoldX skipped; truncation routing unchanged.

---

## 7. FoldX QA (embedded)

### Repeatability
R59W run twice via `compute_foldx_ddg`: ΔΔG 2.02263 both times; band stable. Cached RepairPDB/BuildModel outputs reused deterministically.

### G358R audit
- UniProt 358 → PDB A358, mutation `GA358R`
- RepairPDB and BuildModel completed
- `Dif_*.fxout` parsed; `audit_passed: true`
- Note: ΔΔG > 10 kcal/mol flagged for manual review in audit notes

---

## 8. Remaining open items

### Must do before Pete
- Supervisor review of this report and `results/foldx_panel_1_6d/`
- Evidence tier fields for literature/functional sources (Phase 1.6e)
- Pete-facing packet (explicitly deferred from 1.6d)

### Good stretch for 1.6e
- Literature-driven panel expansion with curated sources
- Threshold calibration against literature (not label-fitting)
- Formal Pete endorsement of site residue lists

### Longer-term
- Rosetta or alternate stability backends
- Multi-primary mechanism support if ever desired

---

## 9. Recommendation

Phase 1.6d is ready for supervisor review. Do not sync with Pete yet. Next step after approval: decide Phase 1.6e scope (literature sources vs Pete packet).

---

## 10. Rollback

Revert Phase 1.6d commit. Prior Phase 1.6c FoldX integration remains; band/tier fields absent from outputs.
