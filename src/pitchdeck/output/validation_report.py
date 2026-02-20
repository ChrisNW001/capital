"""Markdown renderer for deck validation reports."""

from pitchdeck.models import DeckValidationResult


def render_validation_report(result: DeckValidationResult) -> str:
    """Render a DeckValidationResult as formatted Markdown."""
    pass_fail = "PASS" if result.pass_fail else "FAIL"
    lines = [
        f"# Deck Validation Report",
        "",
        f"**Deck**: {result.deck_name}",
        f"**Target VC**: {result.target_vc}",
        f"**Validated**: {result.validated_at}",
        f"**Overall Score**: {result.overall_score}/100 — **{pass_fail}** "
        f"(threshold: {result.pass_threshold})",
        "",
        "---",
        "",
        "## Score Breakdown",
        "",
        "| Dimension | Score | Weight | Weighted |",
        "|-----------|-------|--------|----------|",
    ]

    total_weighted = 0.0
    for dim in result.dimension_scores:
        weighted = dim.score * dim.weight
        total_weighted += weighted
        lines.append(
            f"| {dim.dimension.replace('_', ' ').title()} "
            f"| {dim.score}/100 "
            f"| {int(dim.weight * 100)}% "
            f"| {weighted:.1f} |"
        )
    lines.append(
        f"| **TOTAL** | | | **{total_weighted:.1f}** |"
    )
    lines.append("")

    # Dimension details
    for dim in result.dimension_scores:
        lines.extend([
            f"### {dim.dimension.replace('_', ' ').title()}",
            "",
            f"**Score**: {dim.score}/100",
            f"**Rationale**: {dim.rationale}",
            "",
        ])
        if dim.evidence_found:
            lines.append("**Evidence Found:**")
            for e in dim.evidence_found:
                lines.append(f"- {e}")
            lines.append("")
        if dim.evidence_missing:
            lines.append("**Evidence Missing:**")
            for e in dim.evidence_missing:
                lines.append(f"- {e}")
            lines.append("")

    # VC Custom Checks
    if result.custom_check_results:
        lines.extend([
            "---",
            "",
            "## VC-Specific Checks",
            "",
            "| Check | Status | Evidence |",
            "|-------|--------|----------|",
        ])
        for cc in result.custom_check_results:
            status = "PASS" if cc.passed else "FAIL"
            lines.append(f"| {cc.check} | {status} | {cc.evidence} |")
        lines.append("")

    # Per-slide scores
    lines.extend([
        "---",
        "",
        "## Per-Slide Scores",
        "",
    ])
    for ss in result.slide_scores:
        lines.extend([
            f"### Slide {ss.slide_number}: "
            f"{ss.slide_type} — {ss.score}/100",
            "",
        ])
        if ss.issues:
            lines.append("**Issues:**")
            for issue in ss.issues:
                lines.append(f"- {issue}")
            lines.append("")
        if ss.suggestions:
            lines.append("**Suggestions:**")
            for s in ss.suggestions:
                lines.append(f"- {s}")
            lines.append("")
        if not ss.issues and not ss.suggestions:
            lines.append("No issues detected.")
            lines.append("")

    # Strengths and gaps
    if result.top_strengths:
        lines.extend([
            "---",
            "",
            "## Top Strengths",
            "",
        ])
        for i, s in enumerate(result.top_strengths, 1):
            lines.append(f"{i}. {s}")
        lines.append("")

    if result.critical_gaps:
        lines.extend([
            "## Critical Gaps",
            "",
        ])
        for i, g in enumerate(result.critical_gaps, 1):
            lines.append(f"{i}. {g}")
        lines.append("")

    if result.improvement_priorities:
        lines.extend([
            "## Improvement Priorities (ordered by impact)",
            "",
        ])
        for i, p in enumerate(result.improvement_priorities, 1):
            lines.append(f"{i}. {p}")
        lines.append("")

    if result.recommendation:
        lines.extend([
            "---",
            "",
            "## Recommendation",
            "",
            result.recommendation,
            "",
        ])

    return "\n".join(lines)


def save_validation_report(
    result: DeckValidationResult, path: str
) -> None:
    """Save validation report as Markdown file."""
    content = render_validation_report(result)
    with open(path, "w") as f:
        f.write(content)
