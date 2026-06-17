"""Summary and report emission (PRD §6)."""

import hashlib
import json
from pathlib import Path

from psge.core.models import Config, MechanismHypothesis, VariantRecord
from psge.reporting.evidence import (
    build_evidence_summary,
    enrich_evidence_rows,
    evidence_basis_intro,
    external_evidence_rows,
    format_external_evidence_section,
)


def _format_evidence_line(row: dict) -> str:
    base = f"- {row.get('signal', '')}: {row.get('value', '')}"
    meta = []
    if row.get("evidence_type"):
        meta.append(f"type={row['evidence_type']}")
    if row.get("source_id"):
        meta.append(f"source={row['source_id']}")
    if row.get("claim_scope"):
        meta.append(f"scope={row['claim_scope']}")
    if row.get("evidence_tier"):
        meta.append(f"tier={row['evidence_tier']}")
    if row.get("interpretation"):
        meta.append(f"interpretation={row['interpretation']}")
    if meta:
        return f"{base} ({', '.join(meta)})"
    return base


def emit_summary(
    results_dir: Path,
    variant: str,
    hypothesis: MechanismHypothesis,
    variant_record: VariantRecord,
    skipped_steps: list[str],
    backend_status: dict | None = None,
    delta=None,
    stability_result=None,
) -> Path:
    """Emit summary.json (machine-readable). Phase 1.6d: evidence tiering."""
    from psge.utils.backend_status import get_backend_status

    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    input_hash = hashlib.sha256(variant.encode()).hexdigest()

    enriched = enrich_evidence_rows(
        list(hypothesis.evidence_table),
        stability_result=stability_result,
        delta=delta,
        backend_status=backend_status,
    )
    enriched.extend(external_evidence_rows(variant))
    evidence_summary = build_evidence_summary(enriched, backend_status, variant)

    summary = {
        "variant": variant,
        "input_hash": input_hash,
        "mechanism_class": hypothesis.class_,
        "confidence": hypothesis.confidence,
        "evidence_table": enriched,
        "evidence_summary": evidence_summary,
        "interpretation": hypothesis.interpretation,
        "limits": hypothesis.limits,
        "decision_trace": hypothesis.decision_trace,
        "secondary_hypotheses": getattr(hypothesis, "secondary_hypotheses", None) or [],
        "skipped_steps": skipped_steps,
        "backend_status": backend_status or get_backend_status(),
        "tool_versions": {"psge": "0.1.0"},
    }
    if stability_result and stability_result.foldx_provenance:
        summary["foldx_provenance"] = stability_result.foldx_provenance
    if stability_result and stability_result.stability_signal_band:
        summary["stability_signal_band"] = stability_result.stability_signal_band

    path = results_dir / "summary.json"
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    return path


def emit_report(
    results_dir: Path,
    variant: str,
    hypothesis: MechanismHypothesis,
    skipped_steps: list[str],
    backend_status: dict | None = None,
    delta=None,
    stability_result=None,
) -> Path:
    """Emit report.md (human-readable). Phase 1.6d: tiering and FoldX provenance."""
    from psge.utils.backend_status import get_backend_status

    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    status = backend_status or get_backend_status()
    has_mock = any(
        v in ("mock", "placeholder", "not_implemented")
        for v in (status.values() if isinstance(status, dict) else [])
    )
    mock_note = (
        "**Note:** Some metrics use mock or placeholder backends (e.g. stability, SASA). "
        "Global/local RMSD are real when structure_backend is not mock. See backend_status."
    ) if has_mock else ""

    enriched = enrich_evidence_rows(
        list(hypothesis.evidence_table),
        stability_result=stability_result,
        delta=delta,
        backend_status=status,
    )
    enriched.extend(external_evidence_rows(variant))
    evidence_summary = build_evidence_summary(enriched, status, variant)

    context_limits = (
        "This report is a research-grade, non-clinical analysis intended to generate mechanistically "
        "plausible hypotheses about how a specific variant might perturb PPOX at the molecular level. "
        "It does not diagnose disease, classify pathogenicity, predict symptom onset, or estimate clinical risk/penetrance. "
        "Reported signals (e.g., proximity to FAD/inhibitor, structural deltas, stability estimates) are evidence inputs, "
        "not proof of causality. FoldX ΔΔG is a protein stability estimate on a prepared structural model; it is not a "
        "direct cofactor-binding, catalytic, or clinical measurement. Inhibitor (ACJ) proximity in 3NKS does not prove "
        "substrate binding. A variant can be structurally near a cofactor region and still have limited functional impact. "
        "Mechanism labels are suggestive and should be interpreted alongside primary literature and functional assays where available."
    )

    lines = [
        "# PSGE Mechanism Report",
        "",
        f"**Variant:** {variant}",
        "",
        "## Important context and limitations (*read first*)",
        "",
        context_limits,
        "",
        "## Evidence basis",
        "",
        evidence_basis_intro(variant),
        "",
        f"- evidence_basis: {evidence_summary.get('evidence_basis_description') or 'PSGE-computed structural context and FoldX when applicable'}",
        f"- overall_evidence_basis: {evidence_summary.get('overall_evidence_basis')}",
        f"- highest_evidence_tier: {evidence_summary.get('highest_evidence_tier')}",
        f"- species_context: {evidence_summary.get('species_context')}",
        f"- clinical_interpretation: {evidence_summary.get('clinical_interpretation')}",
        "",
        "## Computed evidence",
        "",
    ]
    for sid in evidence_summary.get("computed_evidence_source_ids", []):
        lines.append(f"- {sid}")
    if not evidence_summary.get("computed_evidence_source_ids"):
        if evidence_summary.get("structural_evidence_status") == "not_applicable":
            lines.append(
                "- Structural, FoldX, and SASA evidence not applicable (non-missense variant class)."
            )
        else:
            lines.append("- (none for this variant type)")
    lines.extend([
        "",
        "## External evidence",
        "",
        format_external_evidence_section(variant),
        "",
        "## Evidence gaps",
        "",
    ])
    gaps = evidence_summary.get("evidence_gaps") or []
    if gaps:
        for g in gaps:
            lines.append(f"- {g}")
    else:
        lines.append("- None identified in variant evidence map.")
    lines.extend([
        "",
        "## Interpretation limits",
        "",
        hypothesis.limits,
        "",
        "## Mechanism Hypothesis (Suggested)",
        "",
        f"- **Class:** {hypothesis.class_}",
        f"- **Confidence:** {hypothesis.confidence}",
    ])
    secondary = getattr(hypothesis, "secondary_hypotheses", None) or []
    if secondary:
        lines.append(f"- **Secondary hypotheses:** {', '.join(secondary)}")
    if stability_result and stability_result.stability_signal_band:
        lines.append(f"- **Stability signal band:** {stability_result.stability_signal_band}")
    lines.extend([
        "",
        "## Classifier Decision Trace",
        "",
    ])
    for rule in hypothesis.decision_trace:
        lines.append(f"- {rule}")
    lines.extend([
        "",
        "## Interpretation",
        "",
        hypothesis.interpretation,
        "",
        "## Evidence",
        "",
    ])
    for row in enriched:
        lines.append(_format_evidence_line(row))

    prov = stability_result.foldx_provenance if stability_result else None
    if prov:
        lines.extend([
            "",
            "## FoldX provenance",
            "",
            f"- pdb_id: {prov.get('pdb_id')}",
            f"- structure_source: {prov.get('structure_source')}",
            f"- chain_id: {prov.get('chain_id')}",
            f"- uniprot_position: {prov.get('uniprot_position')}",
            f"- pdb_residue_id: {prov.get('pdb_residue_id')}",
            f"- mapping_status: {prov.get('mapping_status')}",
            f"- foldx_mutation_string: {prov.get('foldx_mutation_string')}",
            f"- foldx_version: {prov.get('foldx_version')}",
            f"- foldx_status: {prov.get('foldx_status')}",
            f"- repair_pdb_used: {prov.get('repair_pdb_used')}",
            f"- foldx_input_policy: {prov.get('foldx_input_policy')}",
            f"- protein_only_for_foldx: {prov.get('protein_only_for_foldx')}",
            f"- ligands_included_for_foldx: {prov.get('ligands_included_for_foldx')}",
            f"- stability_signal_band: {prov.get('stability_signal_band')}",
            f"- audit_passed: {prov.get('audit_passed')}",
        ])
        if prov.get("audit_notes"):
            lines.append(f"- audit_notes: {prov.get('audit_notes')}")

    lines.extend([
        "",
        "## Limits",
        "",
        "See Interpretation limits above for mechanism-specific caveats.",
        "",
        "## Backend Status",
        "",
        f"- structure_backend: {status.get('structure_backend', '?')}",
        f"- stability_backend: {status.get('stability_backend', '?')}",
        f"- delta_metrics: {status.get('delta_metrics', '?')}",
        f"- sasa: {status.get('sasa', '?')}",
    ])
    if status.get("foldx_version"):
        lines.append(f"- foldx_version: {status.get('foldx_version')}")
    lines.extend([
        "",
        mock_note,
        "",
        "## Skipped Steps",
        "",
    ])
    if skipped_steps:
        for s in skipped_steps:
            lines.append(f"- {s}")
    else:
        lines.append("- None")
    lines.extend([
        "",
        "---",
        "*PSGE: Personal Structural Genomics Engine. Research-grade, non-clinical.*",
    ])
    path = results_dir / "report.md"
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path
