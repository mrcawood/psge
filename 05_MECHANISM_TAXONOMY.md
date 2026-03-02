# PPOX Mechanism Taxonomy

Date: 2026-02-28

Source: Pete's "thumb suck" categorization. Treat as expert-informed hypothesis structure, not ground truth.

**Phase 1.5 implementation:** See [docs/PHASE1_5_REMAP.md](docs/PHASE1_5_REMAP.md) for the current class names, rules, and 3D Å metrics. The mapping below relates Pete's original categories to Phase 1.5.

---

## Mapping: Pete's categories → Phase 1.5 classes

| Pete (original) | Phase 1.5 class | Notes |
|----------------|-----------------|-------|
| Substrate-binding impairment | `cofactor_binding_perturbation` | Variant near FAD/inhibitor; 3D Å proximity |
| Structural destabilization | `folding_stability_hydrophobic_core` | Requires FoldX ΔΔG or SASA |
| Truncation / misexpression | `truncation_misexpression` | Unchanged |
| Mitochondrial targeting defects | `targeting_signal_perturbation` | Secondary hypothesis only by default |

Additional Phase 1.5 classes: `active_site_region_perturbation`, `unknown_mechanism` (default).

---

## Original mechanism classes (Pete)

### 1) Substrate-binding impairment
Typical signals:
- Variant near substrate / pocket residues
- Variant near FAD binding region
- Local geometry changes in pocket
Example: R59W

→ Implemented as `cofactor_binding_perturbation` (FAD/inhibitor 3D Å) or `active_site_region_perturbation`.

### 2) Structural destabilization
Typical signals:
- Large ΔΔG positive (destabilizing)
- Increased local disorder / disrupted secondary structure
- Broad contact map perturbation
Examples: R152C, G358R

→ Implemented as `folding_stability_hydrophobic_core`.

### 3) Truncation / misexpression
Typical signals:
- frameshift / nonsense / splice-site variant
- predicted loss of protein or altered expression
Examples: 78insC, IVS2-2 a→c

Notes: structural modeling is not the right primary tool; route to transcript/annotation analysis and literature.

→ Implemented as `truncation_misexpression`.

### 4) Mitochondrial targeting defects
Typical signals:
- variant in targeting peptide region
- disruption of targeting motifs or signal properties
Example: I12T

Notes: more sequence/motif analysis than 3D fold analysis.

→ Implemented as `targeting_signal_perturbation` (secondary only by default).

---

## Output framing

PSGE outputs:
- "most plausible mechanism class"
- evidence table
- explicit uncertainty
- explicit statement of limits

---

## Canonical definitions

For Phase 1.5 class definitions, rule precedence, and evidence requirements, see [docs/PHASE1_5_REMAP.md](docs/PHASE1_5_REMAP.md).
