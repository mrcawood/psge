# Phase 1.5 Recalibration — Taxonomy, Rules, Metrics

**Purpose:** Align PSGE with domain literature (ClinGen, PDB, FAD/cofactor evidence). Replace sequence-distance heuristics with real 3D metrics. Implement PDB-first for PPOX.

---

## 1. New Taxonomy

| Class | Definition |
|-------|------------|
| `cofactor_binding_perturbation` | Variant is located in or near the cofactor environment (FAD/inhibitor region); potential cofactor-related perturbation is plausible. **Does not infer binding affinity or kinetic mechanism.** Requires real 3D proximity to FAD atoms or curated cofactor-contact residues (Å). |
| `active_site_region_perturbation` | Variant perturbs substrate-binding region. Use if separable from cofactor; otherwise merge with `cofactor_binding_perturbation` for Phase 1.5. |
| `folding_stability_hydrophobic_core` | Variant affects folding, stability, or hydrophobic core. Requires real FoldX ΔΔG above threshold, OR buriedness (low SASA) plus structural perturbation signal. |
| `targeting_signal_perturbation` | Variant in N-terminal targeting region. **Secondary hypothesis only** unless explicit external evidence. |
| `truncation_misexpression` | Truncation or splice variant; no structural modeling. |
| `unknown_mechanism` | Default when no rule matches. Low confidence. |

---

## 2. New Rule Precedence

1. **non_structural_track** → `truncation_misexpression`

2. **targeting_signal_region_hit** → add `secondary_hypotheses += [targeting_signal_perturbation]`  
   - Do **not** force as primary by default.

3. **cofactor_contact** → `cofactor_binding_perturbation`  
   - Requires real 3D proximity (Å) to FAD atoms OR curated contact set derived from PDB.

4. **active_site_contact** → `active_site_region_perturbation`  
   - Requires real 3D proximity (Å).

5. **stability_or_core** → `folding_stability_hydrophobic_core`  
   - Requires either:
     - Real FoldX ΔΔG above threshold, OR
     - Residue buriedness (low SASA) plus supporting structural perturbation signal.

6. **default** → `unknown_mechanism`  
   - Keep `secondary_hypotheses` to record overlaps (e.g., cofactor contact + high ΔΔG).

---

## 3. Panel Table (Expected Outcomes)

| Variant | Expected Primary | Expected Secondary |
|---------|------------------|--------------------|
| R59W | cofactor_binding_perturbation | (none) |
| I12T | folding_stability_hydrophobic_core | targeting_signal_perturbation |
| R152C | folding_stability_hydrophobic_core | (none) |
| G358R | folding_stability_hydrophobic_core | (none) |
| 78insC | truncation_misexpression | (none) |
| IVS2-2 a→c | truncation_misexpression | (none) |

---

## 4. Metric Contract (Replace Sequence-Distance)

### Current (broken)

- `distance_fad`: sequence distance in residues (min |pos - r|)
- `distance_active_site`: sequence distance in residues
- Threshold: ≤ 3 residues treated as "near"

**Code path:**  
- `backends/context.py`: `_min_distance_to_residues(pos, residues)` → residue index difference  
- `pipeline/mechanism.py`: `_near_fad_or_active_site(context)` → `distance_fad <= 3 or distance_active_site <= 3`

### Required (Phase 1.5) — implemented

| Metric | Definition | Contact / Near thresholds |
|--------|------------|---------------------------|
| `min_dist_to_fad_atoms_angstrom` | Minimum 3D distance (Å) from mutation residue to FAD atoms (HETATM) | contact: ≤ 6 Å; near: ≤ 8 Å |
| `min_dist_to_inhibitor_atoms_angstrom` | ACJ (acifluorfen in 3NKS) | contact: ≤ 6 Å |
| `min_dist_to_active_site_residue_atoms_angstrom` | To other site residues (excluding self) | near: ≤ 8 Å |
| `is_in_fad_residue_set` | Membership in curated FAD residue list | fallback when ligand atoms missing |
| `is_in_active_site_residue_set` | Membership in curated active-site list | supporting evidence |

**Near-site rules now use 3D Å distance**, not sequence-distance. Membership in residue lists remains supporting evidence only.

---

## 5. PDB-First Requirements

Structure source preference chain:

1. **Local bundled PDBs** for PPOX (start with 3NKS WT)
2. **RCSB fetch** (cached into `data/public/structures/`)
3. **Predicted structure fallback** (ESMFold / AlphaFold later)

Config knob:

- `structure_source: pdb_first | predict_first`
- Default for PPOX: `pdb_first`

Store ligand atoms (FAD, inhibitors) when present; cofactor proximity is central.

---

## 6. Current State (Surgical Replacement Targets)

### sites.yaml (current)

```yaml
fad_residues: [9, 10, 11, 12, 13, 14, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
active_site_residues: [55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]
n_terminal_targeting_signal_end: 28
n_terminal_targeting_minimal_end: 17
```

### Code path for distance_fad / distance_active_site

1. **`backends/context.py`**  
   - `map_context()` loads `sites.yaml` via `load_ppox_sites()`  
   - Calls `_min_distance_to_residues(pos, fad_residues)` → sequence distance  
   - Calls `_min_distance_to_residues(pos, active_residues)` → sequence distance  
   - Returns `ContextFeatures(distance_fad=..., distance_active_site=..., ...)`

2. **`_min_distance_to_residues(pos, residues)`**  
   - `return float(min(abs(pos - r) for r in residues))`  
   - Pure sequence index difference; no PDB coordinates used.

3. **`pipeline/mechanism.py`**  
   - `_near_fad_or_active_site(ctx)` → `ctx.distance_fad <= 3 or ctx.distance_active_site <= 3`  
   - Uses these values for the `near_fad_or_active_site` rule.

### Replacement plan

- Add `utils/pdb_distances.py` (or equivalent): compute min 3D distance from variant residue to FAD atoms, inhibitor atoms, curated site residue atoms.
- Extend `ContextFeatures` with: `min_dist_to_fad_atoms_angstrom`, `min_dist_to_inhibitor_atoms_angstrom`, `min_dist_to_curated_site_residues_angstrom`.
- Retire or demote `distance_fad` and `distance_active_site` (sequence-based) to optional supporting evidence.
- Classifier: use Å-based contact thresholds instead of sequence-distance.

---

## 7. Implementation Priorities (Order)

1. Add PDB-first loading for 3NKS (local file + caching).
2. Implement real 3D distance metrics (Å) for mutation residue to FAD atoms, inhibitor atoms, curated residue sets.
3. Implement SASA (real).
4. Integrate FoldX ΔΔG (real).
5. Re-run panel; update validation language: "logic validated" vs "scientifically grounded."
