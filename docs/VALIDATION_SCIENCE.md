# PSGE Scientific Validation

**Purpose:** Real metrics, curated knowledge, mechanism hypotheses, and limitations.

**Scope:** PPOX (UniProt P50336). Non-clinical, research-grade. Phase 1.6e.

---

## Panel (pdb_first + FoldX expectations)

See `data/testdata/variants/ppox_panel_expected_pdb_first_foldx.yaml` for enforced FoldX behavior when the binary is available. Mock/`predict_first` expectations remain in `test_panel_t2.py`.

| Variant | Primary (pdb_first + FoldX) | Stability band |
|---------|----------------------------|----------------|
| R59W | cofactor_binding_perturbation | borderline_destabilizing |
| I12T | folding_stability_hydrophobic_core | destabilizing |
| R152C | unknown_mechanism | weak_to_moderate |
| G358R | folding_stability_hydrophobic_core | extreme_destabilizing_requires_audit |
| 78insC / IVS2-2 | truncation_misexpression | FoldX skipped |

---

## Real metrics

### RMSD
BioPython Superimposer on WT vs mutant structures. `delta_metrics: real_rmsd`.

### SASA (Phase 1.6a, local-only)
BioPython Shrake-Rupley. Reports residue-level and 8 Å patch SASA on WT; residue delta only when `sasa_source_pairing: same_backend`. Does not report global `sasa_total_wt/mut` deltas when structures are incomparable (e.g. `pdb_first`).

### Stability (Phase 1.6c–1.6d, FoldX)
Protein-only repaired 3NKS input. FAD/ACJ excluded from FoldX run. `configs/default.yaml` `foldx_path` or `FOLDX_PATH`.

#### Provisional ΔΔG bands (Phase 1.6d)

| Band | ΔΔG (kcal/mol) |
|------|----------------|
| none_or_weak | &lt; 1.0 |
| weak_to_moderate | 1.0 – 2.0 |
| borderline_destabilizing | 2.0 – 2.5 |
| destabilizing | 2.5 – 5.0 |
| strong_destabilizing | 5.0 – 10.0 |
| extreme_destabilizing_requires_audit | ≥ 10.0 |

Bands are provisional. Not calibrated to literature in Phase 1.6d.

#### Classifier policy
- Rule precedence unchanged: cofactor contact before stability primary.
- `folding_stability_hydrophobic_core` primary only when FoldX succeeded and band is at least `destabilizing`, with audit for extreme values.
- `borderline_destabilizing` and `weak_to_moderate` may appear as secondary or evidence only.
- Mock ΔΔG never drives primary classification.

---

## Curated PPOX knowledge

**Reference:** Qin et al. (2011); structure 3NKS.

FAD/active-site residue lists in `sites.yaml` are provisional. Pete has not formally endorsed exact lists.

Targeting: N-terminal region 1–28 used in rules; internal targeting signals exist in literature and are not fully modeled.

---

## Evidence tiers (Phase 1.6d/1.6e)

Reports distinguish computed tiers from curated external evidence.

| Tier | Source |
|------|--------|
| not_applicable | Skipped or inapplicable evidence |
| variant_class_rule | Preflight truncation/splice routing (78insC, IVS2-2) |
| pdb_context_only | 3NKS, SASA, curated sites (`PDB_3NKS`, `SASA_BIOPYTHON_3NKS`) |
| foldx_stability_prediction | FoldX BuildModel ΔΔG (`FOLDX_5_3NKS`) |
| literature_mechanistic | Curated bibliography (e.g. Qin 2011 R59W discussion) |
| functional_assay | Curated functional data (e.g. Meissner 1996 R59W) |

Registry: `data/sources/ppox_sources.yaml`. Per-variant map: `data/sources/ppox_variant_evidence.yaml`. Literature sources use `verification_status` (`bibliography_verified` unless primary paper text was checked). See `docs/PHASE1_6E_EVIDENCE_SOURCE_LAYER.md`.

---

## Limitations

- Static structure only; no expression, splicing, or clinical inference.
- FoldX ΔΔG is not cofactor binding, catalytic activity, or clinical outcome.
- Inhibitor (ACJ) proximity does not prove substrate binding.
- Unknown/low-confidence output is acceptable.
