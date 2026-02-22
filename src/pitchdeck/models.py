"""Pydantic data models for the pitch deck generator."""

from typing import List, Optional

from pydantic import BaseModel, Field, computed_field


class PitchDeckError(Exception):
    """Base exception for pitch deck generator."""

    pass


class DocumentParseError(PitchDeckError):
    """Raised when document parsing fails."""

    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Failed to parse {path}: {reason}")


class ProfileNotFoundError(PitchDeckError):
    """Raised when VC profile YAML not found."""

    pass


class TeamMember(BaseModel):
    name: str
    role: str
    background: str


class CompanyProfile(BaseModel):
    name: str
    product_name: str
    one_liner: str
    founded_year: int
    employee_count: int
    revenue_eur: float
    revenue_type: str  # "ARR", "revenue", "GMV"
    growth_rate_yoy: Optional[float] = None
    customer_count: Optional[int] = None
    key_customers: List[str] = Field(default_factory=list)
    funding_stage: str  # "bootstrapped", "seed", "series-a"
    funding_raised_eur: float = 0
    target_raise_eur: Optional[float] = None
    use_of_funds: List[str] = Field(default_factory=list)
    team_highlights: List[TeamMember] = Field(default_factory=list)
    product_description: str = ""
    technology_description: str = ""
    market_description: str = ""
    competitors: List[str] = Field(default_factory=list)
    differentiators: List[str] = Field(default_factory=list)
    ndr_percent: Optional[float] = None
    gross_margin_percent: Optional[float] = None
    burn_rate_monthly_eur: Optional[float] = None
    raw_document_text: str = ""


class VCPartner(BaseModel):
    name: str
    focus: str
    background: str = ""


class DeckPreferences(BaseModel):
    preferred_slide_count: int = 15
    must_include_slides: List[str] = Field(default_factory=list)
    metrics_emphasis: List[str] = Field(default_factory=list)
    narrative_style: str = "data-driven"
    market_sizing_approach: str = "bottom-up"


class VCProfile(BaseModel):
    name: str
    fund_name: str
    aum_eur: Optional[float] = None
    stage_focus: List[str]
    sector_focus: List[str]
    geo_focus: List[str]
    thesis_points: List[str]
    portfolio_companies: List[str] = Field(default_factory=list)
    key_partners: List[VCPartner] = Field(default_factory=list)
    deck_preferences: DeckPreferences = Field(default_factory=DeckPreferences)
    custom_checks: List[str] = Field(default_factory=list)


class SlideTemplate(BaseModel):
    slide_type: str
    purpose: str
    required_elements: List[str]
    optional_elements: List[str] = Field(default_factory=list)
    metrics_needed: List[str] = Field(default_factory=list)
    max_bullets: int = 5
    word_limit: int = 150


class SlideContent(BaseModel):
    slide_number: int
    slide_type: str
    title: str
    headline: str
    bullets: List[str]
    metrics: List[str] = Field(default_factory=list)
    speaker_notes: str
    transition_to_next: str = ""
    vc_alignment_notes: List[str] = Field(default_factory=list)


class PitchDeck(BaseModel):
    company_name: str
    target_vc: str
    generated_at: str
    slides: List[SlideContent]
    narrative_arc: str
    gaps_identified: List[str] = Field(default_factory=list)
    gaps_filled: dict[str, str] = Field(default_factory=dict)


class GapQuestion(BaseModel):
    field: str
    question: str
    importance: str  # "critical", "important", "nice-to-have"
    default: Optional[str] = None
    choices: List[str] = Field(default_factory=list)


class DimensionScore(BaseModel):
    dimension: str  # "completeness", "metrics_density", "narrative_coherence", "thesis_alignment", "common_mistakes"
    score: int = Field(ge=0, le=100)
    weight: float = Field(ge=0.0, le=1.0)
    rationale: str
    evidence_found: List[str] = Field(default_factory=list)
    evidence_missing: List[str] = Field(default_factory=list)


class SlideValidationScore(BaseModel):
    slide_number: int
    slide_type: str
    score: int = Field(ge=0, le=100)
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class CustomCheckResult(BaseModel):
    check: str  # the original custom_check string from VCProfile
    passed: bool
    evidence: str = ""


class DeckValidationResult(BaseModel):
    deck_name: str
    target_vc: str
    validated_at: str
    overall_score: int = Field(ge=0, le=100)
    pass_threshold: int = Field(default=60, ge=0, le=100)
    dimension_scores: List[DimensionScore]
    slide_scores: List[SlideValidationScore]
    custom_check_results: List[CustomCheckResult]
    top_strengths: List[str]
    critical_gaps: List[str]
    improvement_priorities: List[str]  # ordered by impact
    recommendation: str

    @computed_field
    @property
    def pass_fail(self) -> bool:
        return self.overall_score >= self.pass_threshold
