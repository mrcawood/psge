"""Summary and report emission (PRD §6)."""

import hashlib
import json
from pathlib import Path

from psge.core.models import Config, MechanismHypothesis, VariantRecord


def emit_summary(
    results_dir: Path,
    variant: str,
    hypothesis: MechanismHypothesis,
    variant_record: VariantRecord,
    skipped_steps: list[str],
    backend_status: dict | None = None,
) -> Path:
    """Emit summary.json (machine-readable)."""
    from psge.utils.backend_status import get_backend_status

    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    input_hash = hashlib.sha256(variant.encode()).hexdigest()
    summary = {
        "variant": variant,
        "input_hash": input_hash,
        "mechanism_class": hypothesis.class_,
        "confidence": hypothesis.confidence,
        "evidence_table": hypothesis.evidence_table,
        "interpretation": hypothesis.interpretation,
        "limits": hypothesis.limits,
        "decision_trace": hypothesis.decision_trace,
        "secondary_hypotheses": getattr(hypothesis, "secondary_hypotheses", None) or [],
        "skipped_steps": skipped_steps,
        "backend_status": backend_status or get_backend_status(),
        "tool_versions": {"psge": "0.1.0"},
    }
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
