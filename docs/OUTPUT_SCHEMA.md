# PSGE Output Schema

**Purpose:** Structure and meaning of PSGE outputs (Phase 1.6d).

---

## 1. summary.json

Machine-readable output per variant. Written to `results/<variant>/summary.json` (or panel subdirs).

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `variant` | string | Input variant (e.g. `R59W`) |
| `input_hash` | string | SHA-256 of variant string |
| `mechanism_class` | string | Primary mechanism class |
| `confidence` | string | `plausible`, `low`, `low (membership-only)` |
| `evidence_table` | array | Enriched evidence rows (see below) |
| `evidence_summary` | object | Report-level evidence basis (Phase 1.6d) |
| `stability_signal_band` | string | FoldX band when applicable |
| `foldx_provenance` | object | FoldX run metadata when applicable |
| `interpretation` | string | Human-readable interpretation text |
| `limits` | string | Explicit limits and caveats |
| `decision_trace` | array | Rules that fired |
| `secondary_hypotheses` | array | Additional plausible mechanism classes |
| `skipped_steps` | array | Steps skipped and reason |
| `backend_status` | object | Backend status |
| `tool_versions` | object | `{"psge": "0.1.0"}` |

### evidence_table (Phase 1.6d)

Each row includes:

| Field | Description |
|-------|-------------|
| `signal` | Evidence name |
| `value` | Numeric, boolean, or string |
| `evidence_type` | e.g. `structural_proximity`, `foldx_ddg`, `sasa_context`, `curated_site_membership` |
| `evidence_tier` | e.g. `pdb_context_only`, `foldx_stability_prediction` |
| `species_context` | Usually `human` |
| `source_id` | e.g. `3NKS`, `FoldX_5_on_3NKS`, `sites_yaml_provisional` |
| `interpretation` | Optional band or caveat |

### evidence_summary

| Field | Description |
|-------|-------------|
| `overall_evidence_basis` | List of tiers present |
| `highest_evidence_tier` | Highest tier in this report |
| `species_context` | `human` for current PPOX panel |
| `clinical_interpretation` | Always `false` |
| `sources` | Minimal structured source entries |
| `threshold_policy` | e.g. `provisional_bands_v1_6d` |

### backend_status

| Field | Values | Meaning |
|-------|--------|---------|
| `structure_backend` | `pdb`, `mock`, `esmfold` | WT structure source |
| `stability_backend` | `mock`, `foldx`, `foldx_failed`, `not_available` | Stability backend |
| `delta_metrics` | `real_rmsd` | RMSD computation |
| `sasa` | `biopython_shrake_rupley`, `not_implemented` | SASA backend |
| `foldx_version` | string | When FoldX used |

---

## 2. run_manifest.json

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 UTC |
| `input` | string | Variant string |
| `input_hash` | string | SHA-256 of variant |
| `config_hash` | string | Hash of config |
| `compute_profile` | string | `local` |
| `backend_status` | object | Same as summary.json |
| `mechanism_thresholds` | object | Contact/near Å thresholds + stability bands |
| `foldx_provenance` | object | Present when FoldX ran |

---

## 3. report.md

Sections:

- Important context and limitations
- Evidence basis (report-level tiers)
- Mechanism hypothesis (class, confidence, secondaries, stability band)
- Classifier decision trace
- Interpretation (variant-specific conservative wording when defined)
- Evidence (rows with type/tier metadata)
- FoldX provenance (when applicable)
- Limits
- Backend status
- Skipped steps

SASA: local residue and patch values only. `sasa_source_pairing: incomparable` when WT is PDB and mutant is predicted.
