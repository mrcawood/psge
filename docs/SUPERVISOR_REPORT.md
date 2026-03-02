# PSGE Supervisor Report

**Date:** 2026-02-28  
**Scope:** Implementation status and alignment with supervisor guidance  
**Structure source:** PDB-first (3NKS)  
**WT reference:** 3NKS (human PPOX + FAD + inhibitor ACJ)

---

## 1. Executive summary

PSGE Phase 1.5 is now aligned with the supervisor’s guidance on defensibility, evidence-based reasoning, and caution. The report is:

- **PDB-first** using 3NKS experimental structure
- **3D Å-based** with real FAD/inhibitor/active-site distances
- **Cofactor-oriented** rather than “substrate binding”
- **Self-excluded** site distances (no 0.0 Å artifact)
- **Explicit about thresholds** and rule firing logic
- **Cautious in wording** (“plausible,” “does not establish functional impact”)
- **Evidence-gated secondaries** (no secondary without supporting evidence)

---

## 2. Changes implemented (per supervisor feedback)

### 2.1 Distance and membership fixes

| Issue | Fix |
|-------|-----|
| `min_dist_to_site_residues_angstrom: 0.0` artifact (self-comparison) | Exclude mutated residue from site-distance calculation; rename to `min_dist_to_active_site_residue_atoms_angstrom_excl_self` |
| Missing FAD/inhibitor distances | Compute and report `min_dist_to_fad_atoms_angstrom`, `min_dist_to_inhibitor_atoms_angstrom` (ACJ in 3NKS) |
| Membership hidden as distance | Add explicit booleans: `is_in_fad_residue_set`, `is_in_active_site_residue_set` |

### 2.2 Cofactor rule and precedence

| Change | Implementation |
|--------|----------------|
| Prioritize cofactor over active-site | `cofactor_contact` (≤ 6 Å) fires before `active_site_contact` (≤ 8 Å) |
| Cofactor label for R59W | `cofactor_binding_perturbation` with FAD/inhibitor distances |
| Fallback when ligands missing | `is_in_fad_residue_set` with “low (membership-only)” confidence |

### 2.3 Targeting region and secondaries

| Change | Implementation |
|--------|----------------|
| Active-site secondary-only in targeting region | In targeting region: `active_site_contact` can only be secondary; primary remains folding/unknown |
| Evidence required for secondaries | Each secondary must have ≥1 concrete evidence item; otherwise not emitted |
| Default branch evidence | When primary = `unknown_mechanism`, evidence table built from context (no empty Evidence) |

### 2.4 Interpretation and defensibility

| Change | Implementation |
|--------|----------------|
| Avoid implying causality | “This is consistent with a potential cofactor-environment perturbation, but does not establish functional impact.” |
| Explicit residue and structure | “Residue 59 lies within 4.9 Å of FAD atoms (3NKS reference)...” |
| Auditable thresholds | `contact_threshold_angstrom: 6.0`, `near_threshold_angstrom: 8.0` in Evidence; provenance-tracked in `run_manifest.json` |
| Decision trace | `rule: cofactor_contact (≤ 6 Å) → cofactor_binding_perturbation` |

### 2.5 Report framing

| Change | Implementation |
|--------|----------------|
| Context and limitations first | “Important context and limitations (*read first*)” section at top of report |
| Scope and disclaimers | Research-grade, non-clinical; no diagnosis, pathogenicity, or risk; signals as evidence, not proof; mock/placeholder warnings; static structure only; mechanism labels suggestive |

---

## 3. Example outputs

### 3.1 R59W (cofactor-binding perturbation)

**Primary:** cofactor_binding_perturbation — **Confidence:** plausible

**Interpretation:** Residue 59 lies within 4.9 Å of FAD atoms (3NKS reference) and 8.4 Å of the bound inhibitor; this is consistent with a potential cofactor-environment perturbation, but does not establish functional impact.

**Evidence:**
- contact_threshold_angstrom: 6.0  
- near_threshold_angstrom: 8.0  
- min_dist_to_fad_atoms_angstrom: 4.87  
- min_dist_to_inhibitor_atoms_angstrom: 8.41  
- is_in_fad_residue_set: True  
- min_dist_to_active_site_residue_atoms_angstrom_excl_self: 3.78  

**Decision trace:** `rule: cofactor_contact (≤ 6 Å) → cofactor_binding_perturbation`

**Backend:** structure_backend: pdb, stability_backend: mock

---

### 3.2 I12T (unknown, with secondaries)

**Primary:** unknown_mechanism — **Confidence:** low  
**Secondary hypotheses:** targeting_signal_perturbation, cofactor_binding_perturbation

**Interpretation:** Insufficient evidence for specific mechanism; no rule matched.

**Evidence (each secondary has supporting evidence):**
- in_targeting_region: True  
- pos: 12  
- n_terminal_targeting_signal_end: 28  
- min_dist_to_fad_atoms_angstrom: 4.32  
- min_dist_to_inhibitor_atoms_angstrom: 15.11  
- is_in_fad_residue_set: True  

**Decision trace:** `rule: default_structural → unknown_mechanism (low confidence)`

**Rationale:** I12T is in the targeting region (res 12); without real FoldX ΔΔG, primary remains unknown. Targeting and cofactor are secondary hypotheses with explicit evidence. The cofactor secondary reflects *cofactor-environment proximity* (4.32 Å to FAD), not a claim of binding-affinity or kinetic perturbation—see [Appendix D: Taxonomy definitions](#appendix-d-taxonomy-definitions).

---

## 4. Current limitations (unchanged)

| Backend | Status | Impact |
|---------|--------|--------|
| Stability | mock | ΔΔG not real; folding/stability class not grounded |
| SASA | not_implemented | No SASA-based evidence |

I12T and other destabilization cases remain `unknown` or low-confidence until real stability (and SASA) are available.

---

## 5. Expert support — what we have and what M7 is for

**Aligned with experts (Pete, Lorenzo):**
- Scope boundary: mechanistic hypotheses, not clinical prediction
- Need for domain grounding and humility
- Engaging disease expertise (Pete) and genomics context caution (Lorenzo)

**Not yet expert-endorsed (M7 goal):**
- Exact residue sets (fad_residues, active_site_residues)
- Taxonomy wording and class definitions
- Rule precedence decisions

---

## 6. Next steps (per supervisor)

1. **Implement real SASA** — Evidence layer for surface/buried residues.
2. **Implement real FoldX ΔΔG** — Ground folding/stability hypotheses.
3. **Keep destabilization low/unknown** until those backends are live.
4. **Schedule M7 with Pete** — Sanity-check taxonomy labels, site definitions, and alignment with his mental model.

---

## 7. Test status

- **25 tests passing**
- Panel expectations updated for Phase 1.5 taxonomy
- R59W and I12T outputs validated against supervisor acceptance criteria

---

## 8. Files touched

- `src/psge/backends/context.py` — Context mapping, self-exclusion, ligand distances  
- `src/psge/utils/pdb_distances.py` — FAD/ACJ atom extraction, 3D distance computation  
- `src/psge/pipeline/mechanism.py` — Cofactor/active-site rules, secondaries, evidence gating, interpretation text  
- `src/psge/core/models.py` — ContextFeatures (membership, thresholds, n_terminal_targeting_signal_end)  
- `src/psge/reporting/summary.py` — Important context and limitations section  
- `src/psge/reporting/manifest.py` — Mechanism thresholds in run_manifest for provenance  

---

## Appendix A: Residue definitions (sites.yaml)

**FAD / cofactor-binding residues** (UniProt P50336, 1-based):  
`[9, 10, 11, 12, 13, 14, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]`

**Active-site / substrate-pocket residues** (overlaps FAD; acifluorfen binding site in 3NKS):  
`[55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]`

**Targeting region:** residues 1–28 (`n_terminal_targeting_signal_end: 28`)

*Source: Qin et al. 2011 FASEB J, 3NKS structure. Subject to M7 review.*

---

## Appendix B: Rule precedence (6 steps)

1. **non_structural_track** → `truncation_misexpression` (truncation/splice variants; structural steps skipped)
2. **targeting_signal_region** → add `targeting_signal_perturbation` to secondaries only (never primary by default)
3. **cofactor_contact** (≤ 6 Å to FAD/inhibitor or FAD membership fallback) → `cofactor_binding_perturbation` (or secondary if in targeting region)
4. **active_site_contact** (≤ 8 Å to other site residues, excluding self) → `active_site_region_perturbation` (or secondary if in targeting region)
5. **stability_or_core** (ΔΔG ≥ 2.0 or destabilizing flags) → `folding_stability_hydrophobic_core`
6. **default** → `unknown_mechanism` (with evidence-gated secondaries)

---

## Appendix C: Mock / not implemented

| Component | Status | Note |
|-----------|--------|------|
| **Stability** | mock | ΔΔG values are placeholders; FoldX integration not yet implemented. Folding/stability labels not grounded in real computation. |
| **SASA** | not_implemented | Solvent-accessible surface area not computed; buriedness/surface signals unavailable. |

Until stability and SASA are real, `folding_stability_hydrophobic_core` and SASA-dependent logic should be treated as placeholder. Variants like I12T remain `unknown` or low-confidence until FoldX (or equivalent) is live.

---

## Appendix D: Taxonomy definitions

Mechanism labels are defined in `docs/PHASE1_5_REMAP.md`. Key definition for defensibility:

**`cofactor_binding_perturbation`** — Variant is located in or near the cofactor environment (FAD/inhibitor region); potential cofactor-related perturbation is plausible. **Does not infer binding affinity or kinetic mechanism.** Evidence: 3D Å proximity to FAD/inhibitor atoms or membership in curated FAD residue set. Used for both primary (e.g. R59W) and secondary (e.g. I12T) hypotheses when structural evidence supports cofactor-environment proximity.

Evidence items report *structural context* only (distances, thresholds, membership); they do not imply functional impact.

---

*Report generated for supervisor review. See Appendices A–C for residue lists, rule precedence, and mock/not-implemented status.* PSGE: Personal Structural Genomics Engine. Research-grade, non-clinical.*
