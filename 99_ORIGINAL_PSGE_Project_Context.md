# Project Context Artifact: Personal Structural Genomics Engine (PSGE)

## 1. Core Concept

Build a reproducible HPC + AI pipeline to analyze personal missense
mutations (starting with PPOX R59W) at the structural level.

Working idea: - Use whole genome sequencing (30x WGS) - Extract missense
variants - Predict protein structures (WT vs mutant) using AlphaFold -
Compute structural deltas and stability impact - Optionally run
molecular dynamics and/or QM/MM analysis

Project name (working): **Personal Structural Genomics Engine (PSGE)**

------------------------------------------------------------------------

## 2. Motivating Mutation

Gene: PPOX (Protoporphyrinogen Oxidase)\
Associated condition: Variegate Porphyria\
Candidate mutation: R59W (Arginine → Tryptophan at residue 59)

Key questions: - Is residue 59 structurally critical? - Does R59W alter
protein stability (ΔΔG)? - Is the residue near the active site or FAD
binding region? - Would MD or QM/MM modeling provide meaningful
mechanistic insight?

Important: This project is exploratory/research-focused, not clinical or
diagnostic.

------------------------------------------------------------------------

## 3. Technical Architecture (Proposed)

### Phase 1 -- PPOX Deep Dive (MVP)

Pipeline: 1. Pull canonical PPOX sequence (UniProt). 2. Generate WT and
R59W sequences. 3. Run AlphaFold2 locally. 4. Compute RMSD between WT
and mutant. 5. Perform ΔΔG stability prediction (FoldX / Rosetta). 6. If
interesting → short MD simulation (GROMACS).

Deliverables: - Structural overlay visualizations - RMSD metrics -
Stability estimates - Reproducible containerized workflow

------------------------------------------------------------------------

### Phase 2 -- Generalized Variant Engine

Given full WGS:

-   Extract all missense mutations from VCF.
-   Filter by:
    -   ClinVar annotation
    -   Disease-associated genes
    -   Conservation scores
-   Run structural impact analysis on top N candidates.
-   Rank variants by predicted structural disruption.

Output: - Structural perturbation scores - Active-site proximity
ranking - Stability impact summary

------------------------------------------------------------------------

### Phase 3 -- HPC Benchmarking Angle

Turn the workflow into a real-world benchmark workload:

Components: - AlphaFold inference - Stability prediction - Short MD
simulation - Structural delta analysis

Metrics: - Runtime per variant - GPU memory footprint - Throughput
scaling - Cost per prediction - Energy efficiency

Hardware context: - RTX 4080 Super - RTX 3070 Ti - Potential ROCm vs
CUDA comparisons

This could become a standardized "Bio-AI Structural Benchmark Suite."

------------------------------------------------------------------------

## 4. Value Creation

### Personal Value

-   Deep understanding of structural consequences of personal mutations.
-   Skill expansion into computational biology.
-   Tangible intersection of AI + physics-based modeling.

### Academic Value

-   Potential collaboration with computational chemistry lab (Krishna
    Govender, University of Johannesburg).
-   Cross-continental collaboration opportunity.
-   Possible publication on reproducible mutation modeling workflow.

### Commercial Value (Exploratory)

Possible wedges: - Structural mutation analysis SaaS (non-clinical,
research-grade). - GPU benchmarking suite for AI hardware vendors. -
Open-core CLI + paid compute service model.

Clear boundary: No medical diagnosis or clinical claims.

------------------------------------------------------------------------

## 5. Strategic Rationale

This project aligns strongly with: - HPC systems engineering
background - AI inference benchmarking expertise - Reproducible pipeline
design - Multi-GPU orchestration experience - Emerging role in AI
validation

It demonstrates applied AI on real scientific workloads rather than toy
problems.

------------------------------------------------------------------------

## 6. Krishna Outreach Context

A friendly message was drafted to Krishna Govender (Computational
Chemistry and Materials Modelling Lab, University of Johannesburg) to:

-   Reconnect and catch up
-   Introduce the PPOX structural modeling idea
-   Ask whether the project is scientifically interesting
-   Explore whether there is meaningful computational chemistry depth
    beyond AlphaFold

Decision: Seek expert feedback before building the full pipeline.

------------------------------------------------------------------------

## 7. Open Questions

Scientific: - Is R59W in PPOX structurally significant? - Is residue 59
near active or regulatory regions? - Would MD simulation meaningfully
differentiate WT vs mutant? - Is ΔΔG sufficient or is QM/MM warranted?

Technical: - Which AlphaFold stack to use (OpenFold vs DeepMind
reference)? - Best ΔΔG tool for automation at scale? - Feasible MD
simulation length for benchmarking realism? - Optimal GPU precision
strategy (FP16, BF16, FP8 KV)?

Strategic: - Hobby science vs academic collaboration vs product? -
Publish as benchmark suite? - Keep personal data local-only?

------------------------------------------------------------------------

## 8. Immediate Next Steps

1.  Wait for Krishna's feedback.
2.  Pull canonical PPOX structure and examine residue 59 environment.
3.  Draft MVP pipeline architecture (Dockerized).
4.  Define benchmarking experiment design across GPUs.

------------------------------------------------------------------------

## 9. Guiding Constraints

-   Research-grade, not clinical.
-   Fully reproducible.
-   Containerized workflows.
-   Clear separation between AI prediction and physics-based modeling.
-   Documented performance metrics.

------------------------------------------------------------------------

End of context artifact.
