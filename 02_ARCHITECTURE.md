# PSGE Architecture (Phase 1)

Date: 2026-02-28

## Architectural principles

- Mechanism-first outputs (not phenotype)
- Preflight routing to avoid misuse of structural compute
- Pluggable backends for structure/stability/MD
- Reproducible runs: every output has provenance
- Cache expensive steps

## Core pipeline DAG

Input: `variant` + `config`

1) Preflight
- Parse variant
- Classify type
- Route:
  - missense → structural track
  - truncation/splice → non-structural track

2) Sequence
- Fetch canonical PPOX sequence
- Create WT and mutant sequences (missense only)

3) Structure prediction (missense only)
- AlphaFold preferred; ESMFold fallback
- Output: WT + mutant structures

4) Alignment + delta features
- global RMSD
- local neighborhood RMSD
- SASA / solvent exposure changes
- contact deltas

5) Stability
- ΔΔG estimation via FoldX or Rosetta

6) Context mapping
- Distance to FAD binding and active site features
- Identify targeting region / motifs

7) Mechanism classification
- Transparent rules-based engine (initially)
- Output: class + evidence + confidence + limits

8) Reporting
- `summary.json` + `report.md` + optional figures

## Backends (Phase 1)

- Structure:
  - AlphaFold (preferred)
  - ESMFold (fallback)
- Stability:
  - FoldX (fast)
  - Rosetta (optional / heavier)
- MD:
  - GROMACS (optional, Phase 1 exploratory only)

## What PSGE cannot infer

- mRNA expression/splicing effects (unless variant is splice-site and routed accordingly)
- turnover/proteostasis effects directly
- protein-protein interaction network consequences (unless specifically annotated)
- clinical expression / penetrance
