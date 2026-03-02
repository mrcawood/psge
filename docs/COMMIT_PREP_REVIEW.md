# Commit prep review

**Date:** 2026-02-28  
**Purpose:** Align with 02_ARCHITECTURE, 03_DIRECTORY_STRUCTURE, 08_ARCHITECT_DESIGN before first commit.

---

## 1. Architecture alignment ✓

**Pipeline DAG (02_ARCHITECTURE, 08_ARCHITECT_DESIGN):**

| Stage | Doc | Implementation |
|-------|-----|----------------|
| 1. Preflight | ✓ | `stages.preflight` → `VariantRecord` |
| 2. Sequence | ✓ | `stages.sequence` → `SequencePair` |
| 3. Structure | ✓ | `stages.structure` → `StructurePair` (PDB-first / ESMFold) |
| 4. Alignment + delta | ✓ | `stages.alignment_delta` → `DeltaFeatures` |
| 5. Stability | ✓ | `stages.stability` → `StabilityResult` |
| 6. Context mapping | ✓ | `stages.context_mapping` → `ContextFeatures` |
| 7. Mechanism classification | ✓ | `stages.mechanism_classifier` → `MechanismHypothesis` |
| 8. Reporting | ✓ | `stages.reporting` → `summary.json`, `report.md` |

**Backends:** structure (pdb, esmfold), stability (mock), sequence, alignment, context. All present.

**Outputs:** `summary.json`, `report.md`, `run_manifest.json` per run. ✓

---

## 2. Directory structure: doc vs actual

**03_DIRECTORY_STRUCTURE.md** recommends:

```text
docs/
  PRD.md, ARCHITECTURE.md, VARIANT_PANEL.md, MECHANISM_TAXONOMY.md, REFERENCES.md
data/testdata/
  variants/ppox_panel.yaml
  expected/
configs/
  default.yaml
  backends/
  environments/
src/psge/ ...
docker/
results/
```

**Actual layout:**

| Item | Doc | Actual | Status |
|------|-----|--------|--------|
| Root docs | 03 says `docs/PRD.md` etc. | Root has `01_PRD.md`, `02_ARCHITECTURE.md`, ... (numbered) | **Divergence** — project uses root-level numbered docs |
| docs/ | PRD, ARCHITECTURE, ... | `SUPERVISOR_REPORT.md`, `PHASE1_5_REMAP.md`, `VALIDATION_*.md`, `M7_*`, `m7_examples/` | **Different role** — `docs/` holds Phase 1.5 and validation content |
| data/testdata/expected/ | Present | **Missing** | Gap |
| configs/backends/ | Present | **Missing** | Gap |
| configs/environments/ | Present | **Missing** | Gap |
| docker/ | Present | **Missing** | Gap |
| data/private/ | README.md | ✓ exists | OK |
| src/psge/ layout | cli, core, pipeline, backends, knowledge, reporting, utils | ✓ matches | OK |

**Recommendation:** 03_DIRECTORY_STRUCTURE is aspirational. Either (a) update 03 to reflect current layout, or (b) add placeholder dirs (`configs/backends/.gitkeep`, `configs/environments/.gitkeep`, `data/testdata/expected/.gitkeep`, `docker/.gitkeep`) if those are planned soon. `docker/` is Phase 1 scope per 01_PRD §9.

---

## 3. File consistency

**Python layout (src/psge/):**
- `cli.py`, `core/`, `pipeline/`, `backends/`, `knowledge/ppox/`, `reporting/`, `utils/` ✓
- All stages in `pipeline/stages.py`; orchestrator in `pipeline/runner.py` ✓
- `backends/`: `structure.py`, `structure_pdb.py`, `structure_esmfold.py`, `stability.py`, `alignment.py`, `sequence.py`, `context.py` ✓

**Naming:**
- `ContextFeatures` / `backends/context.py` — context mapping stage ✓
- `mechanism.py` in `pipeline/` (not `backends/`) ✓
- Knowledge: `knowledge/ppox/sites.yaml` ✓

**Test layout:**
- `tests/test_preflight.py`, `test_sequence.py`, `test_structure_cache.py`, `test_stability_context.py`, `test_mechanism_reporting.py`, `test_panel.py`, `test_panel_t2.py`, `test_cli.py` ✓

---

## 4. .gitignore and exclusions

**Current .gitignore:**
- `.venv/`, `__pycache__/`, `*.py[cod]`, `*.egg-info/`, `dist/`, `build/`
- `results/*` (with `!results/.gitignore`)

**03_DIRECTORY_STRUCTURE says:**
- `data/private` excluded from git

**Action:** Add `data/private/` to `.gitignore` if it should never be committed.

**Optional (reduce repo size):**
- `data/public/structures/cache/` — derived; consider ignoring
- `data/public/structures/pdb/` — 3NKS.cif (~456 KB) is a public reference; keep or document fetch in README

---

## 5. Summary: before commit

| Area | Action |
|------|--------|
| **03_DIRECTORY_STRUCTURE** | Update to reflect root-level `01_PRD.md` etc. and `docs/` Phase 1.5 content; or add placeholder dirs |
| **data/private** | Add to `.gitignore` if intended excluded |
| **docker/** | Per PRD §9; optional for first commit (document as future) |
| **configs/backends, configs/environments** | Optional placeholders or remove from 03 |
| **data/testdata/expected/** | Exists as `ppox_panel_expected.yaml` in variants/; 03’s `expected/` may be redundant |

---

## 6. Files to include in first commit

**Source:** `src/psge/**/*.py` (all 31 files)  
**Config:** `pyproject.toml`, `configs/default.yaml`  
**Knowledge:** `knowledge/ppox/sites.yaml`  
**Tests:** `tests/*.py`, `conftest.py`  
**Data (minimal):** `data/testdata/variants/ppox_panel.yaml`, `ppox_panel_expected.yaml`, `data/public/**/.gitkeep`  
**Docs:** Root `00–09_*.md`, `README.md`, `PROGRESS.md`; `docs/*.md`, `docs/m7_examples/`  
**Scripts:** `scripts/run_logic_validation.py`  
**Root:** `.gitignore`

**Exclude:** `results/`, `.venv/`, `*.egg-info`, `data/private` (if added to .gitignore), `data/public/structures/cache` (optional), `data/public/structures/pdb/3NKS.cif` (optional — or keep for reproducibility).

---

*Review complete. Proposed steps applied (03 updated, .gitignore updated, placeholder dirs added).*
