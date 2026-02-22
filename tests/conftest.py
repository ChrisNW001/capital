"""Shared test fixtures for pitch deck generator."""

import pytest
from ruamel.yaml import YAML

from pitchdeck.models import (
    CompanyProfile,
    CustomCheckResult,
    DeckPreferences,
    DeckValidationResult,
    DimensionScore,
    PitchDeck,
    SlideContent,
    SlideValidationScore,
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


@pytest.fixture
def sample_multi_slide_deck():
    """A realistic 15-slide deck for validation testing."""
    slides = []
    slide_types = [
        "cover", "executive-summary", "problem", "why-now",
        "solution", "product", "market-sizing", "business-model",
        "traction", "go-to-market", "competitive-landscape",
        "team", "financials", "the-ask", "ai-architecture",
    ]
    for i, stype in enumerate(slide_types, 1):
        slides.append(
            SlideContent(
                slide_number=i,
                slide_type=stype,
                title=f"Slide {i} Title",
                headline=f"Key insight for {stype}",
                bullets=[
                    f"Point {j} for {stype}"
                    for j in range(1, 4)
                ],
                metrics=[f"Metric for {stype}"]
                if stype
                in (
                    "executive-summary",
                    "traction",
                    "business-model",
                    "market-sizing",
                    "financials",
                )
                else [],
                speaker_notes=f"Say this about {stype}.",
                transition_to_next=f"Moving to next topic..."
                if i < 15
                else "",
                vc_alignment_notes=[
                    f"Aligns with thesis point for {stype}"
                ],
            )
        )
    return PitchDeck(
        company_name="Neurawork",
        target_vc="Test VC",
        generated_at="2026-02-19T12:00:00",
        slides=slides,
        narrative_arc="Hook > Tension > Resolution > Proof > Trust > Ask",
        gaps_identified=["NDR percentage missing"],
    )


@pytest.fixture
def sample_validation_result():
    """A sample DeckValidationResult for report rendering tests."""
    return DeckValidationResult(
        deck_name="Neurawork",
        target_vc="Test VC",
        validated_at="2026-02-19T12:00:00",
        overall_score=73,
        pass_threshold=60,
        dimension_scores=[
            DimensionScore(
                dimension="completeness",
                score=80,
                weight=0.25,
                rationale="15/15 slides present, 14 with speaker notes",
                evidence_found=["15/15 slides", "Speaker notes present"],
                evidence_missing=["1 slide missing notes"],
            ),
            DimensionScore(
                dimension="metrics_density",
                score=65,
                weight=0.20,
                rationale="12 metrics found, 20 expected",
                evidence_found=["ARR present", "Customer count present"],
                evidence_missing=["NDR missing", "Burn multiple missing"],
            ),
            DimensionScore(
                dimension="narrative_coherence",
                score=75,
                weight=0.20,
                rationale="Good flow with minor transition gaps",
            ),
            DimensionScore(
                dimension="thesis_alignment",
                score=70,
                weight=0.20,
                rationale="5/7 thesis points addressed",
            ),
            DimensionScore(
                dimension="common_mistakes",
                score=80,
                weight=0.15,
                rationale="No major mistakes detected",
            ),
        ],
        slide_scores=[
            SlideValidationScore(
                slide_number=1,
                slide_type="cover",
                score=90,
            ),
            SlideValidationScore(
                slide_number=9,
                slide_type="traction",
                score=55,
                issues=["Missing NDR metric"],
                suggestions=["Add NDR or explain unavailability"],
            ),
        ],
        custom_check_results=[
            CustomCheckResult(
                check="European sovereignty angle must be present",
                passed=True,
                evidence="Keywords found: sovereign, european",
            ),
            CustomCheckResult(
                check="Bottom-up market sizing required",
                passed=False,
                evidence="",
            ),
        ],
        top_strengths=[
            "Strong revenue traction for stage",
            "Clear AI infrastructure positioning",
        ],
        critical_gaps=[
            "No NDR data",
            "Bottom-up market sizing missing",
        ],
        improvement_priorities=[
            "Address VC requirement: Bottom-up market sizing required",
            "No NDR data",
            "Fix slide 9 (traction): Missing NDR metric",
        ],
        recommendation="Strong candidate with fixable gaps. Add NDR and bottom-up SOM.",
    )


@pytest.fixture
def sample_deck_json(sample_multi_slide_deck, tmp_path):
    """Write a multi-slide deck as JSON to a temp file."""
    json_path = tmp_path / "deck.json"
    with open(json_path, "w") as f:
        f.write(sample_multi_slide_deck.model_dump_json(indent=2))
    return json_path
