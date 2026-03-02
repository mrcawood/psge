# PSGE PRD v0.2 (Phase 1: PPOX Mechanism Panel MVP)

Date: 2026-02-28

## 1. Problem statement

PPOX variants can reduce enzyme activity through different mechanisms (binding impairment, destabilization, targeting defects, truncation/misexpression).

Existing tools can predict structures and stability, but PSGE’s goal is to integrate:
- structural modeling (when appropriate)
- contextual mapping (active site / FAD / domains / targeting region)
- transparent mechanism hypothesis generation
- reproducible outputs and benchmarking hooks

## 2. Goals

### Primary
Given a PPOX variant, produce:
- the **most plausible mechanism class**
- a short evidence table with metrics and thresholds
- explicit uncertainty
- a clear note on what PSGE cannot infer

### Secondary
- Provide a reproducible workflow suitable as an HPC benchmark workload.

## 3. Non-goals

- Clinical prognosis or penetrance estimation
- Pathogenicity classification
- Medical advice
- Cross-gene or cross-protein generalization claims

## 4. Users

- Primary: computational practitioner building reproducible pipelines
- Secondary: domain experts reviewing mechanistic plausibility

## 5. Inputs

Phase 1 supports:
- protein-level variant notation (e.g., R59W)
- a small curated panel file (YAML)

Phase 2 (future) may support:
- VCF ingestion (requires WGS/VCF data)

## 6. Outputs (contract)

For each run:
- `summary.json` (machine-readable)
- `report.md` (human-readable)
- optional figures (overlay snapshots, local metrics)

Each output MUST include:
- tool versions / parameters
- input hashes
- which steps were skipped and why (e.g., splice variant)

## 7. Functional requirements

### FR1: Preflight routing
- Determine variant class: missense vs truncation/misexpression vs splice.
- Route:
  - missense → structural track
  - truncation/splice → non-structural track + recommended next analysis

### FR2: WT + mutant sequence generation
- Fetch canonical PPOX sequence (public source) and create mutant sequence for missense variants.

### FR3: Structure prediction (missense only)
- Preferred backend: AlphaFold (if available)
- Fallback: ESMFold
- Emit WT and mutant structures

### FR4: Structural delta metrics
- global alignment + RMSD
- local RMSD around residue neighborhood
- solvent accessibility change
- local contact changes (lightweight)

### FR5: Stability estimation
- ΔΔG via FoldX or Rosetta (config-driven)
- Flag destabilization thresholds

### FR6: Context mapping
- Distances to:
  - FAD-binding region/residues
  - active site residues
- Identify if variant lies in:
  - mitochondrial targeting region
  - membrane association regions

### FR7: Mechanism hypothesis classification
Return a `MechanismHypothesis` with:
- class label
- confidence label
- evidence table
- interpretation text (short, cautious)
- explicit “limits” section

## 8. Phase 1 validation set (panel)

See `04_VARIANT_PANEL.md`.

Success criteria:
- R59W → substrate-binding impairment (plausible)
- R152C, G358R → destabilization (plausible)
- I12T → targeting defect (plausible, sequence-focused)
- 78insC, IVS2-2 a→c → truncation/misexpression; structural steps skipped

## 9. Reproducibility requirements

- Containerized execution (Docker) for baseline
- Caching mandatory for expensive steps
- Emit `run_manifest.json` per run capturing:
  - tool versions
  - config resolved
  - input hashes
  - timestamps
  - compute profile (local vs HPC)

## 10. Risks + mitigations

- Overinterpretation of structural deltas → mitigation: mechanism framing, explicit uncertainty, no clinical outputs.
- Wrong tool for variant type → mitigation: preflight routing.
- Backend variability (AlphaFold vs ESMFold) → mitigation: record backend, compare across backends for panel.
- MD too short to mean anything → mitigation: MD optional; treat as exploratory; document limits.

## 11. WGS / genetic test decision

Phase 1 does **not** require new WGS because the PPOX target variant is already known and can be modeled in silico.

WGS becomes relevant only for future Phase 2 (VCF ingestion and ranking across many variants).

Decision gate: do Phase 1 first; only order WGS once Phase 1 is credible and Phase 2 is truly desired.

## 12. Milestones

- M1: Implement pipeline skeleton + CLI
- M2: Preflight routing + panel runner
- M3: Structure backend integration + caching
- M4: Stability + context mapping
- M5: Mechanism classifier + report templates
- M6: Run panel + produce validation report
- M7: Review with Pete (domain sanity check)
