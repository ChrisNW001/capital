"""Shared test fixtures for pitch deck generator."""

import pytest
from ruamel.yaml import YAML

from pitchdeck.models import (
    CompanyProfile,
    DeckPreferences,
    PitchDeck,
    SlideContent,
    VCPartner,
    VCProfile,
)


@pytest.fixture
def sample_company():
    return CompanyProfile(
        name="Neurawork",
        product_name="NeuraPlox",
        one_liner="The AI Control Plane for European SMEs",
        founded_year=2024,
        employee_count=20,
        revenue_eur=2300000,
        revenue_type="revenue",
        growth_rate_yoy=None,
        customer_count=4,
        funding_stage="bootstrapped",
        raw_document_text="Sample document text for testing purposes.",
    )


@pytest.fixture
def sample_company_with_gaps():
    """Company profile with many missing fields."""
    return CompanyProfile(
        name="",
        product_name="",
        one_liner="",
        founded_year=0,
        employee_count=0,
        revenue_eur=0,
        revenue_type="revenue",
        funding_stage="bootstrapped",
        raw_document_text="Some text",
    )


@pytest.fixture
def sample_vc_profile():
    return VCProfile(
        name="Test VC",
        fund_name="Fund I",
        aum_eur=1000000000,
        stage_focus=["seed", "series-a"],
        sector_focus=["enterprise-ai"],
        geo_focus=["DACH"],
        thesis_points=["AI infrastructure", "Capital efficiency"],
        portfolio_companies=["Company A", "Company B"],
        key_partners=[
            VCPartner(name="John Doe", focus="AI", background="PhD ML")
        ],
        deck_preferences=DeckPreferences(
            preferred_slide_count=15,
            must_include_slides=[
                "cover",
                "problem",
                "solution",
                "traction",
                "the-ask",
            ],
            metrics_emphasis=["ARR", "NDR"],
            narrative_style="data-driven",
            market_sizing_approach="bottom-up",
        ),
        custom_checks=["Must show capital efficiency"],
    )


@pytest.fixture
def sample_vc_yaml(tmp_path):
    """Create a temporary VC profile YAML file."""
    yaml = YAML()
    data = {
        "name": "Test VC",
        "fund_name": "Fund I",
        "aum_eur": 1000000000,
        "stage_focus": ["seed"],
        "sector_focus": ["enterprise-ai"],
        "geo_focus": ["DACH"],
        "thesis_points": ["AI infrastructure"],
        "deck_preferences": {
            "preferred_slide_count": 15,
            "must_include_slides": ["cover", "problem", "solution"],
        },
    }
    profile_path = tmp_path / "testvc.yaml"
    with open(profile_path, "w") as f:
        yaml.dump(data, f)
    return tmp_path


@pytest.fixture
def sample_slide():
    return SlideContent(
        slide_number=1,
        slide_type="cover",
        title="NeuraPlox",
        headline="The AI Control Plane for European SMEs",
        bullets=["EUR 2.3M revenue in year 1", "20 employees"],
        metrics=["EUR 2.3M revenue"],
        speaker_notes="Open with the vision statement.",
        transition_to_next="Let me show you the problem we solve.",
        vc_alignment_notes=["Aligns with European sovereignty thesis"],
    )


@pytest.fixture
def sample_deck(sample_slide):
    return PitchDeck(
        company_name="Neurawork",
        target_vc="Test VC",
        generated_at="2026-02-19T12:00:00",
        slides=[sample_slide],
        narrative_arc="Hook > Problem > Solution",
        gaps_identified=["NDR percentage missing"],
        gaps_filled={"revenue_eur": "2300000"},
    )
