# Contributing to PSGE

**Purpose:** How to run tests, add backends, change mechanism rules, and work with domain knowledge.

---

## 1. Repo layout

See [03_DIRECTORY_STRUCTURE.md](../03_DIRECTORY_STRUCTURE.md). Key paths:

| Path | Purpose |
|------|---------|
| `src/psge/cli.py` | CLI entry point |
| `src/psge/pipeline/` | Stages (stages.py) and orchestrator (runner.py) |
| `src/psge/backends/` | Structure, stability, alignment, sequence, context |
| `src/psge/pipeline/mechanism.py` | Rules-based classifier |
| `src/psge/knowledge/ppox/` | PPOX domain config (`sites.yaml`) |
| `src/psge/core/models.py` | Data types (VariantRecord, ContextFeatures, etc.) |

---

## 2. Running tests

```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest tests/ -v
```

Tests cover: preflight routing, sequence, structure cache, alignment, stability, context, mechanism classifier, panel, CLI.

**Lint:** `ruff check src/ tests/` (included in CI).

---

## 3. Adding a stability backend (e.g. FoldX)

1. Add a function in `src/psge/backends/stability.py` with signature:

   ```python
   def _foldx_stability(
       struct_pair: StructurePair,
       pos: int | None,
       config: Config,
   ) -> StabilityResult:
       ...
   ```

2. Update `get_stability_backend()` to return it when `backend == "foldx"`.
3. Set `backend_status["stability_backend"] = "foldx"` when used (e.g. in `stages.py` or via `backend_status`).
4. Update `configs/default.yaml` and `utils/backend_status.py` if needed.

---

## 4. Adding or changing mechanism rules

Rules live in `src/psge/pipeline/mechanism.py`. Order matters:

1. `non_structural_track` → truncation
2. Targeting → secondary only
3. `cofactor_contact` → cofactor_binding_perturbation
4. `active_site_contact` → active_site_region_perturbation
5. `stability_or_core` → folding_stability_hydrophobic_core
6. `default` → unknown_mechanism

To add a rule:

- Add a predicate (e.g. `_new_rule_contact()`)
- Add evidence builder and interpretation helpers
- Insert in `classify()` at the correct precedence
- Update `docs/PHASE1_5_REMAP.md` and `docs/SUPERVISOR_REPORT.md` appendices

Thresholds: `CONTACT_ANGSTROM = 6.0`, `NEAR_ANGSTROM = 8.0`. They are emitted in `run_manifest.json` for provenance.

---

## 5. Domain knowledge (sites.yaml)

`src/psge/knowledge/ppox/sites.yaml` defines:

- `fad_residues`: FAD-binding residues (UniProt 1-based)
- `active_site_residues`: Substrate-pocket residues
- `n_terminal_targeting_signal_end`: End of targeting region

Loaded by `utils/knowledge_loader.py`. Context mapping (`backends/context.py`) and the classifier use these. Changes affect mechanism assignment—validate with panel tests.

---

## 6. Backend status

`utils/backend_status.py` returns a dict used in reports and manifests. Update when adding backends so users see real vs mock. See [USER_GUIDE.md](USER_GUIDE.md) §6.

---

## 7. Documentation

- Update [PHASE1_5_REMAP.md](PHASE1_5_REMAP.md) when taxonomy or rules change.
- Update [OUTPUT_SCHEMA.md](OUTPUT_SCHEMA.md) if output structure changes.
- Update [SUPERVISOR_REPORT.md](SUPERVISOR_REPORT.md) appendices for residue lists and rule precedence.
