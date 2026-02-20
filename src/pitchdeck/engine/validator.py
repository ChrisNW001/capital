"""Pitch deck validation engine — rule-based + LLM scoring."""

import json
import os
import re
from datetime import datetime
from typing import List, Optional

from anthropic import Anthropic

from pitchdeck.engine.slides import SLIDE_TEMPLATES
from pitchdeck.models import (
    CustomCheckResult,
    DeckValidationResult,
    DimensionScore,
    PitchDeck,
    PitchDeckError,
    SlideContent,
    SlideTemplate,
    SlideValidationScore,
    VCProfile,
)


SCORING_DIMENSIONS = [
    {"dimension": "completeness", "weight": 0.25, "method": "rule"},
    {"dimension": "metrics_density", "weight": 0.20, "method": "rule"},
    {"dimension": "narrative_coherence", "weight": 0.20, "method": "llm"},
    {"dimension": "thesis_alignment", "weight": 0.20, "method": "llm"},
    {"dimension": "common_mistakes", "weight": 0.15, "method": "llm"},
]

COMMON_MISTAKES = [
    "Over-indexing on architecture/technical detail vs business proof",
    "Missing simplified operating plan or use-of-funds breakdown",
    "No proactive response to AI commoditization risk",
    "Using top-down TAM only without bottom-up SOM calculation",
    "Generic competitive positioning without differentiated axes",
    "No quantified customer ROI or case study evidence",
    "Missing NDR or retention metrics on traction slide",
    "Title or headline is vague/generic rather than specific and data-driven",
]


def _get_template_for_slide(slide_type: str) -> Optional[SlideTemplate]:
    """Look up the SlideTemplate matching a slide's type."""
    for template in SLIDE_TEMPLATES:
        if template.slide_type == slide_type:
            return template
    return None


def _score_slide_rules(slide: SlideContent) -> SlideValidationScore:
    """Score a single slide using deterministic rule checks."""
    template = _get_template_for_slide(slide.slide_type)
    issues = []
    suggestions = []
    score = 100  # start at 100, deduct for issues

    # Title and headline checks
    if not slide.title.strip():
        issues.append("Missing slide title")
        score -= 15
    if not slide.headline.strip():
        issues.append("Missing slide headline")
        score -= 10

    if template:
        # Bullet count check
        if template.max_bullets > 0 and len(slide.bullets) > template.max_bullets:
            issues.append(
                f"Too many bullets: {len(slide.bullets)} "
                f"(max {template.max_bullets})"
            )
            score -= 10

        # Word count check
        all_text = " ".join(
            [slide.title, slide.headline] + slide.bullets
        )
        word_count = len(all_text.split())
        if word_count > template.word_limit:
            issues.append(
                f"Exceeds word limit: {word_count} words "
                f"(max {template.word_limit})"
            )
            score -= 10

        # Metrics presence check
        if template.metrics_needed and not slide.metrics:
            issues.append(
                f"Missing metrics (expected: "
                f"{', '.join(template.metrics_needed)})"
            )
            score -= 15
            suggestions.append(
                f"Add metrics: {', '.join(template.metrics_needed)}"
            )
        elif template.metrics_needed:
            missing_ratio = max(
                0,
                len(template.metrics_needed) - len(slide.metrics),
            )
            if missing_ratio > 0:
                suggestions.append(
                    f"Consider adding more metrics "
                    f"({len(slide.metrics)}/{len(template.metrics_needed)} "
                    f"present)"
                )
                score -= missing_ratio * 3

        # Empty bullets for non-cover slides
        if template.max_bullets > 0 and not slide.bullets:
            issues.append("No bullet points on a slide that expects them")
            score -= 10

    # Speaker notes check
    if not slide.speaker_notes.strip():
        issues.append("Missing speaker notes")
        score -= 5
        suggestions.append("Add speaker notes explaining what to SAY")

    # VC alignment check
    if not slide.vc_alignment_notes:
        suggestions.append("Add VC alignment notes for this slide")
        score -= 5

    return SlideValidationScore(
        slide_number=slide.slide_number,
        slide_type=slide.slide_type,
        score=max(0, min(100, score)),
        issues=issues,
        suggestions=suggestions,
    )


def _score_completeness(deck: PitchDeck, vc_profile: VCProfile) -> DimensionScore:
    """Score deck completeness: slide count, required elements, data coverage."""
    evidence_found = []
    evidence_missing = []

    # Slide count check
    expected = len(vc_profile.deck_preferences.must_include_slides) or 15
    actual = len(deck.slides)
    if actual >= expected:
        evidence_found.append(f"{actual}/{expected} slides present")
    else:
        evidence_missing.append(
            f"Only {actual}/{expected} slides present"
        )

    # Check required slide types
    slide_types = {s.slide_type for s in deck.slides}
    must_include = set(vc_profile.deck_preferences.must_include_slides)
    if must_include:
        present = must_include & slide_types
        missing = must_include - slide_types
        if present:
            evidence_found.append(
                f"Required slide types present: {', '.join(sorted(present))}"
            )
        if missing:
            evidence_missing.append(
                f"Missing required slide types: {', '.join(sorted(missing))}"
            )

    # Speaker notes coverage
    notes_count = sum(
        1 for s in deck.slides if s.speaker_notes.strip()
    )
    evidence_found.append(
        f"Speaker notes on {notes_count}/{len(deck.slides)} slides"
    )

    # Gaps penalty
    if deck.gaps_identified:
        evidence_missing.append(
            f"{len(deck.gaps_identified)} data gaps identified: "
            f"{', '.join(deck.gaps_identified[:5])}"
        )

    # Calculate score
    total_checks = expected + len(must_include) + len(deck.slides)
    passed_checks = (
        min(actual, expected)
        + len(must_include & slide_types)
        + notes_count
    )
    score = int((passed_checks / max(total_checks, 1)) * 100)

    return DimensionScore(
        dimension="completeness",
        score=max(0, min(100, score)),
        weight=0.25,
        rationale=(
            f"Deck has {actual} slides "
            f"({notes_count} with speaker notes). "
            f"{len(evidence_missing)} gaps found."
        ),
        evidence_found=evidence_found,
        evidence_missing=evidence_missing,
    )


def _score_metrics_density(
    deck: PitchDeck, vc_profile: VCProfile
) -> DimensionScore:
    """Score metrics presence across the deck against VC expectations."""
    evidence_found = []
    evidence_missing = []

    # Count total metrics across all slides
    total_metrics = sum(len(s.metrics) for s in deck.slides)
    evidence_found.append(f"{total_metrics} metrics across deck")

    # Check metrics emphasis from VC profile
    emphasis = vc_profile.deck_preferences.metrics_emphasis
    if emphasis:
        all_content = " ".join(
            " ".join(s.bullets + s.metrics + [s.headline])
            for s in deck.slides
        ).lower()
        for metric_desc in emphasis:
            keywords = metric_desc.lower().split()
            if any(kw in all_content for kw in keywords if len(kw) > 3):
                evidence_found.append(f"Found: {metric_desc}")
            else:
                evidence_missing.append(f"Missing: {metric_desc}")

    # Expected metrics from templates
    total_expected = 0
    for slide in deck.slides:
        template = _get_template_for_slide(slide.slide_type)
        if template:
            total_expected += len(template.metrics_needed)

    coverage = total_metrics / max(total_expected, 1)
    emphasis_found = len(evidence_found) - 1  # subtract the total count entry
    emphasis_total = len(emphasis) if emphasis else 1
    emphasis_coverage = emphasis_found / max(emphasis_total, 1)

    score = int(((coverage * 0.5) + (emphasis_coverage * 0.5)) * 100)

    return DimensionScore(
        dimension="metrics_density",
        score=max(0, min(100, score)),
        weight=0.20,
        rationale=(
            f"{total_metrics} metrics found "
            f"(~{total_expected} expected from templates). "
            f"{emphasis_found}/{emphasis_total} VC emphasis metrics addressed."
        ),
        evidence_found=evidence_found,
        evidence_missing=evidence_missing,
    )


def _check_custom_checks(
    deck: PitchDeck, vc_profile: VCProfile
) -> list[CustomCheckResult]:
    """Evaluate VC-specific custom checks via keyword matching."""
    results = []
    all_content = " ".join(
        " ".join(
            [s.title, s.headline]
            + s.bullets
            + s.metrics
            + [s.speaker_notes]
            + s.vc_alignment_notes
        )
        for s in deck.slides
    ).lower()

    keyword_map = {
        "european sovereignty": ["sovereign", "european", "europe", "data sovereignty", "digital sovereignty"],
        "bottom-up market sizing": ["bottom-up", "bottom up", "som", "icp count", "arpu"],
        "capital efficiency": ["capital efficien", "burn multiple", "revenue-to-raised", "capital-efficient"],
        "customer evidence": ["customer", "pilot", "case study", "roi", "evidence"],
        "ai commoditization": ["commodit", "moat", "defensib", "proprietary"],
        "gross margin": ["gross margin", "margin trajectory"],
        "category creation": ["category", "defining", "new market", "category creation"],
    }

    for check in vc_profile.custom_checks:
        check_lower = check.lower()
        passed = False
        evidence = ""

        # Try keyword matching
        for pattern, keywords in keyword_map.items():
            if pattern in check_lower:
                matches = [kw for kw in keywords if kw in all_content]
                if matches:
                    passed = True
                    evidence = f"Keywords found: {', '.join(matches)}"
                break
        else:
            # Fallback: simple word overlap
            check_words = {
                w for w in check_lower.split() if len(w) > 3
            }
            content_words = set(all_content.split())
            overlap = check_words & content_words
            if len(overlap) >= 2:
                passed = True
                evidence = f"Content overlap: {', '.join(sorted(overlap)[:5])}"

        results.append(
            CustomCheckResult(
                check=check,
                passed=passed,
                evidence=evidence,
            )
        )
    return results


VALIDATOR_SYSTEM_PROMPT = """\
You are a senior VC partner evaluating pitch decks. Score with strict calibration:
- 0-20: Reject immediately — fundamental problems
- 21-40: Significant concerns — major rework needed
- 41-60: Borderline — needs substantial improvement
- 61-80: Strong candidate — minor improvements needed
- 81-100: Exceptional — rare, reserved for truly outstanding decks

DO NOT inflate scores. Most decks score 40-65. A score above 80 requires
exceptional evidence across all dimensions.

Evaluate step by step: analyze evidence FIRST, then assign scores.
Return ONLY valid JSON matching the requested format."""


def _score_qualitative(
    deck: PitchDeck,
    vc_profile: VCProfile,
    rule_findings: str,
) -> dict:
    """Use Claude to score narrative coherence, thesis alignment, and common mistakes.

    Returns dict with keys: narrative_coherence, thesis_alignment, common_mistakes,
    slide_quality (list), top_strengths, critical_gaps, recommendation.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise PitchDeckError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Get your key at https://console.anthropic.com/"
        )

    client = Anthropic()

    from pitchdeck.engine.narrative import _build_vc_context

    vc_context = _build_vc_context(vc_profile)

    system_messages = [
        {"type": "text", "text": VALIDATOR_SYSTEM_PROMPT},
        {
            "type": "text",
            "text": (
                f"<vc_profile>\n{vc_context}\n</vc_profile>\n\n"
                f"<rule_based_findings>\n{rule_findings}\n</rule_based_findings>"
            ),
            "cache_control": {"type": "ephemeral"},
        },
    ]

    deck_json = deck.model_dump_json(indent=2)

    user_prompt = f"""Evaluate this pitch deck for {vc_profile.name}.

<deck>
{deck_json}
</deck>

Score these dimensions (0-100 each) with detailed rationale:

1. NARRATIVE_COHERENCE: Do slides flow logically? Are transitions smooth?
   Is the investor psychology arc (Hook > Tension > Resolution > Proof > Trust > Ask) maintained?

2. THESIS_ALIGNMENT: How well does the deck address each of {vc_profile.name}'s
   thesis points? Evaluate against each thesis point individually.

3. COMMON_MISTAKES: Check for these specific issues:
{chr(10).join(f'   - {m}' for m in COMMON_MISTAKES)}

Also provide:
- Per-slide quality observations (list of objects with slide_number, quality_note)
- Top 3 strengths of the deck
- Top 3 critical gaps
- One-paragraph recommendation

OUTPUT FORMAT (return ONLY this JSON):
{{
    "narrative_coherence": {{
        "score": <0-100>,
        "rationale": "<explanation>",
        "evidence_found": ["<strength1>", ...],
        "evidence_missing": ["<weakness1>", ...]
    }},
    "thesis_alignment": {{
        "score": <0-100>,
        "rationale": "<explanation>",
        "evidence_found": ["<thesis point addressed>", ...],
        "evidence_missing": ["<thesis point not addressed>", ...]
    }},
    "common_mistakes": {{
        "score": <0-100>,
        "rationale": "<explanation>",
        "evidence_found": ["<good practice found>", ...],
        "evidence_missing": ["<mistake detected>", ...]
    }},
    "slide_quality": [
        {{"slide_number": 1, "quality_note": "<observation>"}},
        ...
    ],
    "top_strengths": ["<strength1>", "<strength2>", "<strength3>"],
    "critical_gaps": ["<gap1>", "<gap2>", "<gap3>"],
    "recommendation": "<one paragraph>"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        temperature=0.0,
        system=system_messages,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return _parse_validation_response(response)


def _parse_validation_response(response) -> dict:
    """Extract structured validation data from Claude response."""
    raw_text = response.content[0].text

    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        raise PitchDeckError(
            "Failed to parse validation response — "
            "no JSON found in Claude output"
        )

    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise PitchDeckError(
            f"Failed to parse validation JSON: {e}"
        ) from e


def _build_rule_summary(
    slide_scores: list[SlideValidationScore],
    completeness: DimensionScore,
    metrics_density: DimensionScore,
    custom_checks: list[CustomCheckResult],
) -> str:
    """Summarize rule-based findings for LLM context."""
    lines = [
        f"Completeness score: {completeness.score}/100",
        f"  Found: {', '.join(completeness.evidence_found)}",
        f"  Missing: {', '.join(completeness.evidence_missing)}",
        "",
        f"Metrics density score: {metrics_density.score}/100",
        f"  Found: {', '.join(metrics_density.evidence_found)}",
        f"  Missing: {', '.join(metrics_density.evidence_missing)}",
        "",
        "Per-slide issues:",
    ]
    for ss in slide_scores:
        if ss.issues:
            lines.append(
                f"  Slide {ss.slide_number} ({ss.slide_type}): "
                f"{'; '.join(ss.issues)}"
            )
    lines.append("")
    lines.append("VC custom check results:")
    for cc in custom_checks:
        status = "PASS" if cc.passed else "FAIL"
        lines.append(f"  [{status}] {cc.check}")
    return "\n".join(lines)


def _build_improvement_priorities(
    slide_scores: list[SlideValidationScore],
    custom_checks: list[CustomCheckResult],
    critical_gaps: list[str],
) -> list[str]:
    """Build a prioritized list of improvements, most impactful first."""
    priorities = []

    # Failed custom checks first (VC-specific, highest impact)
    for cc in custom_checks:
        if not cc.passed:
            priorities.append(f"Address VC requirement: {cc.check}")

    # LLM-identified critical gaps
    priorities.extend(critical_gaps)

    # Slides with the most issues
    scored = sorted(slide_scores, key=lambda s: s.score)
    for ss in scored[:3]:
        if ss.issues:
            priorities.append(
                f"Fix slide {ss.slide_number} ({ss.slide_type}): "
                f"{ss.issues[0]}"
            )

    return priorities


def validate_deck(
    deck: PitchDeck,
    vc_profile: VCProfile,
    pass_threshold: int = 60,
    skip_llm: bool = False,
) -> DeckValidationResult:
    """Validate a pitch deck using rule-based + optional LLM scoring.

    Args:
        deck: The PitchDeck to validate.
        vc_profile: VC profile with thesis points and custom checks.
        pass_threshold: Score threshold for pass/fail (0-100).
        skip_llm: If True, skip LLM scoring (rule-based only).

    Returns:
        DeckValidationResult with dimension scores, per-slide scores,
        custom check results, and prioritized improvements.
    """
    # 1. Rule-based per-slide scoring
    slide_scores = [_score_slide_rules(slide) for slide in deck.slides]

    # 2. Rule-based dimension scoring
    completeness = _score_completeness(deck, vc_profile)
    metrics_density = _score_metrics_density(deck, vc_profile)

    # 3. Custom checks
    custom_check_results = _check_custom_checks(deck, vc_profile)

    # 4. LLM qualitative scoring (optional)
    if not skip_llm:
        rule_summary = _build_rule_summary(
            slide_scores, completeness, metrics_density, custom_check_results
        )
        llm_data = _score_qualitative(deck, vc_profile, rule_summary)

        narrative = DimensionScore(
            dimension="narrative_coherence",
            score=max(0, min(100, llm_data["narrative_coherence"]["score"])),
            weight=0.20,
            rationale=llm_data["narrative_coherence"]["rationale"],
            evidence_found=llm_data["narrative_coherence"].get("evidence_found", []),
            evidence_missing=llm_data["narrative_coherence"].get("evidence_missing", []),
        )
        alignment = DimensionScore(
            dimension="thesis_alignment",
            score=max(0, min(100, llm_data["thesis_alignment"]["score"])),
            weight=0.20,
            rationale=llm_data["thesis_alignment"]["rationale"],
            evidence_found=llm_data["thesis_alignment"].get("evidence_found", []),
            evidence_missing=llm_data["thesis_alignment"].get("evidence_missing", []),
        )
        mistakes = DimensionScore(
            dimension="common_mistakes",
            score=max(0, min(100, llm_data["common_mistakes"]["score"])),
            weight=0.15,
            rationale=llm_data["common_mistakes"]["rationale"],
            evidence_found=llm_data["common_mistakes"].get("evidence_found", []),
            evidence_missing=llm_data["common_mistakes"].get("evidence_missing", []),
        )

        # Merge LLM per-slide quality notes into existing slide scores
        for sq in llm_data.get("slide_quality", []):
            num = sq.get("slide_number")
            note = sq.get("quality_note", "")
            if num and note:
                for ss in slide_scores:
                    if ss.slide_number == num and note:
                        ss.suggestions.append(note)

        top_strengths = llm_data.get("top_strengths", [])
        critical_gaps = llm_data.get("critical_gaps", [])
        recommendation = llm_data.get("recommendation", "")
    else:
        # Placeholder LLM dimensions when skipped
        narrative = DimensionScore(
            dimension="narrative_coherence",
            score=0,
            weight=0.20,
            rationale="LLM scoring skipped",
        )
        alignment = DimensionScore(
            dimension="thesis_alignment",
            score=0,
            weight=0.20,
            rationale="LLM scoring skipped",
        )
        mistakes = DimensionScore(
            dimension="common_mistakes",
            score=0,
            weight=0.15,
            rationale="LLM scoring skipped",
        )
        top_strengths = []
        critical_gaps = []
        recommendation = "LLM scoring skipped — run without --skip-llm for full assessment"

    dimension_scores = [
        completeness, metrics_density, narrative, alignment, mistakes
    ]

    # 5. Calculate weighted overall score
    overall = sum(d.score * d.weight for d in dimension_scores)
    overall_score = int(round(overall))

    # 6. Build improvement priorities from all issues
    improvement_priorities = _build_improvement_priorities(
        slide_scores, custom_check_results, critical_gaps
    )

    return DeckValidationResult(
        deck_name=deck.company_name,
        target_vc=deck.target_vc,
        validated_at=datetime.now().isoformat(),
        overall_score=max(0, min(100, overall_score)),
        pass_threshold=pass_threshold,
        pass_fail=overall_score >= pass_threshold,
        dimension_scores=dimension_scores,
        slide_scores=slide_scores,
        custom_check_results=custom_check_results,
        top_strengths=top_strengths,
        critical_gaps=critical_gaps,
        improvement_priorities=improvement_priorities,
        recommendation=recommendation,
    )
