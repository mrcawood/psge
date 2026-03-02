# PSGE Output Schema

**Purpose:** Structure and meaning of PSGE outputs.

---

## 1. summary.json

Machine-readable output per variant. Written to `results/<variant>/summary.json`.

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `variant` | string | Input variant (e.g. `R59W`) |
| `input_hash` | string | SHA-256 of variant string |
| `mechanism_class` | string | Primary mechanism class |
| `confidence` | string | `plausible`, `low`, `low (membership-only)` |
| `evidence_table` | array | List of `{signal, value}` evidence items |
| `interpretation` | string | Human-readable interpretation text |
| `limits` | string | Explicit limits and caveats |
| `decision_trace` | array | Rules that fired (for transparency) |
| `secondary_hypotheses` | array | Additional plausible mechanism classes |
| `skipped_steps` | array | Steps skipped and reason |
| `backend_status` | object | Backend status (see below) |
| `tool_versions` | object | `{"psge": "0.1.0"}` |

### evidence_table

Each item has:
- `signal` (string): Evidence name (e.g. `min_dist_to_fad_atoms_angstrom`)
- `value`: Numeric, boolean, or string

Common signals:

| Signal | Description |
|--------|-------------|
| `contact_threshold_angstrom` | Cofactor contact threshold (6.0 Å) |
| `near_threshold_angstrom` | Active-site near threshold (8.0 Å) |
| `min_dist_to_fad_atoms_angstrom` | Min 3D distance to FAD atoms |
| `min_dist_to_inhibitor_atoms_angstrom` | Min 3D distance to inhibitor (ACJ) |
| `min_dist_to_active_site_residue_atoms_angstrom_excl_self` | Min distance to other site residues |
| `is_in_fad_residue_set` | Residue in FAD residue set |
| `is_in_active_site_residue_set` | Residue in active-site set |
| `in_targeting_region` | Residue in targeting region |
| `pos` | Variant position (UniProt) |
| `n_terminal_targeting_signal_end` | End of targeting region (from knowledge) |

### backend_status

| Field | Values | Meaning |
|-------|--------|---------|
| `structure_backend` | `pdb`, `mock`, `esmfold` | WT structure source |
| `stability_backend` | `mock`, `foldx` | Stability computation |
| `delta_metrics` | `real_rmsd` | RMSD from real or mock |
| `sasa` | `not_implemented` | SASA not yet implemented |

---

## 2. run_manifest.json

Provenance and run metadata. Written to `results/<variant>/run_manifest.json`.

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 UTC |
| `input` | string | Variant string |
| `input_hash` | string | SHA-256 of variant |
| `config_hash` | string | Hash of config (gene, backends, structure_source) |
| `compute_profile` | string | `local` |
| `backend_status` | object | Same as summary.json |
| `mechanism_thresholds` | object | `contact_threshold_angstrom`, `near_threshold_angstrom` |

---

## 3. report.md

Human-readable report. Markdown with:

- Important context and limitations (read first)
- Mechanism hypothesis (class, confidence, secondaries)
- Classifier decision trace
- Interpretation
- Evidence (bulleted list)
- Limits
- Backend status
- Skipped steps

See `results/R59W/report.md` for an example.
