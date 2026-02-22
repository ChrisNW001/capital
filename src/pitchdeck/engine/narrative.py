"""Claude API-powered narrative engine for pitch deck generation."""

import json
import os
import re
from typing import List

from anthropic import Anthropic

from pitchdeck.engine.slides import get_narrative_arc
from pitchdeck.models import (
    CompanyProfile,
    PitchDeck,
    PitchDeckError,
    SlideContent,
    SlideTemplate,
    VCProfile,
)

SYSTEM_PROMPT = """You are an expert pitch deck writer for B2B SaaS and enterprise AI companies \
raising Series A from European VCs. You generate investor-grade slide content that:

1. Follows proven narrative structures (Hook > Problem > Solution > Market > Execution > Ask)
2. Is data-driven with specific metrics on every applicable slide
3. Uses concise, impactful language (no fluff, no generic claims)
4. Tailors the narrative to the specific VC's investment thesis
5. Addresses common investor objections proactively
6. Includes actionable speaker notes for each slide

RULES:
- Never fabricate metrics — if data is missing, note it in gaps_identified
- Keep bullets to the specified max per slide
- Each slide must have a clear "so what" — why should the investor care?
- Speaker notes should tell the founder exactly what to SAY, not what the slide shows
- Transitions between slides must be explicit narrative connectors"""


def generate_deck(
    company: CompanyProfile,
    vc_profile: VCProfile,
    slide_templates: list[SlideTemplate],
) -> PitchDeck:
    """Generate a complete pitch deck using Claude API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise PitchDeckError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Get your key at https://console.anthropic.com/"
        )

    client = Anthropic()

    vc_context = build_vc_context(vc_profile)
    slide_instructions = _build_slide_instructions(slide_templates)
    narrative_arc = get_narrative_arc()

    system_messages = [
        {"type": "text", "text": SYSTEM_PROMPT},
        {
            "type": "text",
            "text": (
                f"<company_document>\n{company.raw_document_text}\n</company_document>\n\n"
                f"<company_profile>\n{company.model_dump_json(indent=2)}\n</company_profile>\n\n"
                f"<vc_profile>\n{vc_context}\n</vc_profile>"
            ),
            "cache_control": {"type": "ephemeral"},
        },
    ]

    user_prompt = f"""Generate a complete {len(slide_templates)}-slide pitch deck for \
{company.product_name or company.name} targeting {vc_profile.name}.

NARRATIVE ARC:
{narrative_arc}

SLIDE STRUCTURE:
{slide_instructions}

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
  "narrative_arc": "Brief summary of the overall story arc",
  "gaps_identified": ["list of missing data points that would strengthen the deck"],
  "slides": [
    {{
      "slide_number": 1,
      "slide_type": "cover",
      "title": "Concise slide title (5-8 words)",
      "headline": "Key takeaway (one sentence)",
      "bullets": ["bullet 1", "bullet 2"],
      "metrics": ["metric 1"],
      "speaker_notes": "2-3 sentences of what to SAY",
      "transition_to_next": "One sentence connecting to next slide",
      "vc_alignment_notes": ["How this maps to {vc_profile.name}'s thesis"]
    }}
  ]
}}

Generate ALL {len(slide_templates)} slides in order. Return ONLY the JSON object, no other text."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16384,
        system=system_messages,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return _parse_deck_response(response, company, vc_profile)


def build_vc_context(vc_profile: VCProfile) -> str:
    """Format VC thesis points, preferences, and custom checks into prompt text."""
    lines = [
        f"VC: {vc_profile.name} ({vc_profile.fund_name})",
        f"Stage Focus: {', '.join(vc_profile.stage_focus)}",
        f"Sector Focus: {', '.join(vc_profile.sector_focus)}",
        f"Geographic Focus: {', '.join(vc_profile.geo_focus)}",
        "",
        "Investment Thesis:",
    ]
    for i, point in enumerate(vc_profile.thesis_points, 1):
        lines.append(f"  {i}. {point}")

    if vc_profile.portfolio_companies:
        lines.append(f"\nPortfolio: {', '.join(vc_profile.portfolio_companies)}")

    if vc_profile.key_partners:
        lines.append("\nKey Partners:")
        for partner in vc_profile.key_partners:
            lines.append(f"  - {partner.name} ({partner.focus})")

    prefs = vc_profile.deck_preferences
    lines.append(f"\nDeck Preferences:")
    lines.append(f"  Narrative style: {prefs.narrative_style}")
    lines.append(f"  Market sizing: {prefs.market_sizing_approach}")
    if prefs.metrics_emphasis:
        lines.append(f"  Key metrics: {', '.join(prefs.metrics_emphasis)}")

    if vc_profile.custom_checks:
        lines.append("\nVC-Specific Requirements:")
        for check in vc_profile.custom_checks:
            lines.append(f"  - {check}")

    return "\n".join(lines)


def _build_slide_instructions(templates: list[SlideTemplate]) -> str:
    """Format slide templates into numbered instructions."""
    lines = []
    for i, t in enumerate(templates, 1):
        lines.append(f"Slide {i}: {t.slide_type}")
        lines.append(f"  Purpose: {t.purpose}")
        lines.append(f"  Required: {', '.join(t.required_elements)}")
        if t.optional_elements:
            lines.append(f"  Optional: {', '.join(t.optional_elements)}")
        if t.metrics_needed:
            lines.append(f"  Metrics: {', '.join(t.metrics_needed)}")
        lines.append(f"  Max bullets: {t.max_bullets}, Word limit: {t.word_limit}")
        lines.append("")
    return "\n".join(lines)


def _parse_deck_response(
    response, company: CompanyProfile, vc_profile: VCProfile
) -> PitchDeck:
    """Extract structured content from Claude response into PitchDeck model."""
    from datetime import datetime

    raw_text = response.content[0].text

    # Try to extract JSON from the response
    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        raise PitchDeckError(
            "Failed to parse deck response — no JSON found in Claude output"
        )

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise PitchDeckError(f"Failed to parse deck JSON: {e}") from e

    slides = []
    for slide_data in data.get("slides", []):
        slides.append(
            SlideContent(
                slide_number=slide_data.get("slide_number", len(slides) + 1),
                slide_type=slide_data.get("slide_type", "unknown"),
                title=slide_data.get("title", ""),
                headline=slide_data.get("headline", ""),
                bullets=slide_data.get("bullets", []),
                metrics=slide_data.get("metrics", []),
                speaker_notes=slide_data.get("speaker_notes", ""),
                transition_to_next=slide_data.get("transition_to_next", ""),
                vc_alignment_notes=slide_data.get("vc_alignment_notes", []),
            )
        )

    return PitchDeck(
        company_name=company.name or company.product_name,
        target_vc=vc_profile.name,
        generated_at=datetime.now().isoformat(),
        slides=slides,
        narrative_arc=data.get("narrative_arc", ""),
        gaps_identified=data.get("gaps_identified", []),
        gaps_filled=dict(company.model_dump().get("gaps_filled", {})),
    )
