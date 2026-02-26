# NeuraPlox Deck v7 — Brainstorming State (Pause Point)

**Date:** 2026-02-26
**Status:** Brainstorming Step 3 — "Propose 2-3 approaches" (not yet started)
**Completed:** Steps 1 (Explore context) and 2 (Clarifying questions)
**Next:** Propose approaches → Present design → Write design doc → Invoke writing-plans

---

## Clarifying Questions — Answers

| # | Question | Answer |
|---|----------|--------|
| 1 | Call Intelligence — what is it? | (B) Showcase-Agent, illustration of "we deliver top agents with the platform" |
| 2 | Other 2-3 agents? | (C) From consulting experience: **Market Intelligence, Marketing Intelligence, Vertriebs Intelligence** + **Prism Agent Flow** (replaces entire consulting functions: tax advisor, accounts payable, bookkeeper — all AI-native) |
| 3 | Deck weighting? | (A) **Platform-first 60%**, Agents as proof 20%, Marketplace as vision 20% |
| 4 | Core narrative? | Scalable AI OS for enterprises. Agents auto-create interfaces to IT systems. Governance makes it enterprise-deployable and compliance-safe. Without governance, nothing goes into production. |
| 5 | Goal output? | (C) Both — first design story/content, then use pitchdeck generate + validate tool iteratively against Earlybird profile |
| 6 | Data update? | ZIM archive in INPUT/zim_archiv/ — same data as Antrag v9, no new financials. Currently ONLY consulting revenue, no platform ARR yet. |

---

## Key Sources Read

- **Deck v6:** `output/neuraplox/current/deck.md` + `deck.json` — 15 slides, score 84/100
- **Validation v6:** `output/neuraplox/current/validation_report.md` — critical gaps identified
- **Antrag v9:** `INPUT/Antrag_v9.pdf` (47 pages, all read)
- **ZIM Archive:** `INPUT/zim_archiv/` — Projektbeschreibung_v2.pdf, Markteinfuehrungskonzept_v2.pdf, Wirkung_v2.pdf (all read)
- **Backlog:** `BACKLOG.md` — 7 ideas, all priority high/medium
- **Earlybird Profile:** `profiles/earlybird.yaml` — 7 thesis points, 15 slides preferred
- **neuraplox_deck.json:** full deck JSON structure

## Deck v6 Validation — Critical Gaps to Fix

1. **Zero confirmed platform ARR** for Series A ask (only consulting revenue)
2. **No CTO** with platform-scale engineering experience
3. **Global winner potential absent** — DACH-only, no international expansion thesis
4. All slides exceed word limits by 50-200%
5. Over-indexing on architecture vs. business proof
6. No NDR/retention metrics
7. No quantified customer ROI case study
8. Raise amount "€3-5M to be confirmed" — signals incomplete financial modeling
9. AI architecture slide (15) disrupts closing momentum

## What Must Change in v7 (User Requirements)

1. **Full coverage of Antrag v9 content** — team of 15, all financial data
2. **Marketplace storyline** — not just 7-layer infrastructure
3. **Incorporate ALL Backlog ideas:**
   - "SAP for the AI Era" positioning (high)
   - Prism Agents — replace consulting categories (high)
   - N+M Architecture as Moat (medium)
   - Agent Marketplace — third-party agents (high)
   - Operational AI — 50% Tech, 50% Mensch (high)
   - Operations as a Service — Shopify analogy (high)
   - Anti-"Süßes Gift" — openness as strategic advantage (medium)
4. **Showcase Agents:** Market Intelligence, Marketing Intelligence, Vertriebs Intelligence, Prism Flow
5. **Investment story reworked** — consulting-to-platform transition with clear path
6. **Growth story reworked** — ecosystem flywheel, not just direct sales
7. **GTM story reworked** — how to massively scale
8. **Iterative validation** against Earlybird profile

## Earlybird Thesis Points (must all be addressed)

1. European digital sovereignty
2. Category creation
3. Capital-efficient growth
4. AI as infrastructure, not veneer
5. Deep tech with commercialization path
6. **Global winner potential from European base** (WEAKEST in v6 — must fix)
7. Industrial/enterprise domain expertise

## Core Narrative Shift: v6 → v7

**v6:** "NeuraPlox is the missing infrastructure layer — 7-layer architecture for AI agents"
**v7:** "NeuraPlox is the AI Operating System for enterprises — scalable architecture where agents automatically create IT interfaces, governance-safe by design. We deliver the OS, the first killer agents (from 25+ consulting projects), AND open a marketplace. This is SAP for the AI era."

## Approach Direction (to be proposed in Step 3)

The three approaches should explore different narrative structures:
- **Approach A:** Platform-OS narrative lead (SAP analogy) → showcase agents → marketplace vision
- **Approach B:** Problem-led (consulting pain → agents that replace consultants) → platform enables scale → marketplace multiplies
- **Approach C:** Category-creation lead (new market category "Agent OS") → why now → platform + agents + ecosystem as unified thesis

Recommendation: Likely Approach A, because user chose platform-first (60/20/20).

## Files to Create/Modify

1. Design doc: `docs/plans/2026-02-26-deck-v7-design.md` (after approach approval)
2. Updated input for deck generation (neuraplox_deck.json or similar)
3. New deck via `pitchdeck generate`
4. Validation via `pitchdeck validate`
