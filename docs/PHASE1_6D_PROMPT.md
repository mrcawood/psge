# Worker Prompt: PSGE Phase 1.6d — Evidence Hardening, Threshold Policy, and Report Readiness

You are continuing PSGE after Phase 1.6c.

Phase 1.6c successfully installed and integrated FoldX, ran the PPOX panel using `pdb_first` / 3NKS, and produced real ΔΔG values in `summary.json`, `report.md`, and `run_manifest.json`.

Your task for Phase 1.6d is **not to redesign the project** and **not to expand into broad literature mining**. The goal is to harden the evidence model, make FoldX interpretation more conservative and auditable, update stale docs, rerun the panel, and prepare outputs suitable for later expert review.

## 0. Starting state

Assume the current state is:

* FoldX 5.x is installed locally on `talos`.
* FoldX binary and license files are local only and must not be committed.
* PSGE can run:

```bash
psge run --panel data/testdata/variants/ppox_panel.yaml \
  --structure-source pdb_first \
  --results-dir results/foldx_panel
```

Current Phase 1.6c panel behavior:

| Variant    | FoldX ΔΔG | Current primary                    |
| ---------- | --------: | ---------------------------------- |
| R59W       |     ~2.02 | cofactor_binding_perturbation      |
| I12T       |     ~3.78 | folding_stability_hydrophobic_core |
| R152C      |     ~1.68 | unknown_mechanism                  |
| G358R      |    ~15.29 | folding_stability_hydrophobic_core |
| 78insC     |   skipped | truncation_misexpression           |
| IVS2-2 a→c |   skipped | truncation_misexpression           |

Important supervisor concerns:

* The hard 2.0 kcal/mol ΔΔG cutoff is too brittle.
* R152C at ~1.68 should not disappear from interpretation entirely.
* R59W at ~2.02 should not suddenly be over-interpreted as a stability mutation.
* I12T’s new folding/stability primary is plausible but must be worded carefully.
* G358R’s ΔΔG is very high and should trigger an audit note.
* Reports must clearly distinguish structural proximity, FoldX prediction, literature evidence, and functional assay evidence.

## 1. Non-negotiable guardrails

Do not:

* commit FoldX binaries, zip files, license files, or proprietary assets;
* silently fall back from failed FoldX to mock ΔΔG;
* allow mock ΔΔG to drive scientific classification;
* make clinical claims;
* infer pathogenicity, penetrance, disease severity, symptom risk, or treatment relevance;
* say FoldX proves functional effect;
* say ACJ/inhibitor proximity proves substrate binding;
* compare incompatible WT/mutant structures as if deltas are meaningful.

Unknown or low-confidence output is acceptable.

## 2. Phase 1.6d objectives

### Objective A — Add evidence tiering

Add structured evidence tier metadata to `summary.json` and `report.md`.

Required fields:

```text
evidence_tier
species_context
sources
evidence_type
```

Recommended allowed values:

```text
evidence_tier:
  - pdb_context_only
  - foldx_stability_prediction
  - literature_mechanistic
  - functional_assay
  - replicated_multi_source

species_context:
  - human
  - non_human
  - mixed
  - not_applicable

evidence_type:
  - structural_proximity
  - sasa_context
  - foldx_ddg
  - curated_site_membership
  - variant_class_rule
  - literature_note
  - functional_assay
```

Initial behavior:

* FoldX evidence should be labeled `foldx_stability_prediction`.
* 3NKS distance/SASA/context evidence should be labeled `pdb_context_only`.
* Do not invent literature or functional evidence unless already represented in the repo.
* If sources are not yet implemented as structured citations, use a minimal structured placeholder, for example:

```json
{
  "source_id": "3NKS",
  "source_type": "pdb_structure",
  "species_context": "human"
}
```

or leave `sources: []` with an explicit note that literature source integration is deferred.

### Objective B — Replace brittle ΔΔG cutoff with threshold bands

Current behavior uses a provisional hard cutoff around `ddg >= 2.0 kcal/mol`.

Replace or supplement this with explicit bands:

```text
ddg < 1.0:
  stability_signal = "none_or_weak"

1.0 <= ddg < 2.0:
  stability_signal = "weak_to_moderate"

2.0 <= ddg < 5.0:
  stability_signal = "destabilizing"

5.0 <= ddg < 10.0:
  stability_signal = "strong_destabilizing"

ddg >= 10.0:
  stability_signal = "extreme_destabilizing_requires_audit"
```

Classifier policy:

* `folding_stability_hydrophobic_core` may be primary only when:

  * `stability_backend == "foldx"`,
  * mapping is exact or otherwise explicitly acceptable,
  * FoldX run succeeded,
  * and the stability signal is at least `destabilizing`.

* For `weak_to_moderate`, do not force primary folding classification. Add an evidence note or secondary hypothesis only if the rest of the mechanism context supports it.

* For `extreme_destabilizing_requires_audit`, allow primary folding classification only after audit metadata confirms:

  * exact mapping,
  * plausible mutation string,
  * residue present,
  * RepairPDB/BuildModel completed normally,
  * no parser anomaly.

### Objective C — Improve interpretation language for key variants

Update report wording so that each major variant is conservative and scientifically clear.

#### R59W

Expected posture:

* Primary remains cofactor/FAD-environment proximity by rule precedence.
* FoldX ΔΔG is borderline/low destabilizing and should appear as secondary or evidence note.
* Do not imply FoldX proves R59W disease mechanism.
* Do not imply cofactor binding affinity is measured.

Preferred language:

```text
R59W is located in the FAD-proximal structural environment in the 3NKS reference. FoldX predicts a borderline destabilizing effect under the prepared protein model. These signals support a plausible structural hypothesis involving the cofactor environment and possible local stability effects, but they do not establish altered enzyme activity, cofactor affinity, penetrance, or clinical outcome.
```

#### I12T

Expected posture:

* FoldX predicts destabilization.
* Folding/stability may now be primary in the pipeline.
* Targeting/localization remains biologically distinct and unresolved by FoldX.

Preferred language:

```text
FoldX predicts a destabilizing effect for I12T under the 3NKS-based model, making folding/stability a plausible primary structural mechanism in this pipeline. Targeting/localization remains a separate biological hypothesis and is not resolved by FoldX.
```

#### R152C

Expected posture:

* Do not force primary folding classification if below threshold.
* Do not ignore the signal.
* Add weak/moderate stability evidence.

Preferred language:

```text
R152C shows a weak-to-moderate FoldX destabilization signal below the current primary-classification threshold. PSGE therefore does not assign a confident primary structural mechanism from the current evidence, but records the stability signal for review.
```

#### G358R

Expected posture:

* Strong/extreme FoldX destabilization signal.
* Likely good folding/stability control.
* Must include audit/provenance because the value is large.

Preferred language:

```text
G358R shows a very large FoldX destabilization signal. PSGE treats this as a strong folding/stability hypothesis only after confirming exact residue mapping, valid mutation syntax, normal FoldX completion, and no parser or structure-preparation anomaly.
```

### Objective D — Add FoldX model-context provenance to outputs

For every FoldX result, include the following in `summary.json`, `report.md`, and/or `run_manifest.json`:

```text
pdb_id
structure_source
chain_id
uniprot_position
pdb_residue_id
mapping_status
foldx_mutation_string
foldx_version
foldx_status
repair_pdb_used
foldx_input_policy
ligands_included_for_foldx
protein_only_for_foldx
repaired_pdb_path
raw_foldx_output_path
mutant_model_path
```

Important wording:

* If FoldX uses protein-only input, say so.
* If FAD/ACJ are removed for FoldX, say so.
* Reports must clarify that FoldX ΔΔG is a protein stability estimate, not a direct cofactor-binding, catalytic, or clinical measurement.

### Objective E — Update stale docs

The Phase 1.6c report identified stale docs.

Update at least:

```text
M7_PETE_OVERVIEW.md
OUTPUT_SCHEMA.md
docs/VALIDATION_SCIENCE.md
docs/PHASE1_6_DELIVERABLE_CHECKLIST.md
PROGRESS.md
```

Specific required cleanup:

* Remove any old global SASA total/delta examples from pre-fix outputs.
* Document local-only SASA.
* Document `sasa_source_pairing`.
* Document FoldX evidence tiering.
* Document ΔΔG threshold bands.
* Document that thresholds are provisional.
* Document that Pete has not formally endorsed exact FAD/active-site residue sets.
* Mark Phase 1.6c complete if appropriate.
* Add Phase 1.6d status.

## 3. Stretch goals: what to include in 1.6d vs defer to 1.6e

### Include in Phase 1.6d if bounded

These are directly tied to making current FoldX results trustworthy.

#### Stretch 1 — FoldX repeatability check

Run the same FoldX-backed variant twice, ideally R59W and G358R.

Confirm:

* cached and non-cached behavior is understood;
* parsed ΔΔG is stable;
* output file selection is deterministic;
* report does not change between runs except expected timestamps/paths.

Deliverable:

```text
docs/PHASE1_6D_FOLDX_REPEATABILITY.md
```

#### Stretch 2 — Audit G358R extreme ΔΔG

Because G358R gives a very large ΔΔG, add an audit section.

Check:

* UniProt→PDB mapping is exact;
* chain/residue is correct;
* mutation string is correct;
* RepairPDB completed normally;
* BuildModel completed normally;
* parser selected the correct `Dif_*.fxout`;
* no obvious malformed structure issue.

Deliverable:

```text
docs/PHASE1_6D_G358R_AUDIT.md
```

#### Stretch 3 — Add FoldX provenance block to reports

If not already covered under Objective D, add a visible FoldX provenance section in `report.md`.

This is useful for Pete and for future reproducibility.

### Defer to Phase 1.6e

Do not attempt these in Phase 1.6d unless explicitly authorized after completing all required work.

#### Defer 1 — Literature-driven panel expansion

Do not start broad literature mining for new PPOX variants in 1.6d.

This should become Phase 1.6e because it requires careful curation, evidence scoring, species mapping, and source quality control.

#### Defer 2 — Pete-facing polished packet

Do not produce the final Pete packet in 1.6d.

Phase 1.6d should produce clean internal reports and updated docs. The Pete packet comes after supervisor review.

#### Defer 3 — Threshold calibration against literature

Do not tune thresholds to match expected labels.

Record raw values and provisional bands. Calibration requires a broader, curated panel and should be Phase 1.6e or later.

#### Defer 4 — Rosetta or alternative stability backends

Do not add another stability backend in 1.6d.

FoldX must be made trustworthy first.

## 4. Required commands

Run baseline:

```bash
pytest
ruff check .
```

Run panel:

```bash
psge run --panel data/testdata/variants/ppox_panel.yaml \
  --structure-source pdb_first \
  --results-dir results/foldx_panel_1_6d
```

Run individual examples if useful:

```bash
psge run --variant R59W --structure-source pdb_first --results-dir results/foldx_r59w_1_6d
psge run --variant I12T --structure-source pdb_first --results-dir results/foldx_i12t_1_6d
psge run --variant R152C --structure-source pdb_first --results-dir results/foldx_r152c_1_6d
psge run --variant G358R --structure-source pdb_first --results-dir results/foldx_g358r_1_6d
```

## 5. Acceptance criteria

Phase 1.6d is complete when:

1. All tests pass.
2. Ruff passes.
3. Panel run completes.
4. `summary.json` includes evidence tiering and FoldX provenance.
5. `report.md` includes conservative interpretation language.
6. R152C weak/moderate FoldX signal is visible but not overclextreme.
8. R59W remains primarily cofactor/FAD-environment unless supervisor approves otherwise.
9. I12T wording distinguishes stability prediction from targeting/localization biology.
10. Stale docs are updated.
11. No FoldX binary, zip, license, or raw proprietary material is tracked by git.
12. Mock stability cannot drive scientific classification.
13. FoldX failure cannot silently fall back to mock.
14. A new supervisor report is produced.

## 6. Required final report

Create:

```text
docs/PHASE1_6D_SUPERVISOR_REPORT.md
```

The report must include:

### Environment

```text
OS
FoldX path
FoldX version
config source
structure source
PDB ID
protein-only vs ligand-included FoldX policy
```

### Code changes

List files changed and summarize each change.

### Test results

Include:

```text
pytest result
ruff result
FoldX integration test behavior
```

### Panel results table

Include:

```text
variant
mapping_status
foldx_status
ddg_kcal_mol
stability_signal_band
primary mechanism
secondary hypotheses
confidence
notes
```

### Interpretation review

Specifically discuss:

* R59W borderline ΔΔG but cofactor-proximity primary
* I12T primary shift to folding/stability
* R152C weak/moderate destabilization signal below primary threshold
* G358R extreme destabilization and audit outcome
* non-missense skip behavior

### Remaining open items

Separate into:

```text
Must do before Pete
Good stretch for 1.6e
Longer-term
```

### Recommendation

State whether Phase 1.6d is ready for supervisor review and whether you recommend syncing with Pete yet.

## 7. Expected supervisor review stance

The likely supervisor decision after Phase 1.6d will be:

* review cleaned panel outputs,
* decide whether Phase 1.6e should expand the variant panel,
* then package a concise Pete-facing report.

Do not optimize for pleasing Pete. Optimize for traceable, conservative, technically defensible output.

