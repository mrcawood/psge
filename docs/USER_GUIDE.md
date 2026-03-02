# PSGE User Guide

**Purpose:** Run PSGE, understand outputs, and interpret reports.

---

## 1. Installation

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Optional: `pip install -e ".[esmfold]"` for ESMFold structure prediction.

---

## 2. Running a single variant

```bash
.venv/bin/psge run --variant R59W --results-dir results/
```

Output goes to `results/R59W/` (or `results/<variant>/` if you pass a different variant).

### Structure source (critical for PPOX)

PSGE supports two structure sources:

| Option | Meaning | Use case |
|--------|---------|----------|
| `pdb_first` (default) | WT from 3NKS (human PPOX + FAD + inhibitor); mutant from prediction or mock | Best for PPOX; real 3D Å distances to FAD/inhibitor |
| `predict_first` | WT and mutant from ESMFold or mock | When no suitable PDB exists |

```bash
# PDB-first (recommended for PPOX)
.venv/bin/psge run --variant R59W --structure-source pdb_first --results-dir results/

# Predict-first (ESMFold/mock)
.venv/bin/psge run --variant R59W --structure-source predict_first --results-dir results/
```

---

## 3. Running the panel

Run all variants in the curated panel:

```bash
.venv/bin/psge run --panel data/testdata/variants/ppox_panel.yaml --results-dir results/
```

Each variant gets its own subdirectory under `results/` (e.g. `results/R59W/`, `results/I12T/`).

---

## 4. Configuration

### Config file

Default: `configs/default.yaml`. Override with `--config`:

```bash
.venv/bin/psge run --variant R59W --config path/to/config.yaml --results-dir results/
```

### Config fields

| Field | Meaning | Example |
|-------|---------|---------|
| `gene` | Gene symbol | `PPOX` |
| `structure_backend` | AlphaFold / ESMFold (when predict_first) | `alphafold`, `esmfold` |
| `stability_backend` | FoldX / mock | `foldx`, `mock` |
| `structure_source` | `pdb_first` or `predict_first` | `pdb_first` |
| `results_dir` | Default output directory | `results` |

---

## 5. Output files

For each variant, PSGE writes to `results/<variant>/`:

| File | Content |
|------|---------|
| `summary.json` | Machine-readable: mechanism class, evidence, confidence, decision trace |
| `report.md` | Human-readable report with interpretation and evidence |
| `run_manifest.json` | Provenance: timestamp, input hash, config hash, backend status, thresholds |

See [OUTPUT_SCHEMA.md](OUTPUT_SCHEMA.md) for the `summary.json` structure.

---

## 6. Understanding the report

### Mechanism classes (Phase 1.5)

| Class | Meaning |
|-------|---------|
| `cofactor_binding_perturbation` | Variant near FAD/inhibitor; potential cofactor-environment perturbation |
| `active_site_region_perturbation` | Variant near substrate-binding region |
| `folding_stability_hydrophobic_core` | Stability analysis suggests folding/core destabilization |
| `targeting_signal_perturbation` | Variant in N-terminal targeting region (often secondary only) |
| `truncation_misexpression` | Truncation or splice; no structural modeling |
| `unknown_mechanism` | No rule matched; low confidence |

### Backend status

The report and manifest show `backend_status`:

| Backend | `mock` / `not_implemented` | Real |
|---------|----------------------------|------|
| `structure_backend` | mock (predicted structures) | `pdb` (3NKS) |
| `stability_backend` | mock (ΔΔG placeholder) | `foldx` |
| `delta_metrics` | — | `real_rmsd` |
| `sasa` | `not_implemented` | — |

**When stability is mock:** Folding/stability labels are not grounded in real computation. Variants like I12T may remain `unknown` until FoldX is integrated.

### Important context and limitations

Every report starts with a context section. Key points:

- Research-grade, non-clinical; no diagnosis or pathogenicity
- Evidence is structural context; does not establish functional impact
- Mock/placeholder values must not be used for scientific conclusions
- Static structure only; no expression, turnover, or dynamics

---

## 7. Limits and non-goals

- **No clinical prognosis**, penetrance, or pathogenicity
- **No medical advice** or phenotype prediction
- **Static structure** only; no MD, expression, or protein–protein interactions
- **PPOX-focused**; taxonomy and knowledge are gene-specific

---

## 8. Further reading

- [PHASE1_5_REMAP.md](PHASE1_5_REMAP.md) — Current taxonomy and rules
- [SUPERVISOR_REPORT.md](SUPERVISOR_REPORT.md) — Status, evidence, appendices
- [OUTPUT_SCHEMA.md](OUTPUT_SCHEMA.md) — summary.json structure
