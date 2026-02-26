# Pitchdeck

## What This Is

A CLI tool that generates, validates, and visually renders investor pitch decks for B2B AI/SaaS companies. Uses Claude for content generation and LLM-powered scoring, and Gemini/Imagen for 4K visual slide rendering. Targets founders preparing for VC pitches.

## Core Value

Generate investor-ready pitch decks with professional visual slides that match the target VC's thesis — from raw company documents to 4K presentation-quality output in one workflow.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- Content generation via Claude from company documents (PDF/DOCX)
- VC-specific deck tailoring using profile YAML configs
- 5-dimension validation scoring (completeness, metrics_density, narrative_coherence, thesis_alignment, common_mistakes)
- Gap detection and interactive filling for missing company data
- Markdown output for generated decks and validation reports
- 15-slide template structure covering standard investor deck narrative arc

### Active

<!-- Current scope. Building toward these. -->

- [ ] Visual slide generation using Gemini/Imagen 4K pipeline
- [ ] `pitchdeck design` CLI command (takes deck JSON, outputs visual slides)
- [ ] 3 XML design systems (Consulting Light, Training Dark, Brochure A4)
- [ ] Neurawork corporate design format transformation
- [ ] ZIP and PDF export of generated slides
- [ ] GEMINI_API_KEY support via .env

### Out of Scope

- Logo/watermark overlay — deferred to future milestone
- Custom user-provided XML design systems — future
- Real-time web UI (NW Slide AI is a React app; this stays CLI)
- Video/animation generation
- OAuth or Google AI Studio integration

## Context

- Existing codebase: Python CLI (Typer + Rich), Pydantic models, Claude API via anthropic SDK
- Reference implementation: NW Slide AI (React/Vite app) uses 2-step pipeline: Gemini Pro for XML prompt elaboration → Imagen 4 for 4K image generation
- 3 XML design systems exist (~1000 lines each) defining typography, colors, layout grids, glassmorphism effects, slide type templates
- Neurawork brand: white background (#FFFFFF), Sky Blue (#15B5E0), Deep Purple (#594297), Soft Pink (#F584D3), Inter typography
- The neurawork-folien skill defines a #Folie[Nr] format with visible content + design metadata in {{ }} blocks

## Constraints

- **Tech stack**: Python CLI only — no Node.js/React runtime; Gemini SDK must be Python (`google-genai`)
- **API keys**: Both ANTHROPIC_API_KEY and GEMINI_API_KEY via .env (python-dotenv)
- **Dependencies**: Minimize new deps — google-genai, Pillow (for image handling), reportlab or similar for PDF
- **Models**: Use latest stable Gemini models for elaboration + Imagen 4 for image generation
- **Design systems**: Port NW Slide AI's 3 XML design systems to Python-loadable format
- **Output**: 4K (3840x2160) slide images for 16:9, 3072x4096 for A4 brochure

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Separate `design` command (not extend `generate`) | Keep concerns separated — content vs visual rendering are distinct pipelines | — Pending |
| Google Gemini/Imagen for visual rendering | Proven pipeline from NW Slide AI; Claude doesn't do image generation | — Pending |
| Port all 3 design systems | Maximum flexibility for different presentation contexts | — Pending |
| No logo overlay in v1 | Keep scope focused on core slide generation first | — Pending |
| ZIP + PDF export | Matches NW Slide AI capabilities; covers both individual and assembled formats | — Pending |

---
*Last updated: 2026-02-26 after milestone v1.1 initialization*
