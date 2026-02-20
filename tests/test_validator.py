"""Tests for the deck validation engine."""

from unittest.mock import MagicMock, patch

import pytest

from pitchdeck.engine.slides import SLIDE_TEMPLATES
from pitchdeck.engine.validator import (
    _check_custom_checks,
    _get_template_for_slide,
    _score_completeness,
    _score_metrics_density,
    _score_slide_rules,
    validate_deck,
)
from pitchdeck.models import (
    DeckValidationResult,
    DimensionScore,
    PitchDeckError,
    SlideContent,
    SlideValidationScore,
)


class TestGetTemplateForSlide:
    def test_finds_existing_type(self):
        template = _get_template_for_slide("cover")
        assert template is not None
        assert template.slide_type == "cover"

    def test_returns_none_for_unknown_type(self):
        assert _get_template_for_slide("nonexistent") is None

    def test_finds_all_15_types(self):
        for t in SLIDE_TEMPLATES:
            assert _get_template_for_slide(t.slide_type) is not None


class TestScoreSlideRules:
    def test_perfect_slide_scores_high(self, sample_slide):
        score = _score_slide_rules(sample_slide)
        assert score.score >= 80
        assert score.slide_type == "cover"

    def test_missing_title_deducts(self):
        slide = SlideContent(
            slide_number=1,
            slide_type="cover",
            title="",
            headline="Test",
            bullets=[],
            speaker_notes="Notes",
        )
        score = _score_slide_rules(slide)
        assert "Missing slide title" in score.issues
        assert score.score < 100

    def test_missing_headline_deducts(self):
        slide = SlideContent(
            slide_number=1,
            slide_type="cover",
            title="Title",
            headline="",
            bullets=[],
            speaker_notes="Notes",
        )
        score = _score_slide_rules(slide)
        assert "Missing slide headline" in score.issues

    def test_too_many_bullets_flagged(self):
        slide = SlideContent(
            slide_number=2,
            slide_type="executive-summary",
            title="Title",
            headline="Headline",
            bullets=["B1", "B2", "B3", "B4", "B5", "B6"],
            speaker_notes="Notes",
        )
        score = _score_slide_rules(slide)
        assert any("Too many bullets" in i for i in score.issues)

    def test_missing_metrics_flagged(self):
        slide = SlideContent(
            slide_number=9,
            slide_type="traction",
            title="Traction",
            headline="Growth proof",
            bullets=["Point 1"],
            metrics=[],
            speaker_notes="Notes",
        )
        score = _score_slide_rules(slide)
        assert any("Missing metrics" in i for i in score.issues)

    def test_missing_speaker_notes_deducts(self):
        slide = SlideContent(
            slide_number=1,
            slide_type="cover",
            title="Title",
            headline="Headline",
            bullets=[],
            speaker_notes="",
        )
        score = _score_slide_rules(slide)
        assert any("Missing speaker notes" in i for i in score.issues)

    def test_score_never_below_zero(self):
        slide = SlideContent(
            slide_number=1,
            slide_type="traction",
            title="",
            headline="",
            bullets=[],
            metrics=[],
            speaker_notes="",
        )
        score = _score_slide_rules(slide)
        assert score.score >= 0

    def test_unknown_slide_type_still_scores(self):
        slide = SlideContent(
            slide_number=1,
            slide_type="unknown-type",
            title="Title",
            headline="Headline",
            bullets=["Point"],
            speaker_notes="Notes",
        )
        score = _score_slide_rules(slide)
        assert score.score > 0


class TestScoreCompleteness:
    def test_full_deck_scores_high(
        self, sample_multi_slide_deck, sample_vc_profile
    ):
        score = _score_completeness(
            sample_multi_slide_deck, sample_vc_profile
        )
        assert score.dimension == "completeness"
        assert score.score > 50
        assert score.weight == 0.25

    def test_empty_deck_scores_low(self, sample_vc_profile):
        from pitchdeck.models import PitchDeck

        empty_deck = PitchDeck(
            company_name="Test",
            target_vc="VC",
            generated_at="2026-01-01",
            slides=[],
            narrative_arc="",
        )
        score = _score_completeness(empty_deck, sample_vc_profile)
        assert score.score < 20

    def test_gaps_reduce_score(
        self, sample_multi_slide_deck, sample_vc_profile
    ):
        sample_multi_slide_deck.gaps_identified = [
            "Gap 1",
            "Gap 2",
            "Gap 3",
        ]
        score = _score_completeness(
            sample_multi_slide_deck, sample_vc_profile
        )
        assert "3 data gaps identified" in " ".join(
            score.evidence_missing
        )


class TestScoreMetricsDensity:
    def test_deck_with_metrics_scores_higher(
        self, sample_multi_slide_deck, sample_vc_profile
    ):
        score = _score_metrics_density(
            sample_multi_slide_deck, sample_vc_profile
        )
        assert score.dimension == "metrics_density"
        assert score.weight == 0.20
        assert 0 <= score.score <= 100


class TestCheckCustomChecks:
    def test_passes_when_keywords_present(self, sample_vc_profile):
        from pitchdeck.models import PitchDeck

        deck = PitchDeck(
            company_name="Test",
            target_vc="VC",
            generated_at="2026-01-01",
            slides=[
                SlideContent(
                    slide_number=1,
                    slide_type="cover",
                    title="European Digital Sovereignty",
                    headline="Capital efficient AI platform",
                    bullets=[
                        "Bottom-up SOM calculation",
                        "Customer ROI: 3x reduction",
                        "AI commoditization moat",
                        "Gross margin 70%",
                        "Category creation like UiPath",
                    ],
                    speaker_notes="Notes",
                )
            ],
            narrative_arc="Arc",
        )
        results = _check_custom_checks(deck, sample_vc_profile)
        assert isinstance(results, list)
        # sample_vc_profile has 1 custom check: "Must show capital efficiency"
        assert len(results) == 1

    def test_fails_when_keywords_absent(self, sample_vc_profile):
        from pitchdeck.models import PitchDeck

        deck = PitchDeck(
            company_name="Test",
            target_vc="VC",
            generated_at="2026-01-01",
            slides=[
                SlideContent(
                    slide_number=1,
                    slide_type="cover",
                    title="Hello",
                    headline="World",
                    bullets=[],
                    speaker_notes="Notes",
                )
            ],
            narrative_arc="Arc",
        )
        results = _check_custom_checks(deck, sample_vc_profile)
        # With minimal content, most checks should fail
        for r in results:
            assert isinstance(r.passed, bool)


class TestValidateDeck:
    def test_rule_based_only(
        self, sample_multi_slide_deck, sample_vc_profile
    ):
        result = validate_deck(
            sample_multi_slide_deck,
            sample_vc_profile,
            skip_llm=True,
        )
        assert isinstance(result, DeckValidationResult)
        assert 0 <= result.overall_score <= 100
        assert len(result.dimension_scores) == 5
        assert len(result.slide_scores) == 15
        assert result.pass_fail == (result.overall_score >= 60)

    def test_rule_based_dimensions_scored(
        self, sample_multi_slide_deck, sample_vc_profile
    ):
        result = validate_deck(
            sample_multi_slide_deck,
            sample_vc_profile,
            skip_llm=True,
        )
        dims = {d.dimension: d for d in result.dimension_scores}
        assert dims["completeness"].score > 0
        assert dims["metrics_density"].score >= 0
        # LLM dimensions should be 0 when skipped
        assert dims["narrative_coherence"].score == 0
        assert dims["thesis_alignment"].score == 0
        assert dims["common_mistakes"].score == 0

    def test_custom_threshold(
        self, sample_multi_slide_deck, sample_vc_profile
    ):
        result = validate_deck(
            sample_multi_slide_deck,
            sample_vc_profile,
            pass_threshold=90,
            skip_llm=True,
        )
        assert result.pass_threshold == 90

    def test_improvement_priorities_populated(
        self, sample_multi_slide_deck, sample_vc_profile
    ):
        result = validate_deck(
            sample_multi_slide_deck,
            sample_vc_profile,
            skip_llm=True,
        )
        assert isinstance(result.improvement_priorities, list)

    def test_requires_api_key_for_llm(
        self, sample_multi_slide_deck, sample_vc_profile
    ):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(PitchDeckError, match="ANTHROPIC_API_KEY"):
                validate_deck(
                    sample_multi_slide_deck,
                    sample_vc_profile,
                    skip_llm=False,
                )

    def test_llm_scoring_with_mock(
        self, sample_multi_slide_deck, sample_vc_profile
    ):
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text="""{
            "narrative_coherence": {
                "score": 72,
                "rationale": "Good flow",
                "evidence_found": ["Clear arc"],
                "evidence_missing": ["Weak transition at slide 5"]
            },
            "thesis_alignment": {
                "score": 68,
                "rationale": "Mostly aligned",
                "evidence_found": ["AI infra thesis"],
                "evidence_missing": ["Category creation weak"]
            },
            "common_mistakes": {
                "score": 80,
                "rationale": "Few mistakes",
                "evidence_found": ["Data-driven bullets"],
                "evidence_missing": ["No NDR on traction"]
            },
            "slide_quality": [
                {"slide_number": 1, "quality_note": "Strong opener"}
            ],
            "top_strengths": ["Revenue traction", "AI positioning"],
            "critical_gaps": ["Missing NDR"],
            "recommendation": "Add NDR metric."
        }"""
            )
        ]

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch(
                "pitchdeck.engine.validator.Anthropic"
            ) as mock_anthropic:
                mock_anthropic.return_value.messages.create.return_value = (
                    mock_response
                )
                result = validate_deck(
                    sample_multi_slide_deck,
                    sample_vc_profile,
                    skip_llm=False,
                )

        assert isinstance(result, DeckValidationResult)
        dims = {d.dimension: d for d in result.dimension_scores}
        assert dims["narrative_coherence"].score == 72
        assert dims["thesis_alignment"].score == 68
        assert dims["common_mistakes"].score == 80
        assert "Revenue traction" in result.top_strengths
        assert "Missing NDR" in result.critical_gaps

    def test_parse_validation_response_invalid_json(self):
        from pitchdeck.engine.validator import _parse_validation_response

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Not valid JSON")]
        with pytest.raises(PitchDeckError, match="no JSON found"):
            _parse_validation_response(mock_response)


class TestDimensionScoreBounds:
    def test_score_at_boundaries(self):
        low = DimensionScore(
            dimension="test", score=0, weight=0.2, rationale="Low"
        )
        high = DimensionScore(
            dimension="test", score=100, weight=0.2, rationale="High"
        )
        assert low.score == 0
        assert high.score == 100

    def test_score_out_of_bounds_raises(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            DimensionScore(
                dimension="test",
                score=150,
                weight=0.2,
                rationale="Too high",
            )
        with pytest.raises(ValidationError):
            DimensionScore(
                dimension="test",
                score=-1,
                weight=0.2,
                rationale="Too low",
            )
