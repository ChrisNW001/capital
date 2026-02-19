"""Markdown deck renderer."""

from pitchdeck.models import PitchDeck


def render_markdown(deck: PitchDeck) -> str:
    """Render a PitchDeck as formatted Markdown."""
    lines = [
        f"# {deck.company_name} — Pitch Deck",
        f"**Target**: {deck.target_vc}",
        f"**Generated**: {deck.generated_at}",
        "",
        "## Narrative Arc",
        f"{deck.narrative_arc}",
        "",
        "---",
        "",
    ]

    for slide in deck.slides:
        lines.extend(
            [
                f"## Slide {slide.slide_number}: {slide.title}",
                f"*Type: {slide.slide_type}*",
                "",
                f"**{slide.headline}**",
                "",
            ]
        )

        if slide.bullets:
            for bullet in slide.bullets:
                lines.append(f"- {bullet}")
            lines.append("")

        if slide.metrics:
            lines.append("**Key Metrics:**")
            for metric in slide.metrics:
                lines.append(f"- {metric}")
            lines.append("")

        if slide.speaker_notes:
            lines.extend(
                [
                    "<details>",
                    "<summary>Speaker Notes</summary>",
                    "",
                    slide.speaker_notes,
                    "",
                    "</details>",
                    "",
                ]
            )

        if slide.vc_alignment_notes:
            lines.append(
                f"> **VC Alignment**: {'; '.join(slide.vc_alignment_notes)}"
            )
            lines.append("")

        if slide.transition_to_next:
            lines.append(f"*Transition: {slide.transition_to_next}*")
            lines.append("")

        lines.extend(["---", ""])

    if deck.gaps_identified:
        lines.extend(
            [
                "## Information Gaps",
                "",
                "The following data points were missing and could strengthen the deck:",
                "",
            ]
        )
        for gap in deck.gaps_identified:
            lines.append(f"- [ ] {gap}")
        lines.append("")

    return "\n".join(lines)


def save_markdown(deck: PitchDeck, path: str) -> None:
    """Save deck as Markdown file."""
    content = render_markdown(deck)
    with open(path, "w") as f:
        f.write(content)
