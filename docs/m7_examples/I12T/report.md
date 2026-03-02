# PSGE Mechanism Report

**Variant:** I12T

## Mechanism Hypothesis (Suggested)

*This taxonomy is expert-informed hypothesis structure, not ground truth. Do not overclaim.*

- **Class:** mitochondrial_targeting_defect
- **Confidence:** plausible

## Classifier Decision Trace

- rule: in_targeting_region → mitochondrial_targeting_defect

## Interpretation

Variant lies in mitochondrial targeting peptide; sequence/motif analysis indicated.

## Evidence

- in_targeting_region: True

## Limits

PSGE uses sequence-level targeting annotation; 3D structure less informative here.

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