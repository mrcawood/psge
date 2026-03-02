# PSGE Mechanism Report

**Variant:** R152C

## Mechanism Hypothesis (Suggested)

*This taxonomy is expert-informed hypothesis structure, not ground truth. Do not overclaim.*

- **Class:** structural_destabilization
- **Confidence:** low

## Classifier Decision Trace

- rule: destabilizing_ddg_or_flags (mock) → structural_destabilization

## Interpretation

Stability analysis suggests destabilization. Mock ΔΔG; FoldX/Rosetta needed for validation.

## Evidence

- ddg (mock): 2.5
- flags (mock): ['destabilizing']

## Limits

Mock ΔΔG in Phase 1; FoldX/Rosetta needed for validation.

## Backend Status

- structure_backend: mock
- stability_backend: mock
- delta_metrics: real_rmsd
- sasa: not_implemented

**Note:** Some metrics use mock or placeholder backends (e.g. stability, SASA). Global/local RMSD are real when structure_backend is not mock. See backend_status.

## Skipped Steps

- None

---
*PSGE: Personal Structural Genomics Engine. Research-grade, non-clinical.*