"""Tests for Markdown output rendering."""

import pytest

from pitchdeck.models import PitchDeck, SlideContent
from pitchdeck.output.markdown import render_markdown, save_markdown


class TestRenderMarkdown:
    def test_renders_header(self, sample_deck):
        md = render_markdown(sample_deck)
        assert "# Neurawork — Pitch Deck" in md
        assert "**Target**: Test VC" in md
        assert "**Generated**: 2026-02-19" in md

    def test_renders_narrative_arc(self, sample_deck):
        md = render_markdown(sample_deck)
        assert "## Narrative Arc" in md
        assert "Hook > Problem > Solution" in md

    def test_renders_slide(self, sample_deck):
        md = render_markdown(sample_deck)
        assert "## Slide 1: NeuraPlox" in md
        assert "*Type: cover*" in md
        assert "**The AI Control Plane for European SMEs**" in md

    def test_renders_bullets(self, sample_deck):
        md = render_markdown(sample_deck)
        assert "- EUR 2.3M revenue in year 1" in md
        assert "- 20 employees" in md

    def test_renders_metrics(self, sample_deck):
        md = render_markdown(sample_deck)
        assert "**Key Metrics:**" in md
        assert "- EUR 2.3M revenue" in md

    def test_renders_speaker_notes_in_details(self, sample_deck):
        md = render_markdown(sample_deck)
        assert "<details>" in md
        assert "<summary>Speaker Notes</summary>" in md
        assert "Open with the vision statement." in md
        assert "</details>" in md

    def test_renders_vc_alignment(self, sample_deck):
        md = render_markdown(sample_deck)
        assert "> **VC Alignment**:" in md
        assert "European sovereignty thesis" in md

    def test_renders_transition(self, sample_deck):
        md = render_markdown(sample_deck)
        assert "*Transition: Let me show you the problem we solve.*" in md

    def test_renders_gaps_section(self, sample_deck):
        md = render_markdown(sample_deck)
        assert "## Information Gaps" in md
        assert "- [ ] NDR percentage missing" in md

    def test_no_gaps_section_when_empty(self, sample_slide):
        deck = PitchDeck(
            company_name="Test",
            target_vc="VC",
            generated_at="2026-01-01",
            slides=[sample_slide],
            narrative_arc="Arc",
            gaps_identified=[],
        )
        md = render_markdown(deck)
        assert "## Information Gaps" not in md

    def test_renders_multiple_slides(self, sample_slide):
        slide2 = SlideContent(
            slide_number=2,
            slide_type="problem",
            title="The Problem",
            headline="SMEs are stuck",
            bullets=["Point A", "Point B"],
            speaker_notes="Explain the pain.",
        )
        deck = PitchDeck(
            company_name="Test",
            target_vc="VC",
            generated_at="2026-01-01",
            slides=[sample_slide, slide2],
            narrative_arc="Arc",
        )
        md = render_markdown(deck)
        assert "## Slide 1:" in md
        assert "## Slide 2:" in md
        assert "The Problem" in md

    def test_slide_without_optional_fields(self):
        slide = SlideContent(
            slide_number=1,
            slide_type="cover",
            title="Test",
            headline="Headline",
            bullets=[],
            speaker_notes="",
        )
        deck = PitchDeck(
            company_name="Test",
            target_vc="VC",
            generated_at="2026-01-01",
            slides=[slide],
            narrative_arc="Arc",
        )
        md = render_markdown(deck)
        assert "**Key Metrics:**" not in md
        assert "<details>" not in md
        assert "> **VC Alignment**" not in md


class TestSaveMarkdown:
    def test_saves_to_file(self, sample_deck, tmp_path):
        output_path = str(tmp_path / "test_deck.md")
        save_markdown(sample_deck, output_path)

        with open(output_path) as f:
            content = f.read()
        assert "# Neurawork — Pitch Deck" in content

    def test_overwrites_existing_file(self, sample_deck, tmp_path):
        output_path = str(tmp_path / "test_deck.md")
        with open(output_path, "w") as f:
            f.write("old content")

        save_markdown(sample_deck, output_path)

        with open(output_path) as f:
            content = f.read()
        assert "old content" not in content
        assert "Neurawork" in content
