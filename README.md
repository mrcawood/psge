# PSGE — Personal Structural Genomics Engine

Reproducible HPC + AI workflow for mechanistic, non-clinical analysis of PPOX variants.

## Phase 1: PPOX Mechanism Panel MVP

Given a PPOX variant, produce the most plausible mechanism class with evidence and explicit uncertainty.

---

## Quick Start

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/psge run --variant R59W --results-dir results/
```

Output: `results/R59W/summary.json`, `results/R59W/report.md`, `results/R59W/run_manifest.json`.

---

## Usage

### Single variant

```bash
.venv/bin/psge run --variant R59W --results-dir results/
```

### Panel (all curated variants)

```bash
.venv/bin/psge run --panel data/testdata/variants/ppox_panel.yaml --results-dir results/
```

### Structure source

For PPOX, `pdb_first` uses the 3NKS experimental structure (human PPOX + FAD + inhibitor) and produces real 3D Å distances. This is the default.

```bash
.venv/bin/psge run --variant R59W --structure-source pdb_first --results-dir results/
```

Use `predict_first` for ESMFold/mock when no suitable PDB exists.

### Config

```bash
.venv/bin/psge run --variant R59W --config configs/default.yaml --results-dir results/
```

See `configs/default.yaml` for options. Full usage: [docs/USER_GUIDE.md](docs/USER_GUIDE.md).

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | **Start here** — installation, usage, outputs, interpretation |
| [docs/OUTPUT_SCHEMA.md](docs/OUTPUT_SCHEMA.md) | summary.json structure |
| [docs/PHASE1_5_REMAP.md](docs/PHASE1_5_REMAP.md) | Current taxonomy and rules |
| [01_PRD.md](01_PRD.md) | Product requirements |
| [02_ARCHITECTURE.md](02_ARCHITECTURE.md) | Pipeline architecture |
| [03_DIRECTORY_STRUCTURE.md](03_DIRECTORY_STRUCTURE.md) | Repository layout |
| [04_VARIANT_PANEL.md](04_VARIANT_PANEL.md) | Validation panel |
| [05_MECHANISM_TAXONOMY.md](05_MECHANISM_TAXONOMY.md) | Mechanism classes |
| [08_ARCHITECT_DESIGN.md](08_ARCHITECT_DESIGN.md) | Interfaces and contracts |
| [09_PLAN.md](09_PLAN.md) | Implementation plan |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Contributor guide |

---

## Tests

```bash
.venv/bin/pytest tests/ -v
```

**CI** (GitHub Actions): Tests run on push/PR to main/master. Jobs: pytest (Python 3.10, 3.12), ruff lint, CLI smoke test.

---

## Logic validation

Run full panel and generate `docs/VALIDATION_LOGIC.md`:

```bash
.venv/bin/python scripts/run_logic_validation.py
```

---

## Non-goals

- Clinical prognosis, penetrance, or pathogenicity
- Medical advice or phenotype prediction
