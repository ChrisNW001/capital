# Deck v7 Execution State

**Last updated:** 2026-02-26
**Plan file:** `docs/plans/2026-02-26-deck-v7-implementation.md`
**Skill:** superpowers:executing-plans

---

## Completed Tasks

### Task 1: Extract Key Data Points from Antrag v9
- **Commit:** `4fa2d35` — `docs: extract Antrag v9 data points for deck v7`
- **Output:** `docs/plans/v7-data-points.md` (198 lines, all financials, team, market data extracted)

### Task 2: Write v7 Narrative Brief DOCX
- **Commit:** `ef9d062` — `docs: add v7 narrative brief DOCX for deck generation`
- **Output:** `INPUT/neuraplox_v7_narrative_brief.docx` (176 paragraphs, slide-by-slide design)

### Task 3: Generate v7 Deck
- **Commit:** `3185251` — `feat: generate deck v7 initial version`
- **Output:** `output/neuraplox/v7/deck.json`, `output/neuraplox/v7/deck.md` (15 slides)

---

## Remaining Tasks

### Task 4: Review Generated Deck Against v7 Design (NEXT)
**Known issue:** The generator reordered slides vs. the v7 design. Current order:
```
1: cover ✓ (matches v7)
2: executive-summary (v7 wants this at position 3)
3: problem (v7 wants this at position 2)
4: why-now (v7 wants this at position 6)
5: solution (v7 wants this at position 4)
6: product (v7 wants this at position 5)
7: market-sizing (v7 wants this at position 10)
8: business-model (v7 wants this at position 9)
9: traction (v7 wants this at position 8)
10: go-to-market (v7 wants this at position 11)
11: competitive-landscape (v7 wants this at position 7)
12: team (v7 wants this at position 13)
13: financials (v7 wants this at position 12)
14: the-ask ✓ (matches v7)
15: ai-architecture ✓ (matches v7)
```

**Steps for Task 4:**
1. Reorder slides to match v7 design order
2. Check word limits (max 80 words per slide body)
3. Check v7 design alignment (SAP analogy on slide 3, governance on slide 5, etc.)
4. Check Earlybird thesis keywords
5. Manual edits to deck.json if needed
6. Commit

### Task 5: Validate Against Earlybird
```bash
python3 -m pitchdeck validate output/neuraplox/v7/deck.json --vc earlybird --output output/neuraplox/v7/validation_report.md --threshold 60
```
Target: >= 90/100 overall score.

### Task 6: Iterate Based on Validation (up to 3 rounds)
Fix gaps from validation report, re-validate, repeat until >= 90 or 3 rounds.

### Task 7: Regenerate Markdown and Finalize
Regenerate deck.md from final deck.json, final validation pass, commit with score.

---

## Key Commands

- Generate: `python3 -m pitchdeck generate` (NOT `pitchdeck generate`)
- Validate: `python3 -m pitchdeck validate` (NOT `pitchdeck validate`)
- Python: `python3` (NOT `python`)

## Key Files

- **Implementation plan:** `docs/plans/2026-02-26-deck-v7-implementation.md`
- **Design document:** `docs/plans/2026-02-26-deck-v7-design.md`
- **Data points reference:** `docs/plans/v7-data-points.md`
- **Narrative brief:** `INPUT/neuraplox_v7_narrative_brief.docx`
- **Generated deck:** `output/neuraplox/v7/deck.json` + `deck.md`
- **Earlybird profile:** `profiles/earlybird.yaml`
- **Slide templates (word limits):** `src/pitchdeck/engine/slides.py`

## Resume Instructions

Tell Claude:
```
Resume deck v7 execution from Task 4. Read docs/plans/v7-execution-state.md for full context, then continue with the executing-plans skill starting from Task 4.
```
