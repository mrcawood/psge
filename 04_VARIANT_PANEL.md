# PPOX Phase 1.5 Variant Panel

Date: 2026-02-28

Purpose: a curated panel used to validate PSGE's routing and mechanism hypothesis outputs.

**Current taxonomy:** See [docs/PHASE1_5_REMAP.md](docs/PHASE1_5_REMAP.md) for Phase 1.5 class names and rules.

---

## Panel (from Pete's mechanism taxonomy, mapped to Phase 1.5)

### Cofactor / active-site (formerly substrate-binding impairment)
- R59W → `cofactor_binding_perturbation` (pdb_first)

### Structural destabilization
- R152C → `folding_stability_hydrophobic_core` (with real FoldX) or `unknown_mechanism` (mock)
- G358R → `folding_stability_hydrophobic_core` (with real FoldX) or `unknown_mechanism` (mock)

### Truncation / misexpression
- 78insC → `truncation_misexpression`
- IVS2-2 a→c → `truncation_misexpression`

### Mitochondrial targeting (formerly targeting defects)
- I12T → `unknown_mechanism` primary, `targeting_signal_perturbation` + `cofactor_binding_perturbation` secondaries (pdb_first; stability mock)

---

## Expected behavior (Phase 1.5, pdb_first)

| Variant | Expected primary | Notes |
|---------|------------------|-------|
| R59W | cofactor_binding_perturbation | Real FAD/inhibitor distances from 3NKS |
| I12T | unknown_mechanism | Targeting region; stability mock; secondaries: targeting, cofactor |
| R152C | folding_stability or unknown | Folding when FoldX real; unknown when mock |
| G358R | folding_stability or unknown | Same as R152C |
| 78insC | truncation_misexpression | Structural steps skipped |
| IVS2-2 a→c | truncation_misexpression | Structural steps skipped |

Panel YAML: `data/testdata/variants/ppox_panel.yaml` (expectations per mode).

---

## Notes

These are suggested mechanisms. PSGE reflects uncertainty and avoids overclaiming. See report "Important context and limitations" and [docs/USER_GUIDE.md](docs/USER_GUIDE.md).
