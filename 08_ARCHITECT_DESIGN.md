# PSGE Architect Design (Phase 1)

Date: 2026-02-28

Source: Derived strictly from 01_PRD.md, 02_ARCHITECTURE.md, 03_DIRECTORY_STRUCTURE.md, 04_VARIANT_PANEL.md, 05_MECHANISM_TAXONOMY.md, 06_VALIDATION_PLAN.md, 00_OVERVIEW.md.

---

## 1. Problem Statement

(From 01_PRD.md §1, 00_OVERVIEW.md)

PPOX variants can reduce enzyme activity through different mechanisms (binding impairment, destabilization, targeting defects, truncation/misexpression). Existing tools predict structures and stability, but PSGE integrates structural modeling, contextual mapping, transparent mechanism hypothesis generation, and reproducible outputs. Given a PPOX variant, produce: the most plausible mechanism class, a short evidence table, explicit uncertainty, and a clear note on what PSGE cannot infer.

---

## 2. Constraints

(From 01_PRD.md §3, §10, 00_OVERVIEW.md)

| Constraint | Source |
|------------|--------|
| No clinical prognosis, penetrance, pathogenicity, or medical advice | PRD §3 |
| Phase 1: protein-level variant notation + curated panel file (YAML) | PRD §5 |
| Outputs MUST include tool versions, parameters, input hashes, skipped steps and why | PRD §6 |
| Containerized execution (Docker) for baseline | PRD §9 |
| Caching mandatory for expensive steps | PRD §9 |
| Emit run_manifest.json per run | PRD §9 |
| Preflight routing: missense → structural; truncation/splice → non-structural | PRD §7 FR1, ARCH §1 |
| Mechanism-first outputs; no phenotype claims | Overview §Scope |
| Research-grade, hypothesis-focused | Overview §Scope |

---

## 3. System Boundaries

(From 01_PRD.md §6, §7; 02_ARCHITECTURE.md "What PSGE cannot infer")

**In scope:**
- Input: variant string (e.g. R59W) + config + optional panel YAML
- Output: summary.json, report.md, optional figures
- Pipeline stages: Preflight, Sequence, Structure, Alignment/delta, Stability, Context mapping, Classification, Reporting

**Out of scope (PSGE cannot infer):**
- mRNA expression/splicing effects (unless splice-site routed)
- Turnover/proteostasis effects
- Protein-protein interaction network consequences
- Clinical expression / penetrance

---

## 4. Component Diagram (Text)

(From 02_ARCHITECTURE.md, 03_DIRECTORY_STRUCTURE.md)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CLI (cli.py)                                                                  │
│   - variant | panel | config → run                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PIPELINE (pipeline/)                                                          │
│                                                                               │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│  │ Preflight │   │ Sequence │   │ Structure│   │ Alignment│   │ Stability│   │
│  │          │──▶│          │──▶│          │──▶│ + Delta  │──▶│          │   │
│  │ route    │   │ WT+mutant│   │ WT+mutant│   │ features │   │ ΔΔG      │   │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   │
│       │                │              │              │              │        │
│       │                │              │              │              │        │
│       ▼                ▼              ▼              ▼              ▼        │
│  (non-structural track skips Structure → Alignment → Stability)               │
│                                                                               │
│  ┌──────────────┐   ┌──────────┐                                             │
│  │ Context      │   │ Mechanism│   ┌──────────┐                               │
│  │ Mapping      │──▶│ Classifier│──▶│ Reporting│                               │
│  │ (FAD, site)  │   │ rules-based│  │ summary  │                               │
│  └──────────────┘   └──────────┘   │ report   │                               │
│                                    └──────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────────────┐
│ backends/       │    │ knowledge/ppox/      │    │ data/                    │
│ - structure     │    │ - sites, motifs      │    │ - public (sequences,    │
│   (AlphaFold,   │    │ - taxonomy           │    │   structures, annots)    │
│   ESMFold)      │    │ - literature mapping │    │ - testdata/variants/     │
│ - stability     │    └─────────────────────┘    └─────────────────────────┘
│   (FoldX,       │
│   Rosetta)      │
└─────────────────┘
```

---

## 5. Data Flow

(From 01_PRD.md §7, 02_ARCHITECTURE.md)

| Stage | Input | Output |
|-------|-------|--------|
| Preflight | variant string, config | VariantRecord { type, routed_track } |
| Sequence | VariantRecord (missense) | WT sequence, mutant sequence |
| Structure | sequences | WT PDB, mutant PDB |
| Alignment/Delta | WT PDB, mutant PDB | global RMSD, local RMSD, SASA delta, contact deltas |
| Stability | structures | ΔΔG, flags |
| Context mapping | structures, knowledge/ppox | distances to FAD/active site; region flags (targeting, membrane) |
| Mechanism classifier | all prior outputs | MechanismHypothesis { class, confidence, evidence_table, limits } |
| Reporting | MechanismHypothesis, run_manifest | summary.json, report.md |

**Contracts (from PRD §6, §7 FR7):**
- `summary.json`: machine-readable; MUST include tool versions, params, input hashes, skipped steps
- `report.md`: human-readable
- `MechanismHypothesis`: class label, confidence label, evidence table, interpretation text, explicit limits section
- `run_manifest.json`: tool versions, config resolved, input hashes, timestamps, compute profile

---

## 6. Failure Modes

(From 01_PRD.md §10, 02_ARCHITECTURE.md)

| Failure | Mitigation |
|---------|------------|
| Overinterpretation of structural deltas | Mechanism framing, explicit uncertainty, no clinical outputs (PRD §10) |
| Wrong tool for variant type | Preflight routing (PRD §10, FR1) |
| Backend variability (AlphaFold vs ESMFold) | Record backend in output; compare across backends for panel (PRD §10) |
| MD too short to mean anything | MD optional; exploratory; document limits (PRD §10) |
| Splice/misexpression run through structural track | Preflight must route to non-structural (06_VALIDATION_PLAN T1) |
| Cache corruption / stale | T3: re-run yields stable outputs; cache key includes input hash |

---

## 7. Alternatives and Tradeoffs

(From 02_ARCHITECTURE.md, 01_PRD.md)

| Choice | Option A | Option B | Selected | Rationale |
|--------|----------|----------|----------|-----------|
| Structure backend | AlphaFold | ESMFold | AlphaFold preferred | PRD FR3 |
| Stability backend | FoldX | Rosetta | FoldX (fast) | 02_ARCHITECTURE §Backends |
| Mechanism classifier | Rules-based | ML | Rules-based initially | 02_ARCHITECTURE §7 |
| MD | Included | Optional | Optional, exploratory | PRD §10 |

---

## 8. Open Questions / Decisions

(From docs; filtered to Phase 1)

| # | Question | Blocking? | Source |
|---|----------|-----------|--------|
| 1 | Doc layout: root 01_PRD.md vs docs/ mirror? | Non-blocking | 03_DIRECTORY_STRUCTURE vs current |
| 2 | Which AlphaFold stack (OpenFold vs DeepMind ref)? | M3 | 99_ORIGINAL §7 |
| 3 | FoldX vs Rosetta for Phase 1 default? | M4 | FoldX in ARCH; Rosetta optional |
| 4 | FAD/active site residue IDs for PPOX—from literature (Qin 2011, Koch 2004)? | M4 | 07_REFERENCES |

---

## Interfaces (Explicit)

### Preflight

```
Input:  variant: str, config: Config
Output: VariantRecord { raw, parsed, type: missense|truncation|splice, track: structural|non_structural }
```

### Sequence

```
Input:  VariantRecord (type=missense), config
Output: SequencePair { wt_sequence, mutant_sequence } | skip_reason
```

### Structure

```
Input:  SequencePair, config
Output: StructurePair { wt_pdb_path, mutant_pdb_path, backend } | skip_reason
```

### Alignment/Delta

```
Input:  StructurePair
Output: DeltaFeatures { global_rmsd, local_rmsd, sasa_delta, contact_deltas }
```

### Stability

```
Input:  StructurePair, config
Output: StabilityResult { ddg, flags[] }
```

### Context Mapping

```
Input:  StructurePair, knowledge/ppox config
Output: ContextFeatures { distance_fad, distance_active_site, in_targeting_region, in_membrane_region }
```

### Mechanism Classifier

```
Input:  VariantRecord, DeltaFeatures?, StabilityResult?, ContextFeatures?, track
Output: MechanismHypothesis { class, confidence, evidence_table, interpretation, limits }
```

Classes: substrate_binding_impairment | structural_destabilization | truncation_misexpression | mitochondrial_targeting_defect
(From 05_MECHANISM_TAXONOMY.md)
