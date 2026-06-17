# PSGE Progress

## Project Summary

PSGE (Personal Structural Genomics Engine) is a reproducible HPC + AI workflow for mechanistic, non-clinical analysis of PPOX variants. Phase 1 delivers a PPOX Mechanism Panel MVP: given a curated panel of known PPOX variants, produce structured reports assigning the most plausible mechanism class with supporting evidence and explicit uncertainty.

## Current Phase

Implementation

## Current State

- Documentation complete: PRD, architecture, variant panel, mechanism taxonomy, validation plan
- Architect design: 08_ARCHITECT_DESIGN.md
- Implementation plan: 09_PLAN.md
- M1 complete: pyproject.toml, CLI, pipeline stubs, run_manifest, config loader
- M2 complete: preflight parsing/classification, panel YAML loader, CLI `--panel`
- M3 complete: sequence fetch (UniProt), variant application, structure mock backend, file-based cache
- M4 complete: DeltaFeatures, StabilityResult, ContextFeatures; alignment_delta, stability, context_mapping; knowledge/ppox sites
- M5 complete: MechanismHypothesis, rules-based classifier, summary.json, report.md
- M6a complete: logic validation, backend_status, decision_trace, VALIDATION_LOGIC.md, T2 assertions
- M6b complete: real RMSD (BioPython), curated PPOX residues (sites.yaml), ESMFold backend option, backend_status sasa/limits, docs/VALIDATION_SCIENCE.md
- Tests: 36 pass, 1 skipped (FoldX integration when unavailable)
- Git repo initialized, no commits

## Approval Status

Awaiting user approval

## Key Decisions

- Phase 1 scope: PPOX Mechanism Panel MVP (not single-variant demo)
- Pipeline DAG: Preflight → Sequence → Structure → Alignment/delta → Stability → Context mapping → Classification → Reporting
- Structural backends: AlphaFold preferred, ESMFold fallback
- Stability: FoldX (fast), Rosetta optional
- Rules-based mechanism classifier initially; no clinical outputs
- Explicit stage interfaces defined (VariantRecord, SequencePair, StructurePair, DeltaFeatures, etc.)
- M6 split: M6a logic validation (mock backends OK), M6b scientific integration (real backends)

## Decision Records

### DR-001: M6 split into M6a (logic) and M6b (science)
- Decision: Split M6 into two sub-milestones
- Options: Single M6 vs M6a logic + M6b science
- Selected: M6a (logic validation) + M6b (scientific integration)
- Rationale: Current run validates orchestration, not science; backends are mocked. Label correctly. M6a proves plumbing; M6b replaces mocks with real computations.
- Date: 2026-02-28

### DR-002: Pete nuances — taxonomy and precedence
- Mechanism taxonomy is not purely structural; preflight routing is core.
- Rule precedence: targeting-region must not be overridden by destabilizing; support primary + secondary hypotheses (first release emits one primary).
- Be explicit that taxonomy is "suggested"; bake into every report.
- Date: 2026-02-28

## Active Tasks

- [x] Architecture design (08_ARCHITECT_DESIGN.md)
- [x] Implementation plan (09_PLAN.md)
- [x] M1: Pipeline skeleton + CLI
- [x] M2: Preflight routing + panel runner
- [x] M3: Structure backend + caching
- [x] M4: Stability + context mapping
- [x] M5: Mechanism classifier + report templates
- [x] M6a: Logic validation report
- [x] M6b: Scientific integration (real structure, RMSD, curated PPOX)
- [x] Phase 1.6a–c: SASA local-only, FoldX integration, panel validation (`docs/PHASE1_6C_SUPERVISOR_REPORT.md`)
- [x] Phase 1.6d: Evidence tiering, ΔΔG bands, FoldX provenance, doc refresh (`docs/PHASE1_6D_SUPERVISOR_REPORT.md`)
- [ ] M7: Pete-facing packet (after supervisor review; not Phase 1.6d)

## Open Questions

- Q1: Doc layout—root 01_PRD.md vs docs/ mirror? (non-blocking)
- Q2: AlphaFold stack: OpenFold vs DeepMind ref? (M3)
- Q3: FoldX vs Rosetta default for Phase 1? (M4)
- Q4: FAD/active site residue IDs from Qin 2011, Koch 2004? (M4)

## Technical Context

- Plan: `09_PLAN.md`
- Architect design: `08_ARCHITECT_DESIGN.md`
- PRD: `01_PRD.md`
- Architecture: `02_ARCHITECTURE.md`
- Target layout: `03_DIRECTORY_STRUCTURE.md`
- Variant panel: `04_VARIANT_PANEL.md`
- Mechanism taxonomy: `05_MECHANISM_TAXONOMY.md`
- Validation plan: `06_VALIDATION_PLAN.md`
- Docs use root-level `01_PRD.md` etc.; target layout suggests `docs/` mirror

## Constraints / Requirements

- Mechanism-first outputs; no clinical/phenotype claims
- Preflight routing for variant type (missense vs truncation/splice)
- Containerized execution (Docker) for baseline
- Caching mandatory for expensive steps
- `run_manifest.json` per run for reproducibility

## Recent Changes (Today)

- Bootstrap: created PROGRESS.md from PRD
- Architect: produced 08_ARCHITECT_DESIGN.md from docs (interfaces, data flow, failure modes, contracts)
- Planner: produced 09_PLAN.md (milestones, tasks, sprints, tests-first)
- Developer: M1 implementation (pyproject, layout, CLI, pipeline stubs, run_manifest, config, tests)
- Developer: M2 implementation (preflight classification, variant parse, panel loader, --panel CLI)
- Developer: M3 implementation (sequence fetch UniProt, variant apply, structure mock, cache)
- Developer: M4 implementation (DeltaFeatures, StabilityResult, ContextFeatures; alignment, stability, context; knowledge/ppox)
- Developer: M5 implementation (MechanismHypothesis, classifier, summary.json, report.md)
- Developer: M6a implementation (backend_status, decision_trace, VALIDATION_LOGIC.md, T2 test, Pete nuances)
- Developer: M6b implementation (pdb_rmsd.py, sites.yaml curation, ESMFold backend, VALIDATION_SCIENCE.md, backend_status sasa/limits)

## Proposed Next Step (Requires Approval)

- NextRole: roles/REVIEWER or Pete (domain sanity)
- Trigger: none
- TriggeredRole: —
- Why: M6a and M6b complete. M7: review with Pete for domain sanity check.
- Confidence: High
- Alternatives: none

## Git Status (Optional)

- current branch: master
- no commits yet
- related PR: none
- merge target: N/A
- tests run: pytest tests/ -v (25 passed)
