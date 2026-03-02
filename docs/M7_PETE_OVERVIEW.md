# PSGE Phase 1 — One-Page Overview for Domain Sanity Check

## What PSGE Is

**PSGE (Personal Structural Genomics Engine)** is a pipeline for mechanistic, non-clinical analysis of protein variants. Phase 1 focuses on PPOX (UniProt P50336) and produces a mechanism hypothesis with structured evidence and explicit limits.

**What it is not:** Not a clinical predictor. Does not infer phenotype or disease severity. Structure ≠ phenotype.

---

## Phase 1 Deliverable

Given a curated panel of PPOX variants, the pipeline:

1. Routes variants by type (missense vs truncation/splice)
2. Fetches sequences, predicts structures (ESMFold when available; mock otherwise)
3. Computes real RMSD when structures exist; SASA and stability are placeholder
4. Maps variants to curated sites (FAD, active site, targeting region)
5. Assigns one of four mechanism classes with evidence and decision trace

---

## Panel Variants

| Variant    | Class                         |
|-----------|-------------------------------|
| R59W      | substrate_binding_impairment  |
| R152C     | structural_destabilization    |
| G358R     | structural_destabilization    |
| I12T      | mitochondrial_targeting_defect|
| 78insC    | truncation_misexpression      |
| IVS2-2 a→c| truncation_misexpression      |

---

## Mechanism Classes

1. **substrate_binding_impairment** — near FAD/active site; binding affected  
2. **structural_destabilization** — large ΔΔG or destabilizing flags  
3. **truncation_misexpression** — truncation/splice; no structural modeling  
4. **mitochondrial_targeting_defect** — in N-terminal targeting signal (residues 1–28; PMID:12556518, 16621625)  
5. **unknown_mechanism** — default when no rule matches (low confidence)

Reports may include **secondary_hypotheses** when multiple mechanisms apply (e.g. near-site + destabilizing).

---

## Limits Disclaimer

- Structure predictions are computational; no experimental validation for many variants.
- Stability (ΔΔG) is mock in Phase 1; FoldX/Rosetta not yet integrated.
- SASA is placeholder.
- Taxonomy is expert-informed hypothesis structure, not ground truth. Reports use “suggested” wording.

---

## Supporting Materials

- **docs/VALIDATION_SCIENCE.md** — Real metrics, curated sites, rule precedence, limitations
- **Example reports** — `docs/m7_examples/R59W/report.md`, `docs/m7_examples/R152C/report.md`, `docs/m7_examples/I12T/report.md`
- **src/psge/knowledge/ppox/sites.yaml** — FAD, active-site, targeting annotations
