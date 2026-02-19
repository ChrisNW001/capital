"""Tests for Pydantic data models."""

import pytest
from pydantic import ValidationError

from pitchdeck.models import (
    CompanyProfile,
    DeckPreferences,
    GapQuestion,
    PitchDeck,
    SlideContent,
    SlideTemplate,
    TeamMember,
    VCPartner,
    VCProfile,
)


class TestCompanyProfile:
    def test_creates_valid_profile(self, sample_company):
        assert sample_company.name == "Neurawork"
        assert sample_company.revenue_eur == 2300000
        assert sample_company.customer_count == 4

    def test_required_fields(self):
        with pytest.raises(ValidationError):
            CompanyProfile()

    def test_optional_fields_default_none(self, sample_company):
        assert sample_company.growth_rate_yoy is None
        assert sample_company.ndr_percent is None
        assert sample_company.gross_margin_percent is None
        assert sample_company.burn_rate_monthly_eur is None

    def test_list_defaults_empty(self):
        profile = CompanyProfile(
            name="Test",
            product_name="Prod",
            one_liner="Test product",
            founded_year=2024,
            employee_count=5,
            revenue_eur=100000,
            revenue_type="revenue",
            funding_stage="seed",
        )
        assert profile.key_customers == []
        assert profile.use_of_funds == []
        assert profile.competitors == []
        assert profile.differentiators == []

    def test_model_copy_with_update(self, sample_company):
        updated = sample_company.model_copy(
            update={"growth_rate_yoy": 150.0}
        )
        assert updated.growth_rate_yoy == 150.0
        assert updated.name == "Neurawork"


class TestTeamMember:
    def test_creates_valid_member(self):
        member = TeamMember(
            name="Jane Doe", role="CTO", background="PhD CS, ex-Google"
        )
        assert member.name == "Jane Doe"
        assert member.role == "CTO"


class TestVCProfile:
    def test_creates_valid_profile(self, sample_vc_profile):
        assert sample_vc_profile.name == "Test VC"
        assert len(sample_vc_profile.thesis_points) == 2

    def test_required_fields(self):
        with pytest.raises(ValidationError):
            VCProfile(name="Test")

    def test_deck_preferences_defaults(self):
        profile = VCProfile(
            name="Minimal VC",
            fund_name="Fund I",
            stage_focus=["seed"],
            sector_focus=["ai"],
            geo_focus=["EU"],
            thesis_points=["AI"],
        )
        assert profile.deck_preferences.preferred_slide_count == 15
        assert profile.deck_preferences.narrative_style == "data-driven"


class TestDeckPreferences:
    def test_defaults(self):
        prefs = DeckPreferences()
        assert prefs.preferred_slide_count == 15
        assert prefs.narrative_style == "data-driven"
        assert prefs.market_sizing_approach == "bottom-up"
        assert prefs.must_include_slides == []
        assert prefs.metrics_emphasis == []


class TestSlideTemplate:
    def test_creates_valid_template(self):
        template = SlideTemplate(
            slide_type="cover",
            purpose="10-second filter",
            required_elements=["company_name"],
        )
        assert template.slide_type == "cover"
        assert template.max_bullets == 5
        assert template.word_limit == 150


class TestSlideContent:
    def test_creates_valid_slide(self, sample_slide):
        assert sample_slide.slide_number == 1
        assert sample_slide.slide_type == "cover"
        assert len(sample_slide.bullets) == 2

    def test_optional_fields_default(self):
        slide = SlideContent(
            slide_number=1,
            slide_type="cover",
            title="Test",
            headline="Test headline",
            bullets=["Point 1"],
            speaker_notes="Say this.",
        )
        assert slide.metrics == []
        assert slide.transition_to_next == ""
        assert slide.vc_alignment_notes == []


class TestPitchDeck:
    def test_creates_valid_deck(self, sample_deck):
        assert sample_deck.company_name == "Neurawork"
        assert len(sample_deck.slides) == 1
        assert sample_deck.gaps_identified == ["NDR percentage missing"]

    def test_empty_slides_allowed(self):
        deck = PitchDeck(
            company_name="Test",
            target_vc="VC",
            generated_at="2026-01-01",
            slides=[],
            narrative_arc="Test arc",
        )
        assert deck.slides == []


class TestGapQuestion:
    def test_creates_valid_gap(self):
        gap = GapQuestion(
            field="ndr_percent",
            question="What is NDR?",
            importance="critical",
        )
        assert gap.field == "ndr_percent"
        assert gap.importance == "critical"
        assert gap.default is None
        assert gap.choices == []

    def test_with_choices(self):
        gap = GapQuestion(
            field="funding_stage",
            question="Stage?",
            importance="important",
            choices=["seed", "series-a"],
        )
        assert len(gap.choices) == 2
