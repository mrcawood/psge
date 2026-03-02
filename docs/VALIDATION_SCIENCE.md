# PSGE Scientific Validation (M6b)

**Purpose:** Document real metrics, curated knowledge, mechanism hypotheses, and limitations for scientific integration.

**Scope:** Structural analysis of PPOX variants (UniProt P50336). Non-clinical, research-grade.

---

## Panel Variants and Expected Mechanisms

| Variant | Expected Class | Rationale (brief) |
|---------|----------------|-------------------|
| R59W | substrate_binding_impairment | Near FAD/active site; affects cofactor binding |
| R152C | structural_destabilization | Destabilizing; ddg threshold |
| G358R | structural_destabilization | Destabilizing; ddg threshold |
| 78insC | truncation_misexpression | Frameshift; non-structural track |
| IVS2-2 a→c | truncation_misexpression | Splice variant; non-structural track |
| I12T | mitochondrial_targeting_defect | In N-terminal targeting signal (res 12; LXXXIXXL motif) |

---

## Real Metrics (M6b)

### RMSD (Implemented)
- **Global RMSD:** Cα backbone superimposition via BioPython. Measures overall structural change.
- **Local RMSD:** Per-residue window (default radius 5) around the variant position. Measures local conformation.
- **Source:** `utils/pdb_rmsd.py` (BioPython Superimposer).

### SASA (Not Implemented)
- `sasa_delta` in `DeltaFeatures` returns `0.0` (placeholder).
- Future integration: freesasa or DSSP for solvent-accessible surface area change.

### Stability (Mock)
- `ddg` and flags from stability stage use mock backend.
- Future: FoldX, Rosetta ddg_monomer, or similar.

---

## Curated PPOX Knowledge

**Reference:** Qin et al. (2011), PPOX structure and mechanism.

### FAD / active site
- Residues: 9–14 (targeting), 54–63 (FAD pocket), 147–150, 173, 318–320.

### N-terminal targeting signal
- Residues 1–28 (independently functioning signal; LXXXIXXL motif Leu-8, Ile-12, Leu-15). PMID:12556518
- Residues 1–17 minimal for efficient targeting in GFP fusion constructs. PMID:16621625
- **Note:** PPOX targeting is not only N-terminal; internal signals exist (e.g. residues 25–477, PMID:12556518; 151–175 interacts with first 150, PMID:14535846). Phase 1 rule uses N-terminal only.

### Membrane region
- Residues 100–120 (approximate transmembrane).

**Source:** `knowledge/ppox/sites.yaml`.

---

## Mechanism Hypotheses and Rule Precedence

1. **non_structural_track** → truncation_misexpression (truncation/splice only).
2. **in_targeting_region** → mitochondrial_targeting_defect (targeting before destabilization).
3. **destabilizing_ddg_or_flags** → structural_destabilization (when stability is real or mock-tagged).
4. **near_fad_or_active_site** → substrate_binding_impairment.
5. **default** → unknown_mechanism (low confidence; honest when no rule matches).

When primary is destabilization and variant is near FAD/active site: secondary_hypotheses = [substrate_binding_impairment]. When primary is substrate_binding and also destabilizing: secondary_hypotheses = [structural_destabilization].

---

## Limitations

- **Structure:** Mock by default; ESMFold optional when installed. No experimental PDB for many variants.
- **Stability:** Mock ddg; no FoldX/Rosetta integration yet.
- **SASA:** Placeholder (0.0); not used in classifier.
- **Contacts:** `contact_deltas` placeholder; not integrated.
- **Taxonomy:** Expert-informed hypothesis structure, not ground truth. Reports use "suggested" wording.

---

## Backend Status Fields

| Field | Values | Meaning |
|-------|--------|---------|
| structure_backend | mock, esmfold | Source of WT/mutant PDBs |
| stability_backend | mock | ddg source |
| delta_metrics | real_rmsd | RMSD is real when structure is real |
| sasa | not_implemented | SASA delta is placeholder |
