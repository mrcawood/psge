"""Summary and report emission (PRD §6)."""

import hashlib
import json
from pathlib import Path

from psge.core.models import Config, MechanismHypothesis, VariantRecord


def _sasa_evidence(delta) -> list[dict]:
    """Build SASA evidence items (Phase 1.6a Option A: local only, no global totals)."""
    if delta is None:
        return []
    ev = []
    if getattr(delta, "sasa_residue_wt", None):
        for pos, val in delta.sasa_residue_wt.items():
            ev.append({"signal": f"sasa_residue_wt_{pos}", "value": round(val, 2)})
    if getattr(delta, "sasa_residue_mut", None):
        for pos, val in delta.sasa_residue_mut.items():
            ev.append({"signal": f"sasa_residue_mut_{pos}", "value": round(val, 2)})
    if getattr(delta, "delta_sasa_residue", None):
        for pos, val in delta.delta_sasa_residue.items():
            ev.append({"signal": f"delta_sasa_residue_{pos}", "value": round(val, 2)})
    if getattr(delta, "sasa_patch_8A", None) is not None:
        ev.append({"signal": "sasa_patch_8A", "value": round(delta.sasa_patch_8A, 2)})
    if getattr(delta, "sasa_mapping_status", None):
        ev.append({"signal": "sasa_mapping_status", "value": delta.sasa_mapping_status})
    if getattr(delta, "sasa_source_pairing", None):
        ev.append({"signal": "sasa_source_pairing", "value": delta.sasa_source_pairing})
    return ev


def _stability_evidence(stability_result, backend_status: dict | None) -> list[dict]:
    """FoldX ΔΔG evidence when real stability backend ran (even if not primary driver)."""
    if stability_result is None:
        return []
    if (backend_status or {}).get("stability_backend") != "foldx":
        return []
    ev = [{"signal": "ddg", "value": round(stability_result.ddg, 5)}]
    if stability_result.flags:
        ev.append({"signal": "flags", "value": stability_result.flags})
    return ev


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
    """Emit summary.json (machine-readable). Phase 1.6: includes SASA when available."""
    from psge.utils.backend_status import get_backend_status

    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    input_hash = hashlib.sha256(variant.encode()).hexdigest()
    sasa_ev = _sasa_evidence(delta)
    stability_ev = _stability_evidence(stability_result, backend_status)
    evidence_table = list(hypothesis.evidence_table)
    existing_signals = {e.get("signal") for e in evidence_table}
    for row in stability_ev:
        if row.get("signal") not in existing_signals:
            evidence_table.append(row)
    evidence_table.extend(sasa_ev)
    summary = {
        "variant": variant,
        "input_hash": input_hash,
        "mechanism_class": hypothesis.class_,
        "confidence": hypothesis.confidence,
        "evidence_table": evidence_table,
        "interpretation": hypothesis.interpretation,
        "limits": hypothesis.limits,
        "decision_trace": hypothesis.decision_trace,
        "secondary_hypotheses": getattr(hypothesis, "secondary_hypotheses", None) or [],
        "skipped_steps": skipped_steps,
        "backend_status": backend_status or get_backend_status(),
        "tool_versions": {"psge": "0.1.0"},
    }
    if sasa_ev:
        summary["sasa"] = {e["signal"]: e["value"] for e in sasa_ev}
    if stability_ev:
        summary["stability"] = {e["signal"]: e["value"] for e in stability_ev}
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
    """Emit report.md (human-readable)."""
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

    context_limits = (
        "This report is a research-grade, non-clinical analysis intended to generate mechanistically "
        "plausible hypotheses about how a specific variant might perturb PPOX at the molecular level. "
        "It does not diagnose disease, classify pathogenicity, predict symptom onset, or estimate clinical risk/penetrance. "
        "Reported signals (e.g., proximity to FAD/inhibitor, structural deltas, stability estimates) are evidence inputs, "
        "not proof of causality. A variant can be structurally \"near\" a cofactor or active-site region and still have "
        "limited functional impact, and conversely a subtle structural change can have large functional effects. "
        "Where any backend is marked mock, not implemented, or fallback, those values must be treated as placeholders "
        "and should not be used for scientific conclusions. Even with experimental structures, these results reflect "
        "static structural context and do not capture expression/splicing, turnover/degradation, membrane environment, "
        "protein–protein interactions, or other biological layers that often govern phenotype. "
        "Mechanism labels in this report are therefore suggestive and should be interpreted alongside primary literature "
        "and, where possible, orthogonal functional assays."
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
        "## Mechanism Hypothesis (Suggested)",
        "",
        f"- **Class:** {hypothesis.class_}",
        f"- **Confidence:** {hypothesis.confidence}",
    ]
    secondary = getattr(hypothesis, "secondary_hypotheses", None) or []
    if secondary:
        lines.append(f"- **Secondary hypotheses:** {', '.join(secondary)}")
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
    for row in hypothesis.evidence_table:
        lines.append(f"- {row.get('signal', '')}: {row.get('value', '')}")
    for row in _stability_evidence(stability_result, status):
        sig = row.get("signal", "")
        if not any(r.get("signal") == sig for r in hypothesis.evidence_table):
            lines.append(f"- {sig}: {row.get('value', '')}")
    for row in _sasa_evidence(delta):
        lines.append(f"- {row.get('signal', '')}: {row.get('value', '')}")
    lines.extend([
        "",
        "## Limits",
        "",
        hypothesis.limits,
        "",
        "## Backend Status",
        "",
        f"- structure_backend: {status.get('structure_backend', '?')}",
        f"- stability_backend: {status.get('stability_backend', '?')}",
        f"- delta_metrics: {status.get('delta_metrics', '?')}",
        f"- sasa: {status.get('sasa', '?')}",
    ])
    if status.get("foldx_version"):
        lines.extend([
            f"- foldx_version: {status.get('foldx_version')}",
        ])
    lines.extend([
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
