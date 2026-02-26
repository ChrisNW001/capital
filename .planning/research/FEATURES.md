# Feature Research

**Domain:** Visual slide generation CLI (Python) — 4K presentation slide image generation via LLM + image model pipeline
**Researched:** 2026-02-26
**Confidence:** HIGH (core pipeline patterns), MEDIUM (API resolution limits), HIGH (output format choices)

---

## Context: What Already Exists

The `pitchdeck generate` command already produces `deck.json` — a structured `PitchDeck` model with 15 `SlideContent` objects. Each slide has: `slide_number`, `slide_type`, `title`, `headline`, `bullets`, `metrics`, `speaker_notes`. The `pitchdeck design` command is a downstream consumer of this JSON. It does not generate content; it visualizes it.

A working prototype exists: `generate_slides.py` (root of project). It demonstrates the 2-step pipeline: Gemini Flash elaboration → Imagen 4 image generation. The new `design` command is a productionized, integrated version of this script.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Accepts deck JSON as input | The `generate` command produces JSON; `design` must consume it | LOW | `PitchDeck.model_validate_json()` pattern already exists in `validate` command — replicate exactly |
| Per-slide progress output | 15 API calls take 2-5 minutes; silent CLI = user assumes crash | LOW | Rich `Progress` + per-slide status lines (already done in prototype: "Elaborating via Gemini... OK") |
| PNG output for each slide | Industry standard for slide images; editors, upload tools expect PNG | LOW | Already works in prototype via `image_bytes` write; naming convention: `slide_01.png` ... `slide_15.png` |
| Output directory creation | User should not need to pre-create directories | LOW | `Path.mkdir(parents=True, exist_ok=True)` — trivial |
| Design system selection | 3 systems exist (Consulting Light, Training Dark, Brochure A4); user needs to choose | LOW | `--design` flag with choices; default to `consulting-light` |
| GEMINI_API_KEY validation | Missing key should give clear error before any API calls | LOW | Same pattern as `ANTHROPIC_API_KEY` check in `generate` — check at command entry, raise `PitchDeckError` |
| Summary output on completion | "Generated 15/15 slides" — user needs confirmation | LOW | Already in prototype's `main()` summary block |
| 16:9 aspect ratio | Standard presentation format; 16:9 is the near-universal investor deck format | LOW | `aspect_ratio="16:9"` in `generate_images()` config — Imagen 4 supports this natively |
| Slide-by-slide error reporting | One failed slide should not abort all 15; report failures at end | MEDIUM | `continue` pattern in prototype is correct; accumulate `failed` list with slide numbers and error reasons |
| ZIP export | Users need to send or upload all slides as a package | MEDIUM | Python stdlib `zipfile` — no new dependency; bundle all `slide_N.png` files into `slides.zip` |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| 3 design systems (Consulting Light, Training Dark, Brochure A4) | Matches presentation context: boardroom vs. conference vs. brochure handout | MEDIUM | Each system is ~1000-line XML; must be loaded as package data (not `/tmp/nw-slide-ai/` hardcoded path) |
| PDF assembly from slides | Investors receive single PDF; easier to share than ZIP of PNGs | MEDIUM | `reportlab` or Pillow's `save(..., format='PDF', save_all=True, append_images=[...])` — Pillow approach is simpler and avoids new heavy dep |
| Partial generation resume (`--from-slide N`) | 15 API calls; if slide 12 fails, user can resume from 12 without regenerating 1-11 | MEDIUM | Skip slides where `slide_N.png` already exists in output dir, OR use `--from-slide N` flag; saves significant API cost |
| Per-slide retry on failure | Single-slide API failures (rate limit, safety filter) are transient; auto-retry saves re-running | MEDIUM | Wrap image gen in retry loop (max 2 retries, 10s backoff) using `time.sleep`; no new dep needed |
| A4 portrait aspect ratio for brochure design | The Brochure A4 design system targets print/handout format (portrait, not 16:9) | MEDIUM | Imagen 4 supports 3:4 aspect ratio (portrait); map `brochure-a4` design → `aspect_ratio="3:4"` automatically |
| Verbose mode (`--verbose`) showing elaborated XML | Designers need to inspect/tune the elaborated XML prompts for quality improvement | LOW | `--verbose` flag; print XML prompt to console before sending to Imagen |
| Dry-run mode (`--dry-run`) | Validate pipeline (load JSON, load design system, elaborate prompts) without burning Imagen API credits | MEDIUM | Run Gemini elaboration steps only, skip Imagen calls, write XML files to disk |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Live slide preview (open images as generated) | "I want to see slides as they render" | Opens 15 OS image viewer windows; breaks CLI UX; not portable across environments | Print file path to console after each save so user can open manually |
| Custom user XML design system upload | "I want my own brand" | Arbitrary XML from users may cause Gemini elaboration failures; unvalidatable surface area; massive scope | Document 3 built-in design systems; defer custom design systems to v2 (already noted as out-of-scope in PROJECT.md) |
| Parallel slide generation (async) | "Make it faster" | Imagen 4 rate limits are poorly documented; parallel calls cause rate limit 429s; complex error recovery; not worth the complexity for 15 slides | Sequential generation with per-slide progress is acceptable for 15-slide decks; 2-4 min total is fine |
| "4K" resolution (3840×2160) | "Highest quality" | Imagen 4 API maximum is approximately 2K (up to ~2816×1536 for 16:9 per current docs); the API does not support true 4K output — marketing language in PROJECT.md is aspirational | Generate at maximum supported 2K resolution with `imageSize="2K"` parameter; rename output to reflect actual resolution |
| PPTX/Keynote export | "I want a real deck file" | `python-pptx` adds a new heavy dependency; inserting rasterized PNG slides into PPTX loses editability anyway | PDF export (Pillow-based) is the right format for sharing non-editable high-quality presentation |
| Logo/watermark overlay | "Add our logo to every slide" | Pillow compositing requires careful positioning per design system; inconsistent results; already explicitly deferred in PROJECT.md | Confirmed out-of-scope for v1; add to PROJECT.md backlog |
| Slide content editing before render | "Let me tweak the bullets before generating" | Would require interactive TUI; belongs in `generate` command iteration, not `design` | User edits `deck.json` directly before running `design`; document this workflow |

---

## Feature Dependencies

```
[deck.json from `pitchdeck generate`]
    └──required input──> [design command: JSON parsing]
                             └──requires──> [design system selection + loading]
                                                └──requires──> [design system files as package data]
                             └──requires──> [Gemini elaboration (per slide)]
                                                └──enables──> [verbose mode: show XML]
                                                └──enables──> [dry-run mode: skip Imagen]
                             └──requires──> [Imagen 4 generation (per slide)]
                                                └──produces──> [PNG per slide]
                                                                   └──enables──> [ZIP export]
                                                                   └──enables──> [PDF assembly]
                                                                   └──enables──> [partial resume]

[--design flag] ──selects──> [design system XML] ──controls──> [aspect ratio choice]
    └── consulting-light → 16:9
    └── training-dark    → 16:9
    └── brochure-a4      → 3:4 (portrait)

[PDF assembly] ──requires──> [all PNGs present] OR [partial set with warning]
[ZIP export]   ──requires──> [all PNGs present] OR [partial set with warning]

[per-slide retry] ──reduces──> [failed count]
[partial resume]  ──conflicts with──> [always-overwrite behavior]
```

### Dependency Notes

- **JSON parsing requires deck.json**: The `design` command has no content generation capability; it is purely a renderer. If `deck.json` is absent or malformed, fail early with the same error pattern as `validate` command.
- **Design system selection controls aspect ratio**: The Brochure A4 system is inherently portrait; the CLI should automatically pass `aspect_ratio="3:4"` when `--design brochure-a4` is chosen. No user configuration of aspect ratio separately.
- **PDF assembly requires Pillow**: Pillow is already a declared dependency in PROJECT.md; use `Image.save()` with `save_all=True` to create multi-page TIFF-like PDF. No `reportlab` needed.
- **Partial resume conflicts with overwrite**: If `--from-slide N`, skip writing slides 1 to N-1 (do not re-generate them). Must check existing files on disk, not just skip API calls. Document: existing files are not overwritten by default.

---

## MVP Definition

### Launch With (v1 — this milestone)

Minimum viable product — what's needed for the `pitchdeck design` command to be useful.

- [ ] `pitchdeck design <deck.json>` command entry point — Typer command following `validate` command pattern
- [ ] GEMINI_API_KEY validation at command entry — clear error if missing
- [ ] Design system selection via `--design` flag — choices: `consulting-light` (default), `training-dark`, `brochure-a4`
- [ ] Design system loading as package data (not `/tmp/` hardcoded path) — port `load_design_system()` from prototype
- [ ] Per-slide Gemini elaboration (2-step pipeline: Gemini Flash → XML) — port `elaborate_slide()` from prototype
- [ ] Per-slide Imagen 4 generation — port `generate_image()` from prototype; use `imageSize="2K"` for maximum quality
- [ ] Slide-type visualization hints (VIZ_HINTS mapping) — port from prototype; extend with remaining slide types
- [ ] Per-slide progress output — Rich `Progress` bar with slide number and status
- [ ] PNG output per slide — `slide_01.png` through `slide_15.png` in `--output` dir
- [ ] Output directory auto-creation — `Path.mkdir(parents=True, exist_ok=True)`
- [ ] Continue-on-error for individual slides — accumulate failures, report at end, exit code 1 if any failed
- [ ] Summary output — "Generated X/15 slides", list failed slides with reasons
- [ ] ZIP export — `--zip` flag writes `slides.zip` alongside output directory
- [ ] Sensible default output path — `output/<company_name>/slides/` derived from deck JSON `company_name` field

### Add After Validation (v1.x)

Features to add once core is working and tested.

- [ ] PDF assembly — `--pdf` flag; Pillow multi-image PDF; requires Pillow already in deps
- [ ] Partial resume (`--from-slide N`) — skip slides 1..N-1; check for existing PNG before API call
- [ ] Per-slide auto-retry (max 2 retries, 10s backoff) — transient rate limit handling; no new deps
- [ ] Verbose mode (`--verbose`) — print elaborated XML before Imagen call
- [ ] Dry-run mode (`--dry-run`) — run elaboration only, write XML files to disk, skip Imagen

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] Custom user-provided design systems — already marked out-of-scope in PROJECT.md
- [ ] Logo/watermark overlay — already deferred in PROJECT.md
- [ ] Parallel async generation — only valuable if deck sizes grow beyond 20+ slides
- [ ] PPTX export — requires `python-pptx`, adds complexity without editability value for rasterized slides

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Design command entry + GEMINI_API_KEY check | HIGH | LOW | P1 |
| Design system loading as package data | HIGH | LOW | P1 |
| Per-slide Gemini elaboration | HIGH | LOW | P1 |
| Per-slide Imagen 4 generation (16:9 PNG) | HIGH | LOW | P1 |
| Per-slide progress output (Rich) | HIGH | LOW | P1 |
| PNG output with consistent naming | HIGH | LOW | P1 |
| Continue-on-error + failure summary | HIGH | LOW | P1 |
| ZIP export (`--zip`) | MEDIUM | LOW | P1 |
| 3 design system choices (`--design`) | MEDIUM | MEDIUM | P1 |
| Brochure A4 portrait aspect ratio auto-mapping | MEDIUM | LOW | P1 |
| PDF assembly (`--pdf`) | MEDIUM | LOW | P2 |
| Partial resume (`--from-slide N`) | MEDIUM | MEDIUM | P2 |
| Per-slide auto-retry | MEDIUM | MEDIUM | P2 |
| Verbose XML output (`--verbose`) | LOW | LOW | P2 |
| Dry-run mode (`--dry-run`) | LOW | MEDIUM | P3 |
| Custom design systems | LOW | HIGH | P3 |
| Logo/watermark overlay | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch (this milestone)
- P2: Should have, add when core is working
- P3: Nice to have, future consideration

---

## Competitor Feature Analysis

| Feature | Gamma / Beautiful.ai (web) | NW Slide AI (reference implementation) | Our Approach |
|---------|----------------------------|----------------------------------------|--------------|
| Input format | Text prompt / outline | Deck JSON + design system XML | Deck JSON from `pitchdeck generate` (structured, typed) |
| Design selection | Template gallery (UI) | 3 XML design systems (code constant) | `--design` CLI flag selecting from 3 ported systems |
| Generation pipeline | Proprietary | Gemini Pro elaboration → Imagen 4 image gen | Identical 2-step pipeline (Gemini Flash → Imagen 4) |
| Aspect ratio | 16:9, 4:3 (UI toggle) | 16:9 hardcoded | 16:9 for consulting/training, 3:4 for brochure-a4 |
| Output format | Download ZIP or PDF | PNG files to disk | PNG per slide + optional ZIP + optional PDF |
| Progress indication | Progress bar (web UI) | Console print per slide | Rich Progress bar + per-slide status lines |
| Error recovery | Full retry (UI) | None (crashes on failure) | Continue-on-error; accumulate failures; partial resume in v1.x |
| API | None (consumer web UI) | None (standalone script) | CLI command integrated in `pitchdeck` tool |
| Language/text support | English | German text enforced in prompts | Preserve existing German-language prompt enforcement from prototype |
| Watermark | No | SynthID (API-applied, not controllable) | SynthID watermark applied by API automatically; no logo overlay in v1 |

---

## API Reality Check: Resolution

**Critical finding (MEDIUM confidence — WebSearch verified):** Imagen 4 does not support true 4K (3840×2160) output. The API maximum is approximately **2K resolution** — up to roughly 2816×1536 for 16:9 aspect ratio, or 2048×2048 for 1:1. PROJECT.md references "4K (3840x2160)" as the target output size. This is not achievable with the current Imagen 4 API.

**Recommendation:** Use `imageSize="2K"` parameter in `generate_images()` config to get maximum supported resolution. Document output as "high-resolution (up to 2K)" rather than 4K. The visual quality difference at typical viewing distances on screens is negligible for presentation use. If true 4K is required in future, Vertex AI Imagen may offer different limits.

**Output format finding (MEDIUM confidence — WebSearch only):** The `output_mime_type` parameter may be limited to `image/jpeg` in the current Gemini API SDK (per search result citing `types.GenerateImagesConfig`). The prototype uses `image/png` — verify against actual SDK behavior. JPEG at high quality is acceptable for presentation slides; PNG is preferable for pixel-perfect text edges. If JPEG is the only option, save with quality 95+ and document this.

---

## Dependencies on Existing Generate Command

The `design` command has a strict dependency on the `generate` command's JSON output format:

| Field from `PitchDeck` | Used by `design` | Required |
|------------------------|-------------------|----------|
| `company_name` | Default output directory naming | Yes |
| `slides[].slide_number` | File naming `slide_N.png`, progress tracking | Yes |
| `slides[].slide_type` | VIZ_HINTS lookup for design guidance | Yes |
| `slides[].title` | Slide description for elaboration prompt | Yes |
| `slides[].headline` | Slide description for elaboration prompt | Yes |
| `slides[].bullets` | Slide description for elaboration prompt | Yes |
| `slides[].metrics` | Slide description for elaboration prompt | Yes |
| `slides[].speaker_notes` | NOT used by design (design-irrelevant) | No |
| `slides[].transition_to_next` | NOT used by design (design-irrelevant) | No |
| `gaps_identified` | NOT used by design | No |

**Important:** The `design` command must accept any valid `PitchDeck` JSON — not just the latest generated output. A user should be able to save `deck.json`, edit bullets manually, then run `pitchdeck design deck.json` to re-render visuals. This is a key part of the separation-of-concerns rationale for keeping `design` independent from `generate`.

---

## Sources

- Google AI for Developers — Imagen documentation: [Generate images using Imagen | Gemini API](https://ai.google.dev/gemini-api/docs/imagen)
- Google Cloud — Imagen 4 Ultra model: [Imagen 4 Ultra | Generative AI on Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-ultra-generate-001)
- Google Developers Blog — Imagen 4 family GA: [Announcing Imagen 4 Fast and the general availability of the Imagen 4 family](https://developers.googleblog.com/en/announcing-imagen-4-fast-and-imagen-4-family-generally-available-in-the-gemini-api/)
- Python stdlib zipfile: [zipfile — Work with ZIP archives](https://docs.python.org/3/library/zipfile.html)
- ReportLab docs (alternative, not recommended — use Pillow instead): [ReportLab Docs](https://docs.reportlab.com/reportlab/userguide/ch2_graphics/)
- Gemini 2.5 Flash image prompting best practices: [How to prompt Gemini 2.5 Flash Image Generation](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/)
- MindStudio — Imagen 4 Ultra specifications: [What Is Imagen 4 Ultra?](https://www.mindstudio.ai/blog/what-is-imagen-4-ultra-google)
- Existing prototype: `/root/projects/capital/generate_slides.py` (primary reference implementation)

---

*Feature research for: Visual slide generation CLI (pitchdeck design command)*
*Researched: 2026-02-26*
