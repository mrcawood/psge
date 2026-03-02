# Phase 1 Validation Plan

Date: 2026-02-28

## Objective

Validate that PSGE:
- routes variants correctly (preflight)
- produces plausible mechanism hypotheses for the PPOX panel
- avoids overclaiming

## Tests

### T1: Preflight routing
- missense → structural track
- frameshift/splice → non-structural track with clear rationale

### T2: Mechanism classification (panel)
Run the full PPOX panel and verify expected “plausible class” assignments.

### T3: Reproducibility
Re-run same variant with same config:
- stable caches
- stable outputs (except timestamps)

### T4: Backend variance (optional)
Compare AlphaFold vs ESMFold outputs and ensure reports reflect backend choice.

## Success criteria

- Panel results match the plausibility assertions in `04_VARIANT_PANEL.md`
- Reports include explicit limits and do not imply clinical phenotype
