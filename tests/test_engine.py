"""Tests for engine components: slides, gaps, and narrative."""

from unittest.mock import MagicMock, patch

import pytest

from pitchdeck.engine.gaps import (
    GAP_DEFINITIONS,
    _coerce_value,
    detect_gaps,
)
from pitchdeck.engine.slides import (
    SLIDE_TEMPLATES,
    get_narrative_arc,
    get_slide_templates,
)
from pitchdeck.models import CompanyProfile, PitchDeckError


class TestSlideTemplates:
    def test_has_15_templates(self):
        assert len(SLIDE_TEMPLATES) == 15

    def test_all_templates_have_required_fields(self):
        for template in SLIDE_TEMPLATES:
            assert template.slide_type
            assert template.purpose
            assert len(template.required_elements) > 0

    def test_template_types_unique(self):
        types = [t.slide_type for t in SLIDE_TEMPLATES]
        assert len(types) == len(set(types))

    def test_template_order_starts_with_cover(self):
        assert SLIDE_TEMPLATES[0].slide_type == "cover"

    def test_template_order_ends_with_ai_architecture(self):
        assert SLIDE_TEMPLATES[-1].slide_type == "ai-architecture"

    def test_get_slide_templates_filters_by_vc(self, sample_vc_profile):
        templates = get_slide_templates(sample_vc_profile)
        types = {t.slide_type for t in templates}
        assert types == {"cover", "problem", "solution", "traction", "the-ask"}

    def test_get_slide_templates_returns_all_when_no_prefs(
        self, sample_vc_profile
    ):
        sample_vc_profile.deck_preferences.must_include_slides = []
        templates = get_slide_templates(sample_vc_profile)
        assert len(templates) == 15

    def test_narrative_arc_contains_stages(self):
        arc = get_narrative_arc()
        assert "HOOK" in arc
        assert "TENSION" in arc
        assert "RESOLUTION" in arc
        assert "PROOF" in arc
        assert "TRUST" in arc
        assert "CALL TO ACTION" in arc


class TestGapDetection:
    def test_detects_missing_fields(self, sample_company_with_gaps):
        gaps = detect_gaps(sample_company_with_gaps, SLIDE_TEMPLATES)
        fields = {g.field for g in gaps}
        assert "name" in fields
        assert "product_name" in fields
        assert "target_raise_eur" in fields

    def test_skips_filled_fields(self, sample_company):
        gaps = detect_gaps(sample_company, SLIDE_TEMPLATES)
        fields = {g.field for g in gaps}
        assert "name" not in fields
        assert "product_name" not in fields
        assert "revenue_eur" not in fields

    def test_detects_none_fields(self, sample_company):
        gaps = detect_gaps(sample_company, SLIDE_TEMPLATES)
        fields = {g.field for g in gaps}
        assert "growth_rate_yoy" in fields
        assert "ndr_percent" in fields

    def test_gap_definitions_have_importance(self):
        for gap in GAP_DEFINITIONS:
            assert gap.importance in ("critical", "important", "nice-to-have")

    def test_coerce_numeric_value(self):
        assert _coerce_value("target_raise_eur", "5,000,000") == 5000000.0
        assert _coerce_value("ndr_percent", "115") == 115.0
        assert _coerce_value("burn_rate_monthly_eur", "EUR 50000") == 50000.0

    def test_coerce_int_value(self):
        assert _coerce_value("customer_count", "42") == 42
        assert _coerce_value("employee_count", "1,000") == 1000

    def test_coerce_string_value(self):
        assert _coerce_value("name", "TestCo") == "TestCo"

    def test_coerce_invalid_numeric_returns_string(self):
        assert _coerce_value("target_raise_eur", "lots") == "lots"


class TestNarrativeEngine:
    def test_generate_deck_requires_api_key(
        self, sample_company, sample_vc_profile
    ):
        templates = get_slide_templates(sample_vc_profile)
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(PitchDeckError, match="ANTHROPIC_API_KEY"):
                from pitchdeck.engine.narrative import generate_deck

                generate_deck(sample_company, sample_vc_profile, templates)

    def test_build_vc_context(self, sample_vc_profile):
        from pitchdeck.engine.narrative import build_vc_context

        context = build_vc_context(sample_vc_profile)
        assert "Test VC" in context
        assert "AI infrastructure" in context
        assert "Capital efficiency" in context

    def test_build_slide_instructions(self):
        from pitchdeck.engine.narrative import _build_slide_instructions

        instructions = _build_slide_instructions(SLIDE_TEMPLATES[:3])
        assert "Slide 1: cover" in instructions
        assert "Slide 2: executive-summary" in instructions
        assert "Slide 3: problem" in instructions

    def test_parse_deck_response(self, sample_company, sample_vc_profile):
        from pitchdeck.engine.narrative import _parse_deck_response

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text="""{
            "narrative_arc": "Test arc",
            "gaps_identified": ["Missing NDR"],
            "slides": [
                {
                    "slide_number": 1,
                    "slide_type": "cover",
                    "title": "Test Title",
                    "headline": "Test Headline",
                    "bullets": ["Point 1"],
                    "metrics": [],
                    "speaker_notes": "Say this",
                    "transition_to_next": "Next up...",
                    "vc_alignment_notes": ["Aligns with thesis"]
                }
            ]
        }"""
            )
        ]

        deck = _parse_deck_response(
            mock_response, sample_company, sample_vc_profile
        )
        assert deck.company_name == "Neurawork"
        assert deck.target_vc == "Test VC"
        assert len(deck.slides) == 1
        assert deck.slides[0].title == "Test Title"
        assert deck.gaps_identified == ["Missing NDR"]

    def test_parse_deck_response_invalid_json(
        self, sample_company, sample_vc_profile
    ):
        from pitchdeck.engine.narrative import _parse_deck_response

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Not JSON at all")]

        with pytest.raises(PitchDeckError, match="no JSON found"):
            _parse_deck_response(
                mock_response, sample_company, sample_vc_profile
            )

    def test_parse_deck_response_empty_response(
        self, sample_company, sample_vc_profile
    ):
        from pitchdeck.engine.narrative import _parse_deck_response

        mock_response = MagicMock()
        mock_response.content = []

        with pytest.raises(PitchDeckError, match="empty response"):
            _parse_deck_response(
                mock_response, sample_company, sample_vc_profile
            )

    def test_parse_deck_response_non_text_block(
        self, sample_company, sample_vc_profile
    ):
        from pitchdeck.engine.narrative import _parse_deck_response

        mock_response = MagicMock()
        block = MagicMock(spec=[])  # no .text attribute
        mock_response.content = [block]

        with pytest.raises(PitchDeckError, match="expected text block"):
            _parse_deck_response(
                mock_response, sample_company, sample_vc_profile
            )


class TestGenerateDeckAPIErrors:
    """Test that API errors from generate_deck are wrapped as PitchDeckError."""

    def test_authentication_error(self, sample_company, sample_vc_profile):
        from anthropic import AuthenticationError

        from pitchdeck.engine.narrative import generate_deck

        templates = get_slide_templates(sample_vc_profile)
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "bad-key"}):
            with patch("pitchdeck.engine.narrative.Anthropic") as mock_anthropic:
                mock_anthropic.return_value.messages.create.side_effect = (
                    AuthenticationError(
                        message="Invalid API key",
                        response=MagicMock(status_code=401),
                        body=None,
                    )
                )
                with pytest.raises(PitchDeckError, match="Invalid API key"):
                    generate_deck(sample_company, sample_vc_profile, templates)

    def test_rate_limit_error(self, sample_company, sample_vc_profile):
        from anthropic import RateLimitError

        from pitchdeck.engine.narrative import generate_deck

        templates = get_slide_templates(sample_vc_profile)
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("pitchdeck.engine.narrative.Anthropic") as mock_anthropic:
                mock_anthropic.return_value.messages.create.side_effect = (
                    RateLimitError(
                        message="Rate limit exceeded",
                        response=MagicMock(status_code=429),
                        body=None,
                    )
                )
                with pytest.raises(PitchDeckError, match="rate limit"):
                    generate_deck(sample_company, sample_vc_profile, templates)

    def test_timeout_error(self, sample_company, sample_vc_profile):
        from anthropic import APITimeoutError

        from pitchdeck.engine.narrative import generate_deck

        templates = get_slide_templates(sample_vc_profile)
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("pitchdeck.engine.narrative.Anthropic") as mock_anthropic:
                mock_anthropic.return_value.messages.create.side_effect = (
                    APITimeoutError(request=MagicMock())
                )
                with pytest.raises(PitchDeckError, match="timed out"):
                    generate_deck(sample_company, sample_vc_profile, templates)

    def test_api_status_error(self, sample_company, sample_vc_profile):
        from anthropic import APIStatusError

        from pitchdeck.engine.narrative import generate_deck

        templates = get_slide_templates(sample_vc_profile)
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("pitchdeck.engine.narrative.Anthropic") as mock_anthropic:
                mock_anthropic.return_value.messages.create.side_effect = (
                    APIStatusError(
                        message="Internal server error",
                        response=MagicMock(status_code=500),
                        body=None,
                    )
                )
                with pytest.raises(PitchDeckError, match="API error"):
                    generate_deck(sample_company, sample_vc_profile, templates)
