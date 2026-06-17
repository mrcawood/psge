# PSGE Phase 1.6e — Evidence Source Layer

Phase 1.6e adds a minimal, curated evidence-source layer for the PPOX panel. PSGE-computed signals and external literature are tracked separately so reports do not look authoritative without source context.

---

## Source registry

File: `data/sources/ppox_sources.yaml`

Each source entry includes:

| Field | Purpose |
|-------|---------|
| `source_id` | Stable identifier referenced in reports and variant map |
| `title` | Human-readable title (from local bibliography when literature) |
| `source_type` | `pdb_structure`, `computational_prediction`, `literature`, `functional_assay`, etc. |
| `species_context` | Usually `human` for current panel |
| `evidence_tier` | Tier used in report-level basis |
| `supports` | What kind of claim the source can support |
| `notes` | Caveats (non-clinical, proxy vs proof, etc.) |

Current registry sources:

- `PDB_3NKS` — human 3NKS crystal structure (FAD + inhibitor ACJ)
- `FOLDX_5_3NKS` — FoldX 5 ΔΔG on repaired protein-only 3NKS
- `SASA_BIOPYTHON_3NKS` — local SASA on 3NKS context
- `MEISSNER_1996_R59W` — functional assay (reduced PPO activity), verified from `07_REFERENCES.md`
- `QIN_2011_R59W_MECHANISTIC` — mechanistic literature context for R59W / FAD environment

No source is invented. Literature claims are only present when verified from project bibliography materials.

---

## Variant evidence map

File: `data/sources/ppox_variant_evidence.yaml`

Per variant:

| Field | Purpose |
|-------|---------|
| `psge_computed_evidence` | Source IDs for PSGE-computed signals |
| `external_evidence` | Curated external claims with `claim_scope`, `evidence_tier`, `claim`, `confidence` |
| `evidence_gap` | Explicit gaps (missing functional data, unresolved targeting, etc.) |

Truncation/splice variants list empty computed evidence and note that structural/FoldX backends are not applied.

---

## Evidence tiers

| Tier | Meaning |
|------|---------|
| `pdb_context_only` | 3NKS distances, SASA, curated site membership |
| `foldx_stability_prediction` | FoldX ΔΔG on prepared model |
| `literature_mechanistic` | Published mechanistic discussion (not PSGE proof) |
| `functional_assay` | External functional measurement |
| `replicated_multi_source` | Reserved; not used in Phase 1.6e |

---

## Claim scope

Per-row and external claims carry `claim_scope`:

- `structural_context` — PDB proximity, SASA
- `computational_prediction` — FoldX ΔΔG
- `direct_variant_evidence` — external functional claim for this variant
- `mechanistic_inference` — literature mechanistic hypothesis
- `background_context`, `unsupported_or_speculative` — reserved for future use

---

## Reporting integration

`summary.json` and `report.md` include:

1. Evidence basis (intro + tier summary)
2. Computed evidence (source ID list)
3. External evidence (curated claims or explicit absence)
4. Evidence gaps
5. Interpretation limits

Per-row evidence in `evidence_table` carries `source_id`, `evidence_tier`, `evidence_type`, and `claim_scope`. External evidence rows are appended from the variant map (not recomputed by PSGE).

PSGE mechanism class remains a hypothesis. External functional evidence (e.g. R59W reduced activity) supports biological relevance but does not override classifier precedence.

---

## Deferred

- Pete-facing packet
- Broad literature mining or new variants
- ClinVar/HGMD integration
- ΔΔG threshold calibration against literature
- Rosetta or additional backends
- Multi-primary classifier redesign
