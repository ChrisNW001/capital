"""Slide structure templates defining the 15-slide deck format."""

from pitchdeck.models import SlideTemplate, VCProfile

SLIDE_TEMPLATES: list[SlideTemplate] = [
    SlideTemplate(
        slide_type="cover",
        purpose="10-second filter — company name, one-liner, stage, contact",
        required_elements=["company_name", "product_name", "one_liner", "funding_stage"],
        metrics_needed=[],
        max_bullets=0,
        word_limit=30,
    ),
    SlideTemplate(
        slide_type="executive-summary",
        purpose="Value prop, competitive edge, flagship results in 30 seconds",
        required_elements=["value_proposition", "key_metric_1", "key_metric_2", "competitive_edge"],
        metrics_needed=["revenue", "growth_rate", "customer_count"],
        max_bullets=4,
        word_limit=100,
    ),
    SlideTemplate(
        slide_type="problem",
        purpose="Systemic pain with market data — not anecdotes",
        required_elements=["problem_statement", "market_evidence", "cost_of_problem", "who_feels_it"],
        metrics_needed=["market_data_citation"],
        max_bullets=4,
        word_limit=120,
    ),
    SlideTemplate(
        slide_type="why-now",
        purpose="Macro tailwind making this the right moment",
        required_elements=["timing_catalyst", "market_shift", "technology_enabler"],
        optional_elements=["regulatory_driver"],
        metrics_needed=[],
        max_bullets=4,
        word_limit=120,
    ),
    SlideTemplate(
        slide_type="solution",
        purpose="Product type, end user, vertical, quantified impact",
        required_elements=["product_description", "target_user", "key_benefit", "quantified_impact"],
        metrics_needed=["roi_metric"],
        max_bullets=5,
        word_limit=150,
    ),
    SlideTemplate(
        slide_type="product",
        purpose="Architecture overview, key capabilities, differentiation",
        required_elements=["architecture_overview", "key_capabilities", "technical_moat"],
        optional_elements=["demo_description", "screenshot_placeholder"],
        metrics_needed=[],
        max_bullets=5,
        word_limit=150,
    ),
    SlideTemplate(
        slide_type="market-sizing",
        purpose="TAM/SAM/SOM with bottom-up methodology",
        required_elements=["tam", "sam", "som", "methodology_explanation"],
        metrics_needed=["tam_eur", "sam_eur", "som_eur", "icp_count", "arpu"],
        max_bullets=4,
        word_limit=120,
    ),
    SlideTemplate(
        slide_type="business-model",
        purpose="Pricing model, unit economics, gross margin",
        required_elements=["pricing_model", "price_range", "unit_economics_summary"],
        metrics_needed=["acv", "gross_margin", "ltv", "cac", "payback_period"],
        max_bullets=5,
        word_limit=130,
    ),
    SlideTemplate(
        slide_type="traction",
        purpose="Growth proof — most scrutinized slide by VCs",
        required_elements=["revenue_metric", "growth_trajectory", "customer_evidence"],
        metrics_needed=["arr_or_revenue", "yoy_growth", "customer_count", "ndr", "logo_names_or_anonymized"],
        max_bullets=5,
        word_limit=130,
    ),
    SlideTemplate(
        slide_type="go-to-market",
        purpose="ICP, sales motion, channels, partnerships",
        required_elements=["icp_definition", "sales_motion", "channel_strategy"],
        optional_elements=["partnership_strategy", "expansion_playbook"],
        metrics_needed=["cac", "sales_cycle_days"],
        max_bullets=5,
        word_limit=130,
    ),
    SlideTemplate(
        slide_type="competitive-landscape",
        purpose="2-axis positioning matrix with differentiated axes",
        required_elements=["positioning_matrix_description", "key_differentiators", "competitive_moat"],
        optional_elements=["win_rate"],
        metrics_needed=[],
        max_bullets=4,
        word_limit=120,
    ),
    SlideTemplate(
        slide_type="team",
        purpose="Domain expertise, key hires, credibility foundation",
        required_elements=["founders_with_credentials", "key_hires", "domain_expertise_proof"],
        optional_elements=["advisors", "board_members"],
        metrics_needed=["years_domain_experience"],
        max_bullets=5,
        word_limit=150,
    ),
    SlideTemplate(
        slide_type="financials",
        purpose="Revenue trajectory, burn rate, runway",
        required_elements=["revenue_trajectory", "cost_structure", "path_to_profitability"],
        metrics_needed=["current_mrr", "burn_rate", "runway_months", "burn_multiple"],
        max_bullets=4,
        word_limit=120,
    ),
    SlideTemplate(
        slide_type="the-ask",
        purpose="Amount, use of funds, milestones to next round",
        required_elements=["raise_amount", "use_of_funds_breakdown", "key_milestones_18_months"],
        metrics_needed=["raise_amount_eur", "target_arr_18_months"],
        max_bullets=5,
        word_limit=130,
    ),
    SlideTemplate(
        slide_type="ai-architecture",
        purpose="Technical depth for AI-specific investors — moat and defensibility",
        required_elements=["architecture_layers", "data_moat", "ai_approach"],
        optional_elements=["performance_benchmarks", "ip_description"],
        metrics_needed=[],
        max_bullets=5,
        word_limit=150,
    ),
]


def get_slide_templates(vc_profile: VCProfile) -> list[SlideTemplate]:
    """Return slide templates filtered and ordered by VC preferences."""
    must_include = set(vc_profile.deck_preferences.must_include_slides)
    if not must_include:
        return list(SLIDE_TEMPLATES)
    return [t for t in SLIDE_TEMPLATES if t.slide_type in must_include]


def get_narrative_arc() -> str:
    """Return the narrative psychology arc description for the prompt."""
    return (
        "Follow the 6-stage investor psychology arc:\n"
        "1. HOOK (Cover + Exec Summary): Instant credibility — name, traction proof, one-liner\n"
        "2. TENSION (Problem + Why Now): Create urgency — the pain is real, the timing is now\n"
        "3. RESOLUTION (Solution + Product): Release tension — here's how we solve it\n"
        "4. PROOF (Market + Traction + Business Model): Validate the resolution — the market is big, we're winning\n"
        "5. TRUST (Team + Competitive + Go-to-Market): Build confidence — we can execute\n"
        "6. CALL TO ACTION (Financials + The Ask + AI Architecture): Close — here's what we need and why it's worth it"
    )
