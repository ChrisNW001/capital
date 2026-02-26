# Deck v7 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate a NeuraPlox v7 pitch deck scoring >= 90/100 against Earlybird profile, following the approved v7 design.

**Architecture:** Create a narrative brief DOCX encoding all v7 design decisions, feed it alongside source documents to `pitchdeck generate`, validate against Earlybird, iterate until target score.

**Tech Stack:** pitchdeck CLI (generate + validate), python-docx (for narrative brief), Earlybird profile

---

## Critical Constraint: Slide Type Mapping

The validator checks that all 15 `must_include_slides` from `profiles/earlybird.yaml` are present as `slide_type` values. The v7 design narrative MUST map to these exact types:

| v7 Slide | slide_type | Why This Mapping |
|---|---|---|
| 1. Cover | `cover` | Direct match |
| 2. Problem | `problem` | Direct match |
| 3. Vision: SAP for AI Era | `executive-summary` | Value prop + competitive edge = SAP vision |
| 4. Platform: N+M Architecture | `solution` | Product + quantified impact |
| 5. Governance: Production Unlock | `product` | Architecture + capabilities + moat |
| 6. Showcase Agents | `why-now` | Agents = market shift proving timing is now |
| 7. Prism: Ops-as-Service | `competitive-landscape` | Positioning vs. traditional consulting |
| 8. Traction & Validation | `traction` | Direct match |
| 9. Business Model: Three Horizons | `business-model` | Direct match |
| 10. Market: Agent OS Category | `market-sizing` | Direct match |
| 11. GTM: Land, Expand, Open | `go-to-market` | Direct match |
| 12. Growth: Ecosystem Flywheel | `financials` | Revenue trajectory + growth mechanics |
| 13. Team | `team` | Direct match |
| 14. The Ask | `the-ask` | Direct match |
| 15. Closing: Open AI OS | `ai-architecture` | Sovereignty + vision as technical moat |

## Validator Scoring (target breakdown for >= 90)

| Dimension | Weight | v6 Score | v7 Target | Strategy |
|---|---|---|---|---|
| Completeness | 25% | 100 | 100 | All 15 types, all speaker notes, keep gaps minimal |
| Metrics Density | 20% | 100 | 95+ | Hit all 8 Earlybird emphasis metrics, include NDR proxy |
| Narrative Coherence | 20% | 72 | 85+ | Word limits respected, strong arc, no architecture-at-end |
| Thesis Alignment | 20% | 74 | 85+ | All 7 thesis points with primary + secondary slides |
| Common Mistakes | 15% | 63 | 80+ | Fix all 8 common mistakes from validator checklist |

---

### Task 1: Extract Key Data Points from Antrag v9

**Files:**
- Read: `INPUT/Antrag_v9.pdf` (47 pages)
- Create: `docs/plans/v7-data-points.md` (temporary reference)

**Step 1: Extract financial data**

Read Antrag v9 and extract:
- Exact consulting revenue figures (current and projected)
- Team composition (all 15 members with roles)
- ZIM grant details (exact amount, timeline, scope)
- Market data citations (all third-party sources)
- Customer/project details (sectors, outcomes, anonymized if needed)
- Raise amount (derive specific figure from financial model)
- Burn rate / runway data

**Step 2: Extract product/technical data**

From Antrag v9 and ZIM docs, extract:
- N+M architecture specifics (concrete connector/agent numbers)
- Governance capabilities (specific compliance certifications)
- Agent descriptions (what Market/Marketing/Vertriebs Intelligence do)
- Prism Agent Flow specifics
- International expansion plans (if any in the document)

**Step 3: Save extracted data**

Write to `docs/plans/v7-data-points.md` as structured reference.

**Step 4: Commit**

```bash
git add docs/plans/v7-data-points.md
git commit -m "docs: extract Antrag v9 data points for deck v7"
```

---

### Task 2: Write v7 Narrative Brief DOCX

**Files:**
- Create: `INPUT/neuraplox_v7_narrative_brief.docx`

**Purpose:** This DOCX is the primary input to `pitchdeck generate`. It explicitly tells Claude what each slide should contain, overriding default narrative patterns.

**Step 1: Create the DOCX**

Use python-docx to create a DOCX with this structure:

```
NEURAPLOX DECK v7 — NARRATIVE DESIGN BRIEF
===========================================

CRITICAL: This document is the primary design guide for deck generation.
Follow this slide-by-slide design. Use data from the accompanying documents
(Antrag_v9.pdf, ZIM archive) for specific figures.

CORE NARRATIVE
--------------
One-liner: "NeuraPlox is the AI Operating System for enterprises —
where agents auto-create their own IT interfaces and governance makes
it production-safe. SAP for the AI era."

Three repeating messages:
1. "Agents need an OS, not more tools"
2. "Governance is the unlock"
3. "Consulting is the lab, Platform is the product, Marketplace is the multiplier"

SLIDE DESIGN (15 slides)
-------------------------

SLIDE 1 (cover): "NeuraPlox — The AI Operating System for Enterprises"
- Subtitle: "Where agents build their own interfaces. Governance-safe by design."
- Company: Neurawork GmbH & Co. KG | Founded 2024 | 15 employees
- Stage: Pre-Seed / Seed (seeking first institutional round)
- Contact: Christoph Knöll

SLIDE 2 (problem): "Enterprise AI is Stuck Between PoC and Production"
- Pain 1: Every agent project = custom integration hell
- Pain 2: No governance = no compliance = no deployment
- Pain 3: Point solutions = vendor lock-in ("Süßes Gift" trap)
- Data: [cite market stats from Antrag v9 on failed AI projects]
- Earlybird hooks: European digital sovereignty (US lock-in), AI as infrastructure (PoC graveyard)

SLIDE 3 (executive-summary): "SAP for the AI Era"
- Value prop: One OS where any agent connects to any system — automatically
- SAP analogy: SAP unified operations → NeuraPlox unifies AI agents
- Visual concept: before (spaghetti) vs. after (OS layer with agents)
- Introduce N+M: N agents × M systems, agents auto-create connectors
- Earlybird hooks: Category creation, Deep tech with commercialization

SLIDE 4 (solution): "N Agents × M Systems — Without N×M Integrations"
- How: Agents declare intent → platform resolves connectors → governance gates execution
- Moat: Every new agent makes connectors more valuable, every new connector makes agents more capable
- Functional description — what it DOES, not how it's built
- Earlybird hooks: Deep tech, AI as infrastructure

SLIDE 5 (product): "Without Governance, Nothing Goes to Production"
- 3 pillars: Compliance (DSGVO, AI Act), Auditability (traceable actions), Control (human-in-the-loop)
- "Operational AI = 50% Tech, 50% Mensch"
- This is what makes NeuraPlox enterprise-deployable vs. every other agent framework
- Earlybird hooks: European digital sovereignty, Domain expertise

SLIDE 6 (why-now): "We Don't Just Build the OS — We Ship the Killer Apps"
- Market shift: Enterprise AI moving from PoC to production NOW (August 2026 AI Act deadline)
- Technology enabler: LLM costs dropping, agents becoming viable for enterprise workflows
- Timing catalyst: 25+ consulting projects prove enterprises need this NOW
- 3 agents: Market Intelligence, Marketing Intelligence, Vertriebs Intelligence
- Each replaces entire consulting function with one metric per agent
- Earlybird hooks: AI as infrastructure (agents do real work)

SLIDE 7 (competitive-landscape): "Entire Consulting Functions — Replaced by Agent Workflows"
- Prism Agent Flow: tax advisor, accounts payable, bookkeeping — all AI-native
- Shopify analogy: Shopify → online stores; Prism → AI operations
- Positioning: NeuraPlox vs. point solutions (LangChain, Langdock) vs. hyperscalers
- Differentiated axes: Infrastructure depth × Mittelstand economics
- AI commoditization rebuttal: Governance layer MORE valuable as models commoditize
- Earlybird hooks: Category creation (new delivery model)

SLIDE 8 (traction): "25+ Enterprise Projects, 15-Person Team, ZIM-Funded"
- Key numbers: [projects, team size, ZIM grant amount from Antrag v9]
- Frame: "Consulting is our R&D lab — every project feeds platform features"
- Customer evidence: [anonymized cases from Antrag v9 with quantified ROI]
- ARR gap — address head-on: "Current revenue is consulting. Platform launch [timeline]. This raise funds the transition."
- Proxy metrics: repeat engagement rate, project expansion from consulting
- Earlybird hooks: Capital-efficient growth

SLIDE 9 (business-model): "Consulting Funds Today, Platform Captures Tomorrow, Marketplace Multiplies"
- H1 (now): Consulting ~30% margin
- H2 (12-18mo): Platform SaaS ~70% margin — per-agent, per-connector pricing
- H3 (24mo+): Marketplace ~80%+ margin — revenue share on third-party agents
- Unit economics: [ACV, LTV, CAC, payback from Antrag v9]
- Earlybird hooks: Capital-efficient growth

SLIDE 10 (market-sizing): "The Agent OS Market Doesn't Exist Yet — We're Creating It"
- Bottom-up: [ICP count × adoption rate × ACV from Antrag v9]
- Category: Not competing in "AI tools" — defining "Agent OS"
- Adjacent disruption: enterprise middleware, consulting, RPA
- Earlybird hooks: Category creation, Global winner potential

SLIDE 11 (go-to-market): "Land Via Consulting, Expand Via Platform, Open Via Marketplace"
- Phase 1: Consulting → platform conversion (warm pipeline)
- Phase 2: Self-serve platform for mid-market
- Phase 3: Marketplace — third-party agents + SIs
- Flywheel: more agents → more data → better governance → more trust → more agents
- Earlybird hooks: Global winner (marketplace scales without linear headcount)

SLIDE 12 (financials): "Network Effects Make This a Winner-Take-Most Market"
- Revenue trajectory: [Y1/Y2/Y3 from Antrag v9]
- Break-even: [customer count / ARR figure]
- Flywheel: agents ↔ connectors ↔ data ↔ governance ↔ trust
- Anti-"Süßes Gift": Open architecture = no lock-in, but ecosystem sticky
- International: Platform + marketplace scale beyond DACH
- SAP precedent: Started DACH → went global
- Earlybird hooks: Global winner from European base

SLIDE 13 (team): "15 People, Deep Enterprise AI + Domain Expertise"
- Full team from Antrag v9 (all 15, not just founders)
- Domain expertise: consulting backgrounds → agent knowledge
- CTO gap: "Hiring platform-scale CTO is priority #1 for this raise"
- Earlybird hooks: Industrial/enterprise domain expertise

SLIDE 14 (the-ask): [Specific Amount from Antrag v9 Financial Model]
- Use of funds: (1) CTO + engineering, (2) Platform launch, (3) Marketplace agents
- Milestones: Platform GA, first 10 paying customers, marketplace beta
- ONE number, not a range
- Earlybird hooks: Clear commercialization path

SLIDE 15 (ai-architecture): "The Open AI OS for Europe"
- NOT a technical deep-dive — this is the CLOSING slide
- Circle back: European sovereignty = Europe's AI OS
- Anti-sweet-poison: Openness as strategic advantage
- Bold closing statement
- Earlybird hooks: European digital sovereignty, Global winner
```

**Step 2: Verify DOCX is valid**

```bash
python -c "from docx import Document; d = Document('INPUT/neuraplox_v7_narrative_brief.docx'); print(f'{len(d.paragraphs)} paragraphs')"
```

Expected: ~100+ paragraphs, no errors.

**Step 3: Commit**

```bash
git add INPUT/neuraplox_v7_narrative_brief.docx
git commit -m "docs: add v7 narrative brief DOCX for deck generation"
```

---

### Task 3: Generate v7 Deck

**Files:**
- Input: `INPUT/neuraplox_v7_narrative_brief.docx`, `INPUT/Antrag_v9.pdf`
- Output: `output/neuraplox/v7/deck.md`, `output/neuraplox/v7/deck.json`

**Step 1: Create output directory**

```bash
mkdir -p output/neuraplox/v7
```

**Step 2: Run pitchdeck generate**

```bash
pitchdeck generate \
  INPUT/neuraplox_v7_narrative_brief.docx \
  INPUT/Antrag_v9.pdf \
  --vc earlybird \
  --output output/neuraplox/v7/deck.md \
  --json output/neuraplox/v7/deck.json \
  --skip-gaps
```

We use `--skip-gaps` because the narrative brief already encodes our design decisions.

**Step 3: Verify output**

```bash
python -c "
import json
with open('output/neuraplox/v7/deck.json') as f:
    deck = json.load(f)
print(f'Slides: {len(deck[\"slides\"])}')
for s in deck['slides']:
    print(f'  {s[\"slide_number\"]}: {s[\"slide_type\"]} — {s[\"title\"][:60]}')
"
```

Expected: 15 slides, all required types present, titles matching v7 design.

---

### Task 4: Review Generated Deck Against v7 Design

**Files:**
- Read: `output/neuraplox/v7/deck.json`
- Read: `docs/plans/2026-02-26-deck-v7-design.md`

**Step 1: Check slide type coverage**

Verify all 15 required slide types are present:
`cover, executive-summary, problem, why-now, solution, product, market-sizing, business-model, traction, go-to-market, competitive-landscape, team, financials, the-ask, ai-architecture`

**Step 2: Check word limits**

For each slide, count words in title + headline + bullets. Compare against template word limits:
- cover: 30, executive-summary: 100, problem: 120, why-now: 120, solution: 150
- product: 150, market-sizing: 120, business-model: 130, traction: 130
- go-to-market: 130, competitive-landscape: 120, team: 150, financials: 120
- the-ask: 130, ai-architecture: 150

v6 exceeded ALL limits. v7 MUST stay within limits. Flag any overages.

**Step 3: Check v7 design alignment**

For each slide, verify:
- Title/headline matches v7 design intent (not default template content)
- SAP analogy appears in slide 3 (executive-summary)
- Governance is on slide 5 (product), not architecture
- Showcase agents on slide 6 (why-now)
- Prism on slide 7 (competitive-landscape)
- Growth flywheel on slide 12 (financials)
- Closing is vision/sovereignty on slide 15 (ai-architecture), NOT tech deep-dive

**Step 4: Check Earlybird thesis keywords**

Verify these keywords appear in deck content (the custom_checks validator uses keyword matching):
- `sovereign`, `european`, `europe`, `data sovereignty`, `digital sovereignty`
- `bottom-up`, `som`, `icp count`, `arpu`
- `capital efficien`, `burn multiple`, `capital-efficient`
- `customer`, `pilot`, `case study`, `roi`
- `commodit`, `moat`, `defensib`, `proprietary`
- `gross margin`, `margin trajectory`
- `category`, `category creation`

**Step 5: Manual edits if needed**

If generation drifted from v7 design, manually edit `deck.json`:
- Fix slide content to match design
- Trim words to stay within limits
- Add missing Earlybird keywords
- Ensure speaker notes are present on all slides
- Ensure vc_alignment_notes reference specific thesis points

Re-save as valid JSON after edits.

**Step 6: Commit**

```bash
git add output/neuraplox/v7/
git commit -m "feat: generate deck v7 initial version"
```

---

### Task 5: Validate Against Earlybird

**Files:**
- Input: `output/neuraplox/v7/deck.json`
- Output: `output/neuraplox/v7/validation_report.md`

**Step 1: Run validation**

```bash
pitchdeck validate \
  output/neuraplox/v7/deck.json \
  --vc earlybird \
  --output output/neuraplox/v7/validation_report.md \
  --threshold 60
```

**Step 2: Read validation report**

Check:
- Overall score (target: >= 90)
- Per-dimension scores (targets in table above)
- Custom checks: all 7 should PASS
- Per-slide scores: no slide below 80
- Critical gaps: should be fewer and less severe than v6
- Improvement priorities: note top 3

**Step 3: Commit**

```bash
git add output/neuraplox/v7/validation_report.md
git commit -m "docs: add deck v7 validation report (iteration 1)"
```

---

### Task 6: Iterate Based on Validation (up to 3 rounds)

**For each iteration:**

**Step 1: Analyze validation gaps**

From the validation report, identify:
- Which dimensions scored below target?
- Which slides have issues?
- Which custom checks failed?
- What are the top improvement priorities?

**Step 2: Fix deck.json**

For each issue:
- Word limit violations → trim content, keep ONE core message per slide
- Missing metrics → add specific data points from v7-data-points.md
- Thesis alignment gaps → add keywords and explicit thesis references
- Narrative coherence issues → fix transitions, ensure arc flows
- Common mistakes → address each flagged mistake directly

**Step 3: Re-validate**

```bash
pitchdeck validate \
  output/neuraplox/v7/deck.json \
  --vc earlybird \
  --output output/neuraplox/v7/validation_report.md \
  --threshold 60
```

**Step 4: Check score improvement**

If >= 90: proceed to Task 7.
If < 90 but improving: repeat iteration.
If < 85 after 3 rounds: present gaps to user for strategic decision.

**Step 5: Commit each iteration**

```bash
git add output/neuraplox/v7/
git commit -m "fix: deck v7 iteration N — address validation gaps"
```

---

### Task 7: Regenerate Markdown and Finalize

**Files:**
- Read: `output/neuraplox/v7/deck.json`
- Create/Update: `output/neuraplox/v7/deck.md`

**Step 1: Regenerate markdown from final JSON**

The deck.md should be regenerated from the final deck.json to ensure consistency.
Use the markdown renderer: `src/pitchdeck/output/markdown.py`

```bash
python -c "
from pitchdeck.models import PitchDeck
from pitchdeck.output import save_markdown
import json

with open('output/neuraplox/v7/deck.json') as f:
    deck = PitchDeck.model_validate_json(f.read())

save_markdown(deck, 'output/neuraplox/v7/deck.md')
print(f'Saved {len(deck.slides)} slides to deck.md')
"
```

**Step 2: Final validation pass**

```bash
pitchdeck validate \
  output/neuraplox/v7/deck.json \
  --vc earlybird \
  --output output/neuraplox/v7/validation_report.md
```

Verify score is still >= 90 after markdown regeneration (JSON unchanged, so should be same).

**Step 3: Final commit**

```bash
git add output/neuraplox/v7/
git commit -m "feat: finalize deck v7 — score XX/100 against Earlybird"
```

---

## Success Criteria

- [ ] Score >= 90/100 overall against Earlybird profile
- [ ] All 7 custom checks PASS
- [ ] All slides within word limits
- [ ] No "critical" gaps in validation report
- [ ] v7 design narrative faithfully represented (SAP analogy, governance, agents, flywheel, closing)
- [ ] All 9 v6 critical gaps addressed per gap remediation strategy
- [ ] Output in `output/neuraplox/v7/` with deck.md, deck.json, validation_report.md
