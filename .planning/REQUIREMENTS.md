# Requirements: Pitchdeck

**Defined:** 2026-02-26
**Core Value:** Generate investor-ready pitch decks with professional visual slides matching the target VC's thesis

## v1.1 Requirements

Requirements for Visual Slide Design milestone. Each maps to roadmap phases.

### Design Pipeline

- [ ] **PIPE-01**: User can run `pitchdeck design <deck.json>` to generate visual slides from existing deck JSON
- [ ] **PIPE-02**: CLI validates GEMINI_API_KEY presence at command entry with clear error message
- [ ] **PIPE-03**: Each slide is elaborated via Gemini Flash into a structured XML image prompt using the selected design system
- [ ] **PIPE-04**: Each elaborated prompt is sent to Imagen 4 to generate a high-resolution slide image
- [ ] **PIPE-05**: User sees Rich progress output per slide (slide number, status, elapsed time)
- [ ] **PIPE-06**: User can pass `--verbose` to see the elaborated XML prompt for each slide before Imagen generation

### Design Systems

- [ ] **DSYS-01**: User can select design system via `--design` flag (choices: consulting-light, training-dark, brochure-a4; default: consulting-light)
- [ ] **DSYS-02**: Design systems are loaded as Python package data from XML files (not hardcoded strings)
- [ ] **DSYS-03**: Brochure A4 design automatically uses 3:4 portrait aspect ratio; others use 16:9

### Output & Export

- [ ] **OUTP-01**: Each generated slide is saved as individual PNG file (slide_01.png through slide_15.png)
- [ ] **OUTP-02**: Output directory is auto-created; default path derived from deck company name
- [ ] **OUTP-03**: User can export all slides as ZIP archive via `--zip` flag
- [ ] **OUTP-04**: User can export all slides as assembled PDF via `--pdf` flag
- [ ] **OUTP-05**: Summary output on completion shows success count, failed count, and output paths

### Reliability

- [ ] **RELY-01**: Single-slide generation failure does not abort the entire deck — errors are isolated per slide
- [ ] **RELY-02**: Failed slides are auto-retried (max 2 retries with exponential backoff)
- [ ] **RELY-03**: Final summary lists all failed slides with error reasons; exit code 1 if any failures
- [ ] **RELY-04**: Images are written to disk immediately after generation (no in-memory accumulation)

### Integration

- [ ] **INTG-01**: GEMINI_API_KEY is loaded from .env via existing python-dotenv pattern
- [ ] **INTG-02**: New dependencies (google-genai, Pillow, img2pdf) added to pyproject.toml
- [ ] **INTG-03**: All new models added to src/pitchdeck/models.py following existing Pydantic patterns

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Custom Design

- **CUST-01**: User can provide custom XML design system file via --design-file flag
- **CUST-02**: User can overlay logo/watermark on generated slides via --logo flag

### Advanced Pipeline

- **ADVP-01**: User can resume partial generation with --from-slide N flag
- **ADVP-02**: User can run in dry-run mode (elaboration only, no Imagen credits)
- **ADVP-03**: User can generate slides in parallel for faster throughput

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time web UI | CLI-only tool; NW Slide AI is the web implementation |
| PPTX/Keynote export | Rasterized slides lose editability; PDF covers sharing use case |
| Video/animation | Out of domain for static pitch decks |
| Custom design system upload | Arbitrary XML is unvalidatable; defer to v2 |
| Logo/watermark overlay | Pillow compositing complexity; defer to v2 |
| Parallel async generation | Imagen rate limits poorly documented; sequential is acceptable for 15 slides |
| True 4K output | Imagen 4 API max is ~2K; upscaling adds complexity without visible quality gain |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PIPE-01 | — | Pending |
| PIPE-02 | — | Pending |
| PIPE-03 | — | Pending |
| PIPE-04 | — | Pending |
| PIPE-05 | — | Pending |
| PIPE-06 | — | Pending |
| DSYS-01 | — | Pending |
| DSYS-02 | — | Pending |
| DSYS-03 | — | Pending |
| OUTP-01 | — | Pending |
| OUTP-02 | — | Pending |
| OUTP-03 | — | Pending |
| OUTP-04 | — | Pending |
| OUTP-05 | — | Pending |
| RELY-01 | — | Pending |
| RELY-02 | — | Pending |
| RELY-03 | — | Pending |
| RELY-04 | — | Pending |
| INTG-01 | — | Pending |
| INTG-02 | — | Pending |
| INTG-03 | — | Pending |

**Coverage:**
- v1.1 requirements: 21 total
- Mapped to phases: 0
- Unmapped: 21

---
*Requirements defined: 2026-02-26*
*Last updated: 2026-02-26 after initial definition*
