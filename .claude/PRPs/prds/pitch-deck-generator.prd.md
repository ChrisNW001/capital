# Pitch Deck Generator & Validator for NeuraPlox / Earlybird

## Problem Statement

Technical founders pitching to VCs waste critical time guessing what investors want to hear, structuring narratives incorrectly, and missing key slides that drive investment decisions. For Christoph Knöll (Neurawork), the immediate problem is translating a deeply technical 7-layer AI architecture platform (NeuraPlox) and strong bootstrapped traction (EUR 2.3M revenue, ~20 employees, year 1) into a compelling investor narrative for Earlybird Capital — without VC pitch experience and under extreme time pressure.

## Evidence

- 86% of pitch decks reviewed by VCs are missing a simplified operating plan (TechCrunch 1,000+ deck review)
- VCs spend an average of 2 minutes 18 seconds on a deck — narrative structure determines whether they read further
- Technical founders systematically over-index on architecture slides and under-index on business proof and market narrative
- Earlybird uses an AI-powered deal sourcing platform (EagleEye) — they are data-driven investors who expect metrics-forward decks
- Founder confirms: "I simply do not know the game and what they want to hear"

## Proposed Solution

A reusable pitch deck generator and validator that takes structured company/product inputs, VC-specific research, and best practices to produce slide-by-slide content (titles, bullet points, speaker notes, narrative arc) scored against investor-specific criteria. The first use case is generating the NeuraPlox pitch deck for Earlybird Capital. The tool outputs content ready for visual rendering (e.g., via Imagen3 XML prompts).

## Key Hypothesis

We believe a structured pitch deck generator with VC-specific validation will produce investor-grade deck content that resonates with target VCs.
We'll know we're right when the generated deck leads to positive investor engagement (meeting requests, follow-up questions, term sheet discussions).

## What We're NOT Building

- Visual slide design/rendering (Imagen3 integration) — deferred to optional Phase 4
- Generic startup pitch tool for all industries — focused on B2B enterprise/AI companies pitching European VCs
- Investor CRM or fundraising pipeline management — out of scope entirely

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Deck completeness | All required slides generated with content | Checklist validation |
| VC criteria score | >80% on Earlybird-specific validation rubric | Built-in scoring engine |
| Time to generate deck | < 30 minutes from input to complete content | Runtime measurement |
| Investor resonance | Positive engagement from target VC | Post-pitch feedback |

## Open Questions

- [ ] What is the exact fundraising amount and use-of-funds allocation for the Earlybird pitch?
- [ ] Which customer names/logos can be disclosed in the deck?
- [ ] What is the current monthly burn rate and runway?
- [ ] What is the Net Dollar Retention (NDR) rate?
- [ ] Are there any existing investor relationships or warm intros to Earlybird (specifically Dr. Andre Retterath)?
- [ ] What is the exact ARR breakdown (recurring vs. services)?

---

## Users & Context

**Primary User**
- **Who**: Christoph Knöll, CEO/Co-founder of Neurawork GmbH & Co. KG — technical founder with PwC Senior Manager background, deep AI/enterprise expertise, limited VC pitch experience
- **Current behavior**: Manually assembling pitch content from ZIM application, architecture docs, and ad-hoc research; uncertain about narrative structure, slide order, and what metrics to highlight
- **Trigger**: Decision to raise external capital from Earlybird to scale NeuraPlox from validated prototype to market leadership — pitch needed within days
- **Success state**: Complete, validated slide-by-slide deck content with speaker notes, scored against Earlybird-specific criteria, ready for Imagen3 visual rendering

**Job to Be Done**
When I need to pitch my AI platform to a specific VC, I want to generate a complete, validated pitch deck that follows proven narrative structures and addresses what that specific investor cares about, so I can focus on telling my story confidently instead of guessing what belongs on each slide.

**Non-Users**
- Fortune 500 / large enterprise pitch teams with dedicated investor relations
- Consumer/B2C startups (different deck structure and metrics)
- Founders pitching friends & family or angel rounds (different depth required)

---

## Solution Detail

### Core Capabilities (MoSCoW)

| Priority | Capability | Rationale |
|----------|------------|-----------|
| Must | **Company Profile Ingestion** — accept structured inputs (company data, metrics, product description, team bios, market data) from files or interactive Q&A | Foundation for all content generation |
| Must | **VC Research Module** — ingest VC-specific data (thesis, portfolio, partners, preferences) to tailor narrative | Earlybird has specific thesis points (European sovereignty, deep tech, category creation) that must be reflected |
| Must | **Narrative Engine** — generate slide-by-slide content following proven deck structure (title, bullets, speaker notes, narrative transitions) | Core value: translating raw inputs into investor-ready narrative |
| Must | **Slide Validator** — score each slide and overall deck against VC-specific rubric (completeness, metrics presence, narrative flow, common mistakes) | Ensures deck quality before pitch; catches blind spots |
| Must | **Content Export** — output structured content (Markdown, JSON) that can feed into Imagen3 XML prompts or other rendering pipelines | Bridge to visual rendering step |
| Should | **Competitor Positioning Generator** — auto-generate 2-axis positioning matrix and competitive narrative from market research | Competitive slide is where technical founders commonly fail |
| Should | **Objection Anticipator** — generate likely investor objections with pre-built responses based on company profile | Prepares founder for Q&A, the most critical part of the pitch |
| Could | **Multi-VC Profiles** — support profiles for different VCs (Earlybird, HV Capital, Lakestar, etc.) with different thesis weighting | Reusability for future pitches |
| Could | **Deck Versioning** — track iterations and score improvements over revisions | Useful for iterating based on feedback |
| Won't | **Visual slide rendering** — generating actual PowerPoint/PDF slides with design | Deferred to optional Phase 4; Imagen3 handles this |
| Won't | **Live pitch coaching or teleprompter** — real-time presentation assistance | Out of scope |

### MVP Scope

Generate a complete, validated NeuraPlox pitch deck for Earlybird Capital:
- 15-18 slides of structured content (title, key points, supporting data, speaker notes)
- Earlybird-specific validation scoring
- Exportable format for Imagen3 rendering pipeline
- Objection/Q&A preparation document

### User Flow

```
1. INPUT PHASE
   ├── Load company data (from files: ZIM application, architecture docs, financials)
   ├── Load VC profile (Earlybird research, thesis, portfolio patterns)
   └── Answer gap-filling questions (fundraise amount, use of funds, specific metrics)

2. GENERATION PHASE
   ├── Determine optimal slide order based on company strengths + VC preferences
   ├── Generate slide-by-slide content with narrative transitions
   ├── Generate speaker notes per slide
   └── Generate Q&A preparation / objection handling

3. VALIDATION PHASE
   ├── Score each slide (0-100) against rubric dimensions
   ├── Flag missing elements, weak sections, common mistakes
   ├── Generate overall deck score with improvement recommendations
   └── Highlight Earlybird-specific alignment points

4. EXPORT PHASE
   ├── Output structured Markdown (human-readable)
   ├── Output JSON (machine-readable for Imagen3 pipeline)
   └── Output Q&A preparation document
```

---

## Technical Approach

**Feasibility**: HIGH

The tool is a structured content generation and validation pipeline. No novel AI research required — it combines:
- Document parsing (PDF/DOCX ingestion from existing company materials)
- Structured prompt engineering (slide-by-slide generation with constraints)
- Rule-based validation (rubric scoring against defined criteria)
- Template-driven export (Markdown + JSON output)

**Architecture Notes**
- Python-based CLI/script application (matches founder's tech stack)
- LLM-powered content generation (Claude API for narrative quality)
- Rule-based + LLM-hybrid validation (rubric checks + qualitative scoring)
- File-based I/O (reads company docs, outputs structured content)
- VC profile system stored as YAML/JSON configs for reusability

**Technical Risks**

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| LLM generates generic/fluffy pitch content | Medium | Constrain with specific company data, metrics, and Earlybird thesis points; validate against rubric |
| Narrative doesn't flow between slides | Low | Use explicit transition prompts and full-deck coherence pass |
| Validation scoring is too lenient | Medium | Calibrate rubric against known good/bad decks; include hard rules (e.g., "no metrics on traction slide = automatic fail") |
| Content too long for slide format | Medium | Enforce word/bullet limits per slide type |

---

## Implementation Phases

| # | Phase | Description | Status | Parallel | Depends | PRP Plan |
|---|-------|-------------|--------|----------|---------|----------|
| 1 | Core Engine | Company data ingestion, VC profile system, slide structure template, narrative generation engine | complete | - | - | `.claude/PRPs/plans/completed/pitch-deck-core-engine.plan.md` |
| 2 | Validation Engine | Rubric-based scoring, slide-level and deck-level validation, Earlybird-specific criteria, improvement recommendations | pending | - | 1 | - |
| 3 | Export & Q&A | Markdown and JSON export, speaker notes, Q&A/objection document generation, Imagen3-compatible output format | pending | with 2 | 1 | - |
| 4 | Visual Rendering (Optional) | Imagen3 API integration for XML-based slide design generation | pending | - | 3 | - |

### Phase Details

**Phase 1: Core Engine**
- **Goal**: Build the content generation pipeline — from raw company/VC inputs to complete slide-by-slide deck content
- **Scope**:
  - Document parser for PDF/DOCX company materials
  - VC profile schema and Earlybird profile
  - Slide structure template (15-18 slides with defined purposes)
  - LLM-powered narrative engine that generates per-slide content (title, bullets, data points, speaker notes, transitions)
  - Interactive gap-filler for missing data points
- **Success signal**: Given NeuraPlox inputs, generates a complete 15-18 slide deck content in Markdown

**Phase 2: Validation Engine**
- **Goal**: Score and validate generated deck against VC-specific criteria
- **Scope**:
  - Scoring rubric with dimensions: completeness, metrics density, narrative coherence, Earlybird thesis alignment, common mistake detection
  - Per-slide scoring (0-100) with specific feedback
  - Overall deck score with prioritized improvement list
  - Earlybird-specific checks (European sovereignty angle, category creation narrative, capital efficiency highlight, bottom-up TAM)
- **Success signal**: Validates a generated deck and produces actionable scores with specific improvement recommendations

**Phase 3: Export & Q&A**
- **Goal**: Produce final outputs ready for use
- **Scope**:
  - Markdown export (human-readable deck content)
  - JSON export (structured for Imagen3 XML pipeline)
  - Speaker notes document
  - Q&A preparation: top 10 likely Earlybird questions with suggested answers
  - Objection handling guide based on company profile gaps
- **Success signal**: Exported files that can directly feed into Imagen3 or be used as presentation preparation

**Phase 4: Visual Rendering (Optional)**
- **Goal**: Auto-generate slide visuals via Imagen3 API
- **Scope**:
  - XML prompt generation for each slide
  - Imagen3 API integration
  - Slide style/branding configuration
  - PDF/PPTX output
- **Success signal**: Visually polished slides generated from content output

### Parallelism Notes

Phases 2 and 3 can run in parallel after Phase 1, as validation logic and export formatting are independent concerns. Phase 4 is optional and fully decoupled.

---

## Decisions Log

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Content generation approach | LLM-powered with structured constraints | Template-only, manual writing | LLM produces higher quality narrative; constraints prevent generic output |
| Validation approach | Hybrid rule-based + LLM scoring | Pure rules, pure LLM | Rules catch hard requirements (missing metrics); LLM evaluates narrative quality |
| Export format | Markdown + JSON | PowerPoint direct, PDF | Markdown is human-readable; JSON feeds Imagen3 pipeline; avoids coupling to specific presentation tool |
| VC profile storage | YAML config files | Database, hardcoded | YAML is portable, version-controllable, and easy to add new VCs |
| Target VC for MVP | Earlybird Capital | Generic | Specific target produces better-validated output; generalizable later via profiles |
| Positioning narrative | "SAP of the new AI era for European SMEs" | "AI governance platform", "Enterprise AI infrastructure" | Founder's vision; resonates with Earlybird's category creation thesis |

---

## Research Summary

**Market Context**
- Earlybird Capital manages EUR 2.5B, invests Seed to Series A in Western Europe (DACH focus)
- Key contact: Dr. Andre Retterath (Enterprise Software + AI vertical lead)
- Earlybird thesis alignment: European AI sovereignty, deep tech, enterprise SaaS, category creation, capital-efficient growth
- Portfolio pattern: Aleph Alpha (AI sovereignty), Remberg (SME SaaS), HiveMQ (infrastructure), TopK (AI search infra)
- Comparable valuations at EUR 2.3M ARR: EUR 46-69M pre-money at 20-30x revenue multiple

**Company Context (NeuraPlox / Neurawork)**
- Neurawork GmbH & Co. KG, founded 2024, ~20 employees, bootstrapped
- EUR 2.3M revenue in first full business year
- NeuraPlox: 7-layer AI control plane architecture for Mittelstand (50-500 employees)
- ZIM funding application submitted (EUR 525K total, EUR 236K requested)
- 4 pilot customers validating architecture components (TRL 4 → TRL 7 target)
- Pricing: EUR 2,000-8,000/month managed service; 10x cheaper than enterprise alternatives
- Go-to-market: Land-and-expand via Plox ecosystem; partner channel via IT consultancies

**Pitch Deck Best Practices**
- 15-18 slides optimal for Series A send deck; 12 for live presentation
- Team slide early (credibility is foundational for enterprise AI)
- NDR is the #1 metric VCs scrutinize for AI SaaS
- Capital efficiency narrative is a superpower in 2024-2026 fundraising climate
- Category creation ("Enterprise AI Control Plane") resonates with Earlybird's investment pattern
- Bottom-up SOM calculation required (not top-down TAM)
- Must proactively address: AI commoditization risk, gross margin trajectory, customer concentration

**Earlybird-Specific Deck Requirements**
- European digital sovereignty angle (mirrors Aleph Alpha thesis)
- Data-driven metrics presentation (Andre Retterath is a data-driven VC)
- Category ownership narrative (UiPath/RPA, Remberg/XRM pattern)
- Capital efficiency as proof of founder quality
- Bottom-up market sizing with clear SOM methodology
- Named or anonymized customer evidence with quantified ROI

---

*Generated: 2026-02-19*
*Status: DRAFT - needs validation*
