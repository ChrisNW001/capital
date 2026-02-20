"""Tests for validation report rendering."""

from pitchdeck.models import (
    CustomCheckResult,
    DeckValidationResult,
    DimensionScore,
    SlideValidationScore,
)
from pitchdeck.output.validation_report import (
    render_validation_report,
    save_validation_report,
)


class TestRenderValidationReport:
    def test_renders_header(self, sample_validation_result):
        md = render_validation_report(sample_validation_result)
        assert "# Deck Validation Report" in md
        assert "**Deck**: Neurawork" in md
        assert "**Target VC**: Test VC" in md
        assert "**Overall Score**: 73/100" in md
        assert "**PASS**" in md

    def test_renders_score_breakdown_table(
        self, sample_validation_result
    ):
        md = render_validation_report(sample_validation_result)
        assert "## Score Breakdown" in md
        assert "| Dimension |" in md
        assert "Completeness" in md
        assert "Metrics Density" in md
        assert "**TOTAL**" in md

    def test_renders_dimension_details(
        self, sample_validation_result
    ):
        md = render_validation_report(sample_validation_result)
        assert "### Completeness" in md
        assert "**Score**: 80/100" in md
        assert "**Evidence Found:**" in md
        assert "**Evidence Missing:**" in md

    def test_renders_custom_checks_table(
        self, sample_validation_result
    ):
        md = render_validation_report(sample_validation_result)
        assert "## VC-Specific Checks" in md
        assert "| Check | Status | Evidence |" in md
        assert "PASS" in md
        assert "FAIL" in md

    def test_renders_per_slide_scores(
        self, sample_validation_result
    ):
        md = render_validation_report(sample_validation_result)
        assert "## Per-Slide Scores" in md
        assert "### Slide 1:" in md
        assert "### Slide 9:" in md
        assert "Missing NDR metric" in md

    def test_renders_strengths_and_gaps(
        self, sample_validation_result
    ):
        md = render_validation_report(sample_validation_result)
        assert "## Top Strengths" in md
        assert "## Critical Gaps" in md
        assert "Strong revenue traction" in md
        assert "NDR data" in md

    def test_renders_improvement_priorities(
        self, sample_validation_result
    ):
        md = render_validation_report(sample_validation_result)
        assert "## Improvement Priorities" in md
        assert "Bottom-up market sizing" in md

    def test_renders_recommendation(
        self, sample_validation_result
    ):
        md = render_validation_report(sample_validation_result)
        assert "## Recommendation" in md
        assert "Strong candidate" in md

    def test_fail_result_shows_fail(self):
        result = DeckValidationResult(
            deck_name="Test",
            target_vc="VC",
            validated_at="2026-01-01",
            overall_score=40,
            pass_threshold=60,
            pass_fail=False,
            dimension_scores=[],
            slide_scores=[],
            custom_check_results=[],
            top_strengths=[],
            critical_gaps=[],
            improvement_priorities=[],
            recommendation="Needs work.",
        )
        md = render_validation_report(result)
        assert "**FAIL**" in md

    def test_empty_sections_omitted(self):
        result = DeckValidationResult(
            deck_name="Test",
            target_vc="VC",
            validated_at="2026-01-01",
            overall_score=50,
            pass_threshold=60,
            pass_fail=False,
            dimension_scores=[],
            slide_scores=[],
            custom_check_results=[],
            top_strengths=[],
            critical_gaps=[],
            improvement_priorities=[],
            recommendation="",
        )
        md = render_validation_report(result)
        assert "## Top Strengths" not in md
        assert "## Recommendation" not in md


class TestSaveValidationReport:
    def test_saves_to_file(
        self, sample_validation_result, tmp_path
    ):
        output_path = str(tmp_path / "report.md")
        save_validation_report(sample_validation_result, output_path)

        with open(output_path) as f:
            content = f.read()
        assert "# Deck Validation Report" in content
        assert "Neurawork" in content

    def test_overwrites_existing_file(
        self, sample_validation_result, tmp_path
    ):
        output_path = str(tmp_path / "report.md")
        with open(output_path, "w") as f:
            f.write("old content")

        save_validation_report(sample_validation_result, output_path)

        with open(output_path) as f:
            content = f.read()
        assert "old content" not in content
        assert "Deck Validation Report" in content
