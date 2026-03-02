# Documentation Assessment

**Date:** 2026-02-28  
**Purpose:** First-class documentation review for PSGE as a serious repo artifact.

---

## 1. Current documentation inventory

| Doc | Audience | Purpose | Status |
|-----|----------|---------|--------|
| README.md | All | Entry point, quick start | Minimal; functional |
| 00_OVERVIEW.md | Domain experts, agents | Context, scope, Pete/Lorenzo guidance | Good |
| 01_PRD.md | Product, eng | Requirements, outputs, FRs | Complete |
| 02_ARCHITECTURE.md | Eng | Pipeline DAG, backends | Good |
| 03_DIRECTORY_STRUCTURE.md | Eng | Repo layout | Updated |
| 04_VARIANT_PANEL.md | Validation | Panel variants, expected behavior | **Outdated** — class names from Phase 1 |
| 05_MECHANISM_TAXONOMY.md | Domain, eng | Mechanism classes | **Outdated** — substrate-binding vs cofactor |
| 06_VALIDATION_PLAN.md | QA | T1–T3 assertions | Reference |
| 07_REFERENCES.md | Domain | Literature | Reference |
| 08_ARCHITECT_DESIGN.md | Eng | Interfaces, contracts, failure modes | Strong |
| 09_PLAN.md | Eng | Milestones, sprints | Reference |
| docs/PHASE1_5_REMAP.md | Eng, domain | Phase 1.5 taxonomy, rules, metrics | **Source of truth** for current behavior |
| docs/SUPERVISOR_REPORT.md | Supervisor, Pete | Status, evidence, appendices | Strong |
| docs/VALIDATION_LOGIC.md | QA | Logic validation output | Generated |
| docs/VALIDATION_SCIENCE.md | QA | Scientific validation | Reference |
| docs/M7_PETE_OVERVIEW.md | Pete | M7 prep | Reference |
| docs/COMMIT_PREP_REVIEW.md | Eng | Commit prep | Reference |
| configs/default.yaml | Users | Config template | Inline comments only |

---

## 2. Gaps (user-facing)

### 2.1 No user guide

A new user (computational practitioner or domain expert) needs a single path:

- How to install and run
- Single variant vs panel
- Config options (`--structure-source`, `--results-dir`, config file)
- Output files: `summary.json`, `report.md`, `run_manifest.json` — what they contain and how to interpret
- Backend status: what "mock" means, what’s real
- Limits and caveats

**Recommendation:** Add `docs/USER_GUIDE.md` (or `docs/GETTING_STARTED.md`).

### 2.2 README is minimal

README has quick start and doc links but lacks:

- `--structure-source pdb_first` vs `predict_first` (critical for PPOX)
- Panel run: `psge run --panel data/testdata/variants/ppox_panel.yaml`
- Config file path and overrides
- Output layout (`results/<variant>/`)

**Recommendation:** Expand README with a short “Usage” section.

### 2.3 Taxonomy/panel docs inconsistent with Phase 1.5

- `05_MECHANISM_TAXONOMY.md`: Still uses "Substrate-binding impairment" and old class names.
- `04_VARIANT_PANEL.md`: Expects "substrate-binding impairment" for R59W.
- Current behavior: `cofactor_binding_perturbation`, `active_site_region_perturbation`, etc. (in `docs/PHASE1_5_REMAP.md`).

**Recommendation:** Add a note in 04/05 pointing to `docs/PHASE1_5_REMAP.md` as the current taxonomy, or update 04/05 to Phase 1.5.

### 2.4 Output schema undocumented

`summary.json` has a clear shape but no schema or field-by-field description.

**Recommendation:** Add `docs/OUTPUT_SCHEMA.md` or a section in the user guide with the JSON structure and fields.

---

## 3. Gaps (technical/contributor)

### 3.1 No contributor guide

A new contributor needs:

- Repo layout (`03_DIRECTORY_STRUCTURE`)
- How to run tests
- How to add a new backend (e.g., FoldX)
- How to add or change a mechanism rule
- Where knowledge lives (`knowledge/ppox/sites.yaml`)

**Recommendation:** Add `docs/CONTRIBUTING.md`.

### 3.2 No API reference

Module docstrings exist and refer to PRD; function docstrings vary. No generated API docs (Sphinx, pdoc).

**Recommendation:** For Phase 1, rely on `08_ARCHITECT_DESIGN.md` and code docstrings. Add Sphinx/pdoc later if the codebase grows.

### 3.3 Backend status not explained

`backend_status` in `run_manifest.json` and report is described only implicitly. Mock vs real is critical.

**Recommendation:** Document in USER_GUIDE and/or a short `docs/BACKENDS.md`.

---

## 4. Strengths

- **08_ARCHITECT_DESIGN.md**: Clear interfaces, data flow, failure modes.
- **docs/SUPERVISOR_REPORT.md**: Strong for stakeholders; appendices (residues, rules, mock status).
- **docs/PHASE1_5_REMAP.md**: Current behavior and taxonomy.
- **Code docstrings**: Modules reference PRD; key functions are described.
- **Config comments**: `configs/default.yaml` has inline notes.

---

## 5. Recommended additions (priority order)

| Priority | Doc | Purpose | Status |
|----------|-----|---------|--------|
| 1 | `docs/USER_GUIDE.md` | End-to-end usage for practitioners and domain experts | Done |
| 2 | README expansion | Usage, structure-source, panel, config, outputs | Done |
| 3 | Taxonomy sync | Point 04/05 at PHASE1_5_REMAP or update inline | Done |
| 4 | `docs/OUTPUT_SCHEMA.md` | summary.json structure and fields | Done |
| 5 | `docs/CONTRIBUTING.md` | Contributor workflow, tests, adding backends/rules | Done |

---

## 6. Doc hierarchy proposal

```
README.md              # Entry point; quick start; link to USER_GUIDE
00_OVERVIEW.md         # Context, scope (keep)
01_PRD.md              # Requirements (keep)
02_ARCHITECTURE.md     # Pipeline (keep)
03_DIRECTORY_STRUCTURE.md  # Layout (keep)
04_VARIANT_PANEL.md    # Update or redirect to Phase 1.5
05_MECHANISM_TAXONOMY.md   # Update or redirect to Phase 1.5
06–09, 99              # As-is
docs/
  USER_GUIDE.md        # NEW: primary user doc
  OUTPUT_SCHEMA.md     # NEW: summary.json structure
  CONTRIBUTING.md      # NEW: contributor guide
  PHASE1_5_REMAP.md    # Current taxonomy (keep)
  SUPERVISOR_REPORT.md # Status report (keep)
  BACKENDS.md          # Optional: backend status, mock vs real
```

---

## 7. Assessment summary

| Dimension | Grade | Notes |
|-----------|-------|------|
| **User documentation** | C+ | Quick start works; no user guide; config/outputs under-documented |
| **Technical documentation** | B | 08_ARCHITECT_DESIGN is strong; no contributor guide |
| **Consistency** | C | 04/05 out of sync with Phase 1.5 |
| **Discoverability** | B- | README points to specs; user path is unclear |
| **First-class as artifact** | B- | Good spec depth; user/contributor paths need work |

**Verdict:** Documentation improved. USER_GUIDE, README, taxonomy sync, OUTPUT_SCHEMA, and CONTRIBUTING implemented (2026-02-28).
