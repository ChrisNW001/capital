"""Gap detection and interactive filling for missing company data."""

from typing import List

import questionary

from pitchdeck.models import CompanyProfile, GapQuestion, SlideTemplate

GAP_DEFINITIONS: list[GapQuestion] = [
    GapQuestion(
        field="name",
        question="Company name?",
        importance="critical",
    ),
    GapQuestion(
        field="product_name",
        question="Product name?",
        importance="critical",
    ),
    GapQuestion(
        field="one_liner",
        question="One-liner description (e.g., 'The AI Control Plane for European SMEs')?",
        importance="critical",
    ),
    GapQuestion(
        field="target_raise_eur",
        question="Target fundraise amount (EUR)?",
        importance="critical",
    ),
    GapQuestion(
        field="growth_rate_yoy",
        question="Year-over-year revenue growth rate (%)?",
        importance="critical",
    ),
    GapQuestion(
        field="ndr_percent",
        question="Net Dollar Retention (NDR) percentage?",
        importance="critical",
    ),
    GapQuestion(
        field="gross_margin_percent",
        question="Gross margin percentage?",
        importance="important",
    ),
    GapQuestion(
        field="burn_rate_monthly_eur",
        question="Monthly burn rate (EUR)?",
        importance="important",
    ),
    GapQuestion(
        field="customer_count",
        question="Number of paying customers?",
        importance="important",
    ),
    GapQuestion(
        field="funding_stage",
        question="Current funding stage?",
        importance="important",
        choices=["bootstrapped", "pre-seed", "seed", "series-a"],
    ),
]


def detect_gaps(
    profile: CompanyProfile, templates: List[SlideTemplate]
) -> list[GapQuestion]:
    """Identify missing data points needed for slide generation."""
    gaps = []
    for gap_def in GAP_DEFINITIONS:
        value = getattr(profile, gap_def.field, None)
        if value is None or value == "" or value == 0:
            gaps.append(gap_def)
    return gaps


def fill_gaps_interactive(
    profile: CompanyProfile, gaps: list[GapQuestion]
) -> CompanyProfile:
    """Prompt user to fill missing data points."""
    updates: dict = {}
    for gap in gaps:
        label = (
            f"[{gap.importance.upper()}]"
            if gap.importance == "critical"
            else f"[{gap.importance}]"
        )
        try:
            if gap.choices:
                answer = questionary.select(
                    f"{label} {gap.question}",
                    choices=gap.choices + ["Skip"],
                ).ask()
            else:
                answer = questionary.text(
                    f"{label} {gap.question}",
                    default=gap.default or "",
                ).ask()
        except KeyboardInterrupt:
            break
        if answer and answer != "Skip":
            updates[gap.field] = _coerce_value(gap.field, answer)
    return profile.model_copy(update=updates)


def _coerce_value(field: str, value: str):
    """Coerce string input to the appropriate type."""
    numeric_fields = {
        "target_raise_eur",
        "ndr_percent",
        "gross_margin_percent",
        "burn_rate_monthly_eur",
        "growth_rate_yoy",
        "revenue_eur",
    }
    if field in numeric_fields:
        try:
            return float(value.replace(",", "").replace("EUR", "").strip())
        except ValueError:
            return value
    int_fields = {"customer_count", "employee_count", "founded_year"}
    if field in int_fields:
        try:
            return int(value.replace(",", "").strip())
        except ValueError:
            return value
    return value
