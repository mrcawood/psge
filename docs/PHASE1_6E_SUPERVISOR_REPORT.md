# PSGE Phase 1.6e Supervisor Report

## Summary

Phase 1.6e adds a minimal PPOX evidence-source layer separating PSGE-computed from curated external evidence. Phase 1.6e-fix corrects non-missense tier handling (`variant_class_rule` instead of `pdb_context_only`), adds R59W interpretation gaps, and makes literature `verification_status` explicit (`bibliography_verified` for Meissner 1996 and Qin 2011).

Pre-task `RG358R` typo was fixed in commit `8a40db6` before 1.6e work; `git grep RG358R` is clean.

---

## Files changed

| Area | Files |
|------|-------|
| Source data | `data/sources/ppox_sources.yaml`, `data/sources/ppox_variant_evidence.yaml` |
| Loader | `src/psge/sources/loader.py`, `src/psge/sources/__init__.py` |
| Reporting | `src/psge/reporting/evidence.py`, `src/psge/reporting/summary.py` |
| Tests | `tests/test_sources.py`, `tests/test_variant_evidence.py`, `tests/test_report_evidence_sources.py` |
| Docs | `docs/PHASE1_6E_EVIDENCE_SOURCE_LAYER.md`, `OUTPUT_SCHEMA.md`, `VALIDATION_SCIENCE.md`, `M7_PETE_OVERVIEW.md`, `PROGRESS.md` |

---

## Source registry contents

| source_id | type | tier |
|-----------|------|------|
| PDB_3NKS | pdb_structure | pdb_context_only |
| FOLDX_5_3NKS | computational_prediction | foldx_stability_prediction |
| SASA_BIOPYTHON_3NKS | computational_prediction | pdb_context_only |
| MEISSNER_1996_R59W | functional_assay | functional_assay |
| QIN_2011_R59W_MECHANISTIC | literature | literature_mechanistic |

---

## Variant evidence coverage

| variant | computed | external | highest tier | evidence gaps |
|---------|----------|----------|--------------|---------------|
| R59W | PDB_3NKS, FOLDX_5_3NKS, SASA_BIOPYTHON_3NKS | MEISSNER_1996_R59W, QIN_2011_R59W_MECHANISTIC | functional_assay | interpretation gaps despite external evidence (see variant map) |
| I12T | PDB_3NKS, FOLDX_5_3NKS, SASA_BIOPYTHON_3NKS | none | foldx_stability_prediction | no external functional; targeting unresolved |
| R152C | PDB_3NKS, FOLDX_5_3NKS, SASA_BIOPYTHON_3NKS | none | foldx_stability_prediction | weak/moderate FoldX needs literature review |
| G358R | PDB_3NKS, FOLDX_5_3NKS, SASA_BIOPYTHON_3NKS | none | foldx_stability_prediction | extreme ΔΔG needs external context |
| 78insC | none | none | variant_class_rule | structural/FoldX/SASA not applicable |
| IVS2-2 a→c | none | none | variant_class_rule | structural/FoldX/SASA not applicable |

---

## Tests run

```text
pytest: 50 passed, 1 skipped (FoldX integration when unavailable)
ruff check src/psge tests: passed
```

New tests cover registry load/validation, variant map references, report sections, R59W external rows, and I12T evidence gaps.

---

## Panel run summary

```bash
psge run --panel data/testdata/variants/ppox_panel.yaml \
  --structure-source pdb_first \
  --results-dir results/foldx_panel_1_6e
```

| variant | primary class | FoldX band | notes |
|---------|---------------|------------|-------|
| R59W | cofactor_binding_perturbation | borderline_destabilizing | secondary folding; external evidence in report |
| I12T | folding_stability_hydrophobic_core | destabilizing | targeting secondary |
| R152C | unknown_mechanism | weak_to_moderate | folding secondary |
| G358R | folding_stability_hydrophobic_core | extreme_destabilizing_requires_audit | provenance visible |
| 78insC | truncation_misexpression | skipped | evidence gap listed |
| IVS2-2 a→c | truncation_misexpression | skipped | evidence gap listed |

---

## Example report snippets

R59W external evidence block:

```text
R59W has curated literature evidence reporting reduced PPOX enzyme activity (Meissner et al. 1996).
Qin et al. (2011) discuss R59W in relation to the FAD/cofactor environment as mechanistic context.
```

I12T evidence gap:

```text
- No curated external functional evidence linked for I12T in PSGE.
- Targeting/localization remains unresolved by FoldX and lacks linked literature.
```

Per-row FoldX source:

```text
ddg: 2.02263 (type=foldx_ddg, source=FOLDX_5_3NKS, scope=computational_prediction, ...)
```

---

## Open gaps before Pete

- No curated external evidence for I12T, R152C, G358R (by design in 1.6e)
- ΔΔG bands still provisional; not calibrated to literature
- FAD/active-site residue lists still provisional
- Pete-facing packet not started
- Broader literature mining deferred

---

## Recommendation

Phase 1.6e is ready for supervisor review. Do not sync with Pete yet. After approval, next decision is whether M7 (Pete packet) or bounded literature expansion for non-R59W panel variants is the priority.

Rollback: revert the Phase 1.6e commit; 1.6d reporting and band logic remain.
