"""Pitch deck validation engine — rule-based + LLM scoring."""

import json
import os
import re
from datetime import datetime
from typing import List, Optional

from anthropic import (
    Anthropic,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from pitchdeck.engine.narrative import build_vc_context

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

        # Empty bullets check — only for slides expecting bullets (max_bullets > 0)
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
    """Score deck completeness: slide count vs preferred, required slide type coverage, and speaker notes presence.

    Note: gaps_identified is recorded in evidence_missing but does not affect the score axes.
    """
    evidence_found = []
    evidence_missing = []

    # Axis 1: Slide count vs preferred
    expected = vc_profile.deck_preferences.preferred_slide_count
    actual = len(deck.slides)
    slide_count_score = min(100, int((actual / max(expected, 1)) * 100))
    if actual >= expected:
        evidence_found.append(f"{actual}/{expected} slides present")
    else:
        evidence_missing.append(
            f"Only {actual}/{expected} slides present"
        )

    # Axis 2: Required slide type coverage
    slide_types = {s.slide_type for s in deck.slides}
    must_include = set(vc_profile.deck_preferences.must_include_slides)
    if must_include:
        present = must_include & slide_types
        missing = must_include - slide_types
        type_score = int((len(present) / len(must_include)) * 100)
        if present:
            evidence_found.append(
                f"Required slide types present: {', '.join(sorted(present))}"
            )
        if missing:
            evidence_missing.append(
                f"Missing required slide types: {', '.join(sorted(missing))}"
            )
    else:
        type_score = 100  # no requirements = full marks

    # Axis 3: Speaker notes coverage
    notes_count = sum(
        1 for s in deck.slides if s.speaker_notes.strip()
    )
    notes_score = int((notes_count / max(len(deck.slides), 1)) * 100)
    evidence_found.append(
        f"Speaker notes on {notes_count}/{len(deck.slides)} slides"
    )

    # Gaps (informational only — recorded in evidence but does not affect score)
    if deck.gaps_identified:
        evidence_missing.append(
            f"{len(deck.gaps_identified)} data gaps identified: "
            f"{', '.join(deck.gaps_identified[:5])}"
        )

    # Average the three independent axes
    score = int(round((slide_count_score + type_score + notes_score) / 3))

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
    if emphasis:
        emphasis_found = sum(1 for e in evidence_found if e.startswith("Found:"))
        emphasis_total = len(emphasis)
        emphasis_coverage = emphasis_found / emphasis_total
        score = int(((coverage * 0.5) + (emphasis_coverage * 0.5)) * 100)
        rationale = (
            f"{total_metrics} metrics found "
            f"(~{total_expected} expected from templates). "
            f"{emphasis_found}/{emphasis_total} VC emphasis metrics addressed."
        )
    else:
        # No VC emphasis configured — score based on template coverage only
        score = int(coverage * 100)
        rationale = (
            f"{total_metrics} metrics found "
            f"(~{total_expected} expected from templates)."
        )

    return DimensionScore(
        dimension="metrics_density",
        score=max(0, min(100, score)),
        weight=0.20,
        rationale=rationale,
        evidence_found=evidence_found,
        evidence_missing=evidence_missing,
    )


def _check_custom_checks(
    deck: PitchDeck, vc_profile: VCProfile
) -> List[CustomCheckResult]:
    """Evaluate VC-specific custom checks via keyword matching.

    Uses a hardcoded keyword_map for known check patterns. Falls back to
    word-overlap heuristic (>=2 matching words longer than 3 chars) for
    checks that don't match any known pattern.
    """
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
        matched_pattern = False
        for pattern, keywords in keyword_map.items():
            if pattern in check_lower:
                matched_pattern = True
                matches = [kw for kw in keywords if kw in all_content]
                if matches:
                    passed = True
                    evidence = f"Keywords found: {', '.join(matches)}"
                else:
                    evidence = f"Keywords checked but not found: {', '.join(keywords)}"
                break

        if not matched_pattern:
            # Fallback: simple word overlap
            check_words = {
                w for w in check_lower.split() if len(w) > 3
            }
            content_words = set(all_content.split())
            overlap = check_words & content_words
            if len(overlap) >= 2:
                passed = True
                evidence = f"Weak match (word overlap): {', '.join(sorted(overlap)[:5])}"
            else:
                evidence = (
                    f"No keyword match found. "
                    f"Checked words: {', '.join(sorted(check_words)[:5])}"
                )

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

    Returns dict with keys:
        Required (raise PitchDeckError if missing):
            narrative_coherence, thesis_alignment, common_mistakes —
            each a dict with "score" (int) and "rationale" (str).
        Optional (.get() with defaults):
            slide_quality (list of {slide_number, quality_note}),
            top_strengths (list[str]), critical_gaps (list[str]),
            recommendation (str).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise PitchDeckError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Get your key at https://console.anthropic.com/"
        )

    client = Anthropic()
    vc_context = build_vc_context(vc_profile)

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

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            temperature=0.0,
            system=system_messages,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except AuthenticationError:
        raise PitchDeckError(
            "Invalid API key. Check ANTHROPIC_API_KEY at https://console.anthropic.com/"
        )
    except RateLimitError:
        raise PitchDeckError(
            "Anthropic API rate limit hit. Wait a moment and try again."
        )
    except APITimeoutError:
        raise PitchDeckError(
            "Anthropic API timed out. The deck may be too large — "
            "try --skip-llm for rule-based scoring only."
        )
    except APIStatusError as e:
        raise PitchDeckError(
            f"Anthropic API error (HTTP {e.status_code}): {e.message}"
        ) from e
    except Exception as e:
        raise PitchDeckError(
            f"Unexpected {type(e).__name__} calling Claude API: {e}"
        ) from e

    return _parse_validation_response(response)


def _parse_validation_response(response) -> dict:
    """Extract structured validation data from Claude response."""
    if not response.content:
        raise PitchDeckError(
            "Claude returned an empty response. "
            "The deck may be too large — try reducing slide count."
        )
    content_block = response.content[0]
    if not hasattr(content_block, "text"):
        raise PitchDeckError(
            f"Unexpected Claude response format: "
            f"expected text block, got {type(content_block).__name__}"
        )
    raw_text = content_block.text

    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        snippet = raw_text[:200] + ("..." if len(raw_text) > 200 else "")
        raise PitchDeckError(
            "Failed to parse validation response — "
            f"no JSON found in Claude output. Response starts with: {snippet}"
        )

    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError as e:
        extracted = json_match.group()
        snippet = extracted[:200] + ("..." if len(extracted) > 200 else "")
        raise PitchDeckError(
            f"Failed to parse validation JSON: {e}. "
            f"Extracted text starts with: {snippet}"
        ) from e


def _build_rule_summary(
    slide_scores: List[SlideValidationScore],
    completeness: DimensionScore,
    metrics_density: DimensionScore,
    custom_checks: List[CustomCheckResult],
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
    slide_scores: List[SlideValidationScore],
    custom_checks: List[CustomCheckResult],
    critical_gaps: List[str],
) -> List[str]:
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
            When True, LLM dimension weights are set to 0.0 and
            rule-based dimension weights are rescaled to sum to 1.0.

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

        def _extract_dimension(data: dict, key: str) -> dict:
            """Safely extract a dimension dict from LLM response."""
            dim = data.get(key)
            if not isinstance(dim, dict):
                available_keys = list(data.keys()) if isinstance(data, dict) else "non-dict"
                raise PitchDeckError(
                    f"LLM response missing or malformed '{key}' dimension. "
                    f"Available keys: {available_keys}"
                )
            if "score" not in dim or "rationale" not in dim:
                missing = [f for f in ["score", "rationale"] if f not in dim]
                raise PitchDeckError(
                    f"LLM response '{key}' missing required fields: {missing}. "
                    f"Got: {list(dim.keys())}"
                )
            try:
                dim["score"] = int(dim["score"])
            except (TypeError, ValueError) as e:
                raise PitchDeckError(
                    f"LLM response '{key}' has non-numeric score: {dim['score']!r}"
                ) from e
            return dim

        nc = _extract_dimension(llm_data, "narrative_coherence")
        narrative = DimensionScore(
            dimension="narrative_coherence",
            score=max(0, min(100, nc["score"])),
            weight=0.20,
            rationale=nc["rationale"],
            evidence_found=nc.get("evidence_found", []),
            evidence_missing=nc.get("evidence_missing", []),
        )
        ta = _extract_dimension(llm_data, "thesis_alignment")
        alignment = DimensionScore(
            dimension="thesis_alignment",
            score=max(0, min(100, ta["score"])),
            weight=0.20,
            rationale=ta["rationale"],
            evidence_found=ta.get("evidence_found", []),
            evidence_missing=ta.get("evidence_missing", []),
        )
        cm = _extract_dimension(llm_data, "common_mistakes")
        mistakes = DimensionScore(
            dimension="common_mistakes",
            score=max(0, min(100, cm["score"])),
            weight=0.15,
            rationale=cm["rationale"],
            evidence_found=cm.get("evidence_found", []),
            evidence_missing=cm.get("evidence_missing", []),
        )

        # Merge LLM per-slide quality notes into existing slide scores
        for sq in llm_data.get("slide_quality", []):
            num = sq.get("slide_number")
            note = sq.get("quality_note", "")
            if num and note:
                for i, ss in enumerate(slide_scores):
                    if ss.slide_number == num:
                        slide_scores[i] = ss.model_copy(
                            update={"suggestions": ss.suggestions + [note]}
                        )

        top_strengths = llm_data.get("top_strengths", [])
        critical_gaps = llm_data.get("critical_gaps", [])
        recommendation = llm_data.get("recommendation", "")
    else:
        # When LLM is skipped, rescale rule-based weights to sum to 1.0
        # so rule-based mode can still produce meaningful scores
        rule_weight_sum = completeness.weight + metrics_density.weight  # 0.45
        completeness = completeness.model_copy(
            update={"weight": completeness.weight / rule_weight_sum}
        )
        metrics_density = metrics_density.model_copy(
            update={"weight": metrics_density.weight / rule_weight_sum}
        )

        narrative = DimensionScore(
            dimension="narrative_coherence",
            score=0,
            weight=0.0,
            rationale="LLM scoring skipped",
        )
        alignment = DimensionScore(
            dimension="thesis_alignment",
            score=0,
            weight=0.0,
            rationale="LLM scoring skipped",
        )
        mistakes = DimensionScore(
            dimension="common_mistakes",
            score=0,
            weight=0.0,
            rationale="LLM scoring skipped",
        )
        top_strengths = []
        critical_gaps = []
        recommendation = "LLM scoring skipped — run without --skip-llm for full assessment"

    dimension_scores = [
        completeness, metrics_density, narrative, alignment, mistakes
    ]

    # 5. Verify dimension weights sum to ~1.0
    weight_sum = sum(d.weight for d in dimension_scores)
    if abs(weight_sum - 1.0) > 0.01:
        raise PitchDeckError(
            f"Dimension weights must sum to ~1.0, got {weight_sum:.3f}"
        )

    # 6. Build improvement priorities from all issues
    improvement_priorities = _build_improvement_priorities(
        slide_scores, custom_check_results, critical_gaps
    )

    return DeckValidationResult(
        deck_name=deck.company_name,
        target_vc=deck.target_vc,
        validated_at=datetime.now().isoformat(),
        pass_threshold=pass_threshold,
        dimension_scores=dimension_scores,
        slide_scores=slide_scores,
        custom_check_results=custom_check_results,
        top_strengths=top_strengths,
        critical_gaps=critical_gaps,
        improvement_priorities=improvement_priorities,
        recommendation=recommendation,
    )
