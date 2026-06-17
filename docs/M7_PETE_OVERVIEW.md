# PSGE Phase 1 — Overview for Domain Review (updated Phase 1.6e)

## What PSGE Is

PSGE (Personal Structural Genomics Engine) is a pipeline for mechanistic, non-clinical analysis of PPOX variants (UniProt P50336). It produces a suggested mechanism hypothesis with structured evidence, explicit evidence tiers, and conservative limits.

What it is not: a clinical predictor. It does not infer pathogenicity, penetrance, disease severity, or treatment relevance.

## Phase 1 deliverable (current)

Given the curated PPOX panel, the pipeline:

1. Routes variants by type (missense vs truncation/splice)
2. Uses experimental 3NKS for `pdb_first` structural context (FAD, inhibitor ACJ proximity)
3. Computes real RMSD and local SASA (local-only; no global SASA deltas when structures are incomparable)
4. Runs FoldX ΔΔG on protein-only repaired 3NKS when configured (`foldx_path` or `FOLDX_PATH`)
5. Assigns Phase 1.5 mechanism classes with rule precedence, threshold bands, and evidence-gated secondaries

## Panel variants (pdb_first + FoldX, Phase 1.6d)

| Variant | Typical primary (current) | Notes |
|---------|---------------------------|-------|
| R59W | cofactor_binding_perturbation | FAD-proximal; borderline FoldX signal secondary |
| I12T | folding_stability_hydrophobic_core | FoldX destabilizing; targeting unresolved |
| R152C | unknown_mechanism | weak-to-moderate FoldX signal recorded |
| G358R | folding_stability_hydrophobic_core | extreme FoldX signal; audit required |
| 78insC | truncation_misexpression | FoldX skipped |
| IVS2-2 a→c | truncation_misexpression | FoldX skipped |

## Mechanism classes (Phase 1.5)

See `docs/PHASE1_5_REMAP.md`. Key names: `cofactor_binding_perturbation`, `folding_stability_hydrophobic_core`, `targeting_signal_perturbation` (secondary by default), `truncation_misexpression`, `unknown_mechanism`.

Cofactor proximity does not prove binding affinity. FoldX ΔΔG is a protein stability estimate, not a clinical or catalytic measurement.

## Evidence tiers (Phase 1.6e)

Reports distinguish `pdb_context_only` and `foldx_stability_prediction` (PSGE-computed) from curated external tiers (`literature_mechanistic`, `functional_assay`). R59W links Meissner (1996) reduced-activity data and Qin (2011) mechanistic context from project bibliography only. Other panel variants list explicit evidence gaps when no external source is curated.

Computed vs external evidence is separated in every report (`Evidence basis`, `Computed evidence`, `External evidence`, `Evidence gaps`).

## Limits

- Curated FAD/active-site residue sets are provisional; Pete has not formally endorsed exact lists.
- ΔΔG threshold bands are provisional (see `docs/VALIDATION_SCIENCE.md`).
- Inhibitor (ACJ) in 3NKS is a structural proxy; not proof of substrate binding.

## Supporting materials

- `docs/VALIDATION_SCIENCE.md` — metrics, bands, classifier policy
- `docs/OUTPUT_SCHEMA.md` — `summary.json` / `report.md` fields
- `docs/PHASE1_6E_SUPERVISOR_REPORT.md` — latest validation summary
- `docs/PHASE1_6E_EVIDENCE_SOURCE_LAYER.md` — source registry and variant map
- `src/psge/knowledge/ppox/sites.yaml` — curated sites
