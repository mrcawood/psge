# PSGE Context Overview (for worker agents)

Date: 2026-02-28

## What this is

PSGE (Personal Structural Genomics Engine) is a reproducible HPC + AI workflow for **mechanistic, non-clinical** analysis of PPOX variants (starting with PPOX R59W).

Key principle: produce **mechanistically plausible hypotheses** with explicit uncertainty. Do not output clinical predictions.

## Why PPOX / VP

- Case study gene: **PPOX** (protoporphyrinogen oxidase)
- Case study condition: variegate porphyria (VP)
- Starting variant: **R59W** (clinically confirmed silent carrier)

R59W is a strong vertical case study because it is well characterized in the literature and has enzyme activity evidence.

## Guidance from domain experts (summary)

### Pete (porphyria expert, retired but active)
- Structural predictions can help explain **mechanism**, but are not meaningful for predicting **clinical expression**.
- Variant interpretation requires functional evidence and biological context.
- Provided a practical taxonomy of PPOX mechanisms:
  - Substrate-binding impairment (example: R59W)
  - Structural destabilization (examples: R152C, G358R)
  - Truncation / misexpression (examples: 78insC, IVS2-2 a→c)
  - Mitochondrial targeting defects (example: I12T)

### Lorenzo (genomics / multi-omics)
- “There are so many layers”: expression, turnover, co-factors, protein interactions.
- Generalizing a structure-based effect model across proteins is risky.
- Structure + conservation + ClinVar + expression can guide experiments; phenotype prediction is hard.

## Phase 1 direction (updated)

Phase 1 is now a **PPOX Mechanism Panel MVP**, not a single-variant demo.

Deliverable: for a small panel of known PPOX variants, produce a structured report that assigns the most plausible mechanism class and supporting evidence, and routes non-structural variants appropriately.

## Scope boundaries (non-negotiable)

- Research-grade and hypothesis-focused.
- Not clinical, not diagnostic, not a pathogenicity classifier.
- Explicitly avoid “will get sick” and similar phenotype claims.
