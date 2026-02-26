# Project Research Summary

**Project:** pitchdeck visual slide generation (design command)
**Domain:** AI-powered visual presentation generation — Gemini/Imagen pipeline integrated into existing Python CLI
**Researched:** 2026-02-26
**Confidence:** HIGH (stack and architecture), HIGH (pitfalls), HIGH/MEDIUM (features)

## Executive Summary

The `pitchdeck design` command is a visual rendering pipeline layered on top of the existing `generate` command. Experts in this domain build a 2-step pipeline: an LLM elaboration step converts structured slide content into detailed image generation prompts (tuned to a design system), followed by a diffusion model call that produces the actual slide image. This pattern is validated by the NW Slide AI reference implementation and the existing `generate_slides.py` prototype in the project. The recommended approach is to productionize the prototype's 2-step pipeline (Gemini Flash elaboration + Imagen 4 generation) as a clean engine module following existing codebase patterns, with design systems stored as external XML files loaded via `importlib.resources`.

The recommended technology additions are minimal: `google-genai>=1.65.0` (the only supported Google AI Python SDK as of 2026), `Pillow>=12.1.0` for image processing and 2K-to-upscale operations, and `img2pdf>=0.6.3` for lossless PNG-to-PDF assembly. Everything else uses the existing dependency set or Python stdlib. The existing architectural patterns — typed Pydantic models flowing through engine functions, no I/O inside engine modules, API keys checked at call entry, output layer handling all file writes — apply directly and without modification to the new `design` command.

The primary risks are operational, not architectural: Imagen 4 enforces English-only prompts (German slide content must be translated during elaboration), the content filter silently returns zero images rather than raising exceptions, and the deprecated `google-generativeai` package must never be used in favor of `google-genai`. Memory management during 15-slide 4K generation requires write-to-disk-immediately semantics to avoid OOM crashes. All five critical pitfalls have concrete, implementable mitigations that should be built into the architecture from the start, not patched in later.

## Key Findings

### Recommended Stack

The existing stack already covers 80% of what is needed. The only net-new runtime dependencies are `google-genai` (Gemini text + Imagen 4 image generation via a single unified SDK), `Pillow` (image manipulation and upscaling), and `img2pdf` (lossless PDF assembly). Three stdlib modules — `zipfile`, `xml.etree.ElementTree`, and `io.BytesIO` — cover ZIP export, design system XML parsing, and image byte buffering respectively. See `.planning/research/STACK.md` for full version rationale.

**Core technologies:**
- `google-genai>=1.65.0`: Gemini text elaboration + Imagen 4 image generation — the only supported SDK; `google-generativeai` is EOL as of November 2025
- `Pillow>=12.1.0`: Image processing, 2K-to-upscale (LANCZOS), format conversion — de facto standard; already an indirect dependency
- `img2pdf>=0.6.3`: Lossless PNG-to-PDF assembly — preserves 4K fidelity unlike Pillow's PDF writer which re-encodes pixels

**Model selection:**
- Elaboration: `gemini-2.5-flash` (stable, cost-efficient, handles 1000-line XML context)
- Generation: `imagen-4.0-generate-001` (standard quality, production stable)
- Development iteration: `imagen-4.0-fast-generate-001` (faster, lower quality)
- Note: True 4K (3840x2160) is not achievable via the Gemini Developer API; use `imageSize="2K"` and upscale via Pillow LANCZOS

### Expected Features

The `design` command is purely a renderer — it consumes `deck.json` produced by `pitchdeck generate` and produces visual slide images. It has no content generation capability of its own. See `.planning/research/FEATURES.md` for full prioritization matrix.

**Must have (v1 table stakes):**
- `pitchdeck design <deck.json>` command entry point with GEMINI_API_KEY validation at entry
- Design system selection via `--design` flag (choices: `consulting-light`, `training-dark`, `brochure-a4`; default: `consulting-light`)
- Design system XML files loaded as package data (not hardcoded paths)
- Per-slide Gemini Flash elaboration + Imagen 4 generation with `imageSize="2K"`
- Rich progress output showing per-slide status during the 2-5 minute generation run
- PNG output: `slide_01.png` through `slide_15.png` with auto-created output directory
- Continue-on-error: per-slide failures accumulate in a failure list, reported at end
- ZIP export via `--zip` flag (stdlib `zipfile`, no new dependency)
- Brochure A4 auto-maps to `aspect_ratio="3:4"`; all other designs use `"16:9"`

**Should have (v1.x after core validated):**
- PDF assembly (`--pdf` flag, Pillow multi-image PDF)
- Partial resume (`--from-slide N`): skip already-generated PNGs, saves API cost
- Per-slide auto-retry (max 2 retries, 10s backoff) for transient rate limit failures
- Verbose mode (`--verbose`): print elaborated XML prompt before Imagen call
- Dry-run mode (`--dry-run`): run elaboration only, skip Imagen, write XML files

**Defer to v2+:**
- Custom user-provided design systems (arbitrary XML; unvalidatable surface area)
- Logo/watermark overlay (Pillow compositing; per-design-system positioning complexity)
- Parallel async generation (rate limit risk; unnecessary for 15-slide decks)
- PPTX export (heavy dependency; rasterized PNGs lose editability anyway)

### Architecture Approach

The design pipeline integrates as a fourth engine module (`engine/design.py`) alongside the three existing engines, following identical patterns: typed Pydantic models in, typed models out, no I/O inside the engine, API key checked at function entry, errors wrapped as `PitchDeckError` subclasses. New models (`DesignSystemName`, `SlideImage`, `DesignResult`, `DesignError`, `SlideGenerationError`) are added to `models.py`. Output concerns (PNG writing, ZIP assembly, PDF assembly) live in a new `output/slides_output.py` module. Design system XML files are stored in `src/pitchdeck/design_systems/` and loaded via `importlib.resources.files()` for correct pip-install packaging. See `.planning/research/ARCHITECTURE.md` for full component diagram and data flow.

**Major components:**
1. `engine/design.py` — Gemini elaboration + Imagen 4 generation pipeline; returns `DesignResult`; pure computation, no file I/O
2. `design_systems/__init__.py` + XML files — Static design system resources; loader returns raw XML string for Gemini prompt injection
3. `output/slides_output.py` — PNG save, ZIP assembly, PDF assembly; all filesystem writes isolated here
4. `models.py` additions — `DesignSystemName` (Literal type), `SlideImage`, `DesignJob`, `DesignResult`, `DesignError`, `SlideGenerationError`
5. `cli.py` `design()` command — Orchestrates validation, engine call, output, progress reporting; mirrors `validate()` command pattern exactly

**Unchanged:** `narrative.py`, `validator.py`, `gaps.py`, `slides.py`, `markdown.py`, `validation_report.py`, `parsers/`, `profiles/`

### Critical Pitfalls

See `.planning/research/PITFALLS.md` for full detail including warning signs and recovery strategies.

1. **Imagen is English-only via Developer API** — German slide content must be translated to English during Gemini elaboration before any image prompt is constructed. This is a hard architectural constraint: the elaboration step must enforce English output, not a patch applied later. Vertex AI supports German but the project uses AI Studio (`GEMINI_API_KEY`), not Vertex.

2. **Content filter silently returns empty image list** — `response.generated_images` can be an empty list (not an exception) when content policy triggers. Always guard with `if not response.generated_images:` before index access. Set `include_rai_reason=True` in `GenerateImagesConfig` to surface the reason. Business content (financial projections, competitor names, market size claims) triggers filters unexpectedly.

3. **No validation firewall between elaboration and generation** — Gemini may produce prompts exceeding 480 tokens, containing policy triggers, or misinterpreting the design system XML. Without an intermediate check, bad elaborations spend Imagen quota and produce wrong slides silently. Add token count check and prompt validation before each `generate_images()` call.

4. **`google-generativeai` is EOL — use only `google-genai`** — The two packages have nearly identical names. The old package reached EOL November 2025; Imagen 4 model IDs don't resolve through it. Import pattern: `from google import genai`. Annotate this in `pyproject.toml` to prevent future "fixes."

5. **4K PNG memory accumulation crashes CLI mid-deck** — Holding all 15 slide images in memory simultaneously consumes 450-750 MB. Write each PNG to disk immediately after generation, never accumulating `image_bytes` in a list. Use context managers for all Pillow operations.

## Implications for Roadmap

Based on combined research, the design command builds naturally across five phases respecting the data-layer-first, then-logic-then-output ordering of the existing codebase. The pitfall-to-phase mapping from PITFALLS.md and the suggested build order from ARCHITECTURE.md align closely.

### Phase 1: Foundation — Models, Design Systems, SDK Setup

**Rationale:** Data models must exist before any logic can reference them; design system files must be package data before tests can run; correct SDK installed once prevents re-work across all later phases. All critical pitfalls that are "must fix at architecture time" (SDK choice, English-only constraint, design system storage) are resolved here before any API calls are written.
**Delivers:** Typed models in `models.py`, three XML design system files in `src/pitchdeck/design_systems/`, `load_design_system()` loader, `VIZ_HINTS` constant and `_slide_to_folie_format()` pure function, `google-genai` + `Pillow` + `img2pdf` in `pyproject.toml`
**Features addressed:** Design system selection, GEMINI_API_KEY validation pattern, `--design` flag choices
**Pitfalls avoided:** Wrong SDK installation (P4), hardcoded design system XML as Python strings (anti-pattern), design systems not packaged for pip install

### Phase 2: Design Engine — Gemini Elaboration + Imagen Generation

**Rationale:** Core pipeline logic with all critical safety guards built in from the start. Per-slide error isolation must be designed into the engine, not added as a patch. The validation firewall between elaboration and generation must be part of the initial implementation.
**Delivers:** `engine/design.py` with `_elaborate_slide()`, `_generate_image()`, and `generate_slide_images()` (orchestrator); per-slide error isolation with `SlideGenerationError` accumulation; English-only enforcement in elaboration output; prompt token count guard; content filter empty-response guard; `imageSize="2K"` with LANCZOS upscale to 4K; aspect ratio auto-selection by design system
**Features addressed:** Per-slide Gemini elaboration, Imagen 4 generation, continue-on-error, rate limit retry (max 2 retries, 10s backoff)
**Pitfalls avoided:** English-only constraint (P1), no validation firewall (P2), content filter IndexError (P3), 4K memory accumulation (P5)
**Stack used:** `google-genai`, `Pillow`, `io.BytesIO`

### Phase 3: Output Layer — PNG, ZIP, PDF

**Rationale:** Output concerns are entirely separate from engine concerns. The engine returns `DesignResult` with `image_bytes`; the output layer handles all filesystem writes. PDF assembly is v1.x (add after core works) but PNG save and ZIP are v1 table stakes.
**Delivers:** `output/slides_output.py` with `save_slide_images()` (write-immediately semantics), `create_zip()` (stdlib `zipfile`), and `create_pdf()` (Pillow multi-page + `img2pdf` for lossless assembly); output directory auto-creation; file naming convention `slide_01.png`..`slide_15.png`
**Features addressed:** PNG output, ZIP export (`--zip`), PDF assembly (`--pdf`)
**Pitfalls avoided:** Uncompressed PDF size exceeding 100 MB, memory accumulation from loading all slides for ZIP

### Phase 4: CLI Integration

**Rationale:** Wire all components together only after each component is independently tested and verified. CLI command follows the `validate()` pattern exactly.
**Delivers:** `design()` @app.command() in `cli.py`; GEMINI_API_KEY check at command entry (before any API call); `PitchDeck.model_validate_json()` for deck loading; Rich `Progress` with per-slide status (`[X/15] Generating slide N: {title}`); summary output (N succeeded, M failed, file locations); non-zero exit code on partial failure; sensible default output path (`output/<company_name>/slides/`)
**Features addressed:** All v1 table stakes CLI features, verbose mode, dry-run mode
**Pitfalls avoided:** No progress during 10-minute run (UX), GEMINI_API_KEY missing buried in stack trace, exit code 0 on partial failure

### Phase 5: Tests

**Rationale:** Tests validate the complete pipeline with mocked APIs; all test patterns already established in `tests/test_engine.py` and `tests/test_validator.py`. New tests follow identical mocking conventions.
**Delivers:** `tests/test_design.py` (mocked Gemini + Imagen; tests `_slide_to_folie_format()`, elaboration prompt format, English-only enforcement, empty response guard, per-slide error isolation); `tests/test_slides_output.py` (file naming, ZIP contents, PDF page count); `tests/test_cli_design.py` (integration test with mocked engine; GEMINI_API_KEY missing error; partial failure exit code)
**Features addressed:** All acceptance criteria validation
**Pitfalls avoided:** All "Looks Done But Isn't" checklist items from PITFALLS.md

### Phase Ordering Rationale

- Phase 1 before Phase 2: models must be importable before engine code compiles; correct SDK installed before any imports attempted; design system XML must be loadable from package before the engine test suite runs
- Phase 2 before Phase 3: engine returns `image_bytes` in `DesignResult`; output layer depends on this contract being defined
- Phase 3 before Phase 4: CLI cannot call output functions that don't exist; output functions must be independently tested before wiring
- Phase 4 before Phase 5: integration tests for the CLI command require the full pipeline to be assembled
- This ordering also matches the pitfall prevention phases from PITFALLS.md exactly: Phase 1 prevents SDK and design system pitfalls, Phase 2 prevents generation loop pitfalls, Phase 3 prevents output size pitfalls

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Design Engine):** Gemini elaboration prompt engineering for design system XML injection is experimental — the quality of elaborated prompts heavily determines image output quality. The VIZ_HINTS dict in the prototype covers only some slide types and may need extension for full 15-slide coverage. Token counting before prompt submission needs verification against actual `google-genai` SDK APIs (no `count_tokens()` method confirmed yet).
- **Phase 3 (Output Layer):** PDF assembly using `img2pdf` vs Pillow multi-image PDF has performance implications at 4K resolution that need empirical verification. The 100 MB PDF size target requires testing with actual Imagen 4 output (not mockable).

Phases with standard patterns (no additional research needed):
- **Phase 1 (Foundation):** Pydantic models, `importlib.resources` loading, and XML file extraction are fully documented standard Python patterns.
- **Phase 4 (CLI Integration):** The `validate()` command pattern is already established in the codebase and maps directly to `design()`.
- **Phase 5 (Tests):** Mock patterns for both Anthropic and Google SDKs are well-documented; existing test structure provides the template.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions confirmed against PyPI; API patterns verified from working `generate_slides.py` prototype; no version conflicts expected |
| Features | HIGH (core), MEDIUM (resolution) | Core pipeline features are validated by working prototype; 4K resolution claim in PROJECT.md is incorrect — Imagen 4 API max is 2K; `output_mime_type="image/png"` behavior unconfirmed by official docs (prototype uses it but docs may limit to JPEG) |
| Architecture | HIGH | NW Slide AI reference implementation available in `/tmp/nw-slide-ai/`; full existing codebase analyzed; component boundaries follow established patterns |
| Pitfalls | HIGH | Critical pitfalls sourced from official Google AI docs, verified SDK issue trackers, and Pillow memory issue history; English-only constraint is documented API behavior |

**Overall confidence:** HIGH

### Gaps to Address

- **Imagen API output_mime_type:** Official docs may limit `output_mime_type` to `image/jpeg` — the prototype uses `image/png` but this needs verification in Phase 2. If PNG is unavailable, save JPEG at quality 95+ and document. This does not change architecture; only the file extension and save call.
- **Gemini elaboration English-only enforcement mechanism:** Research confirms the constraint exists but the exact prompt engineering pattern to guarantee English output from Gemini (when given German slide content) needs implementation-time validation. A system prompt instruction ("respond in English only") combined with the design system context should suffice but needs smoke testing.
- **VIZ_HINTS completeness:** The prototype's `VIZ_HINTS` dict covers the slide types present in the test deck but may be missing types for all 15 `SLIDE_TEMPLATES` entries in `engine/slides.py`. This gap is addressable by comparing the two dictionaries during Phase 1 implementation.
- **Gemini `thinking_budget` parameter availability:** The reference implementation uses `thinking_budget=2000` in `GenerateContentConfig`. This is a Gemini 2.5 Flash Thinking feature — verify it is available in the non-thinking `gemini-2.5-flash` model or switch to the thinking variant.
- **Imagen 4 daily quota limits:** Free tier limits (approximately 5-20 requests/day) affect development and testing. Phase 2 and testing phases should use `imagen-4.0-fast-generate-001` to conserve quota, switching to standard model for acceptance testing.

## Sources

### Primary (HIGH confidence)
- PyPI `google-genai` 1.65.0 — version, import patterns, `GenerateImagesConfig` API
- Google AI Docs (ai.google.dev) — Imagen 4 model names, aspect ratios, imageSize options, English-only restriction
- Google AI Docs (ai.google.dev) — `gemini-2.5-flash` as stable production model
- PyPI `Pillow` 12.1.1 — version, LANCZOS resampling, multi-image PDF save
- PyPI `img2pdf` 0.6.3 — lossless PNG-to-PDF assembly
- Vertex AI Docs — German language support is Vertex-only (not Developer API)
- `/root/projects/capital/generate_slides.py` — working prototype (primary implementation reference)
- `/tmp/nw-slide-ai/` — NW Slide AI reference implementation (App.tsx, geminiService.ts, constants.tsx)
- Existing codebase (`.planning/codebase/`) — architecture, structure, integration patterns

### Secondary (MEDIUM confidence)
- Google Developers Blog — Imagen 4 family GA announcement; model availability confirmation
- google-genai GitHub issues — SDK behavior edge cases (model not found errors)
- Pillow GitHub issues #3610, #5797, #6448 — memory leak documentation

### Tertiary (LOW confidence — needs implementation validation)
- `output_mime_type="image/png"` support in `GenerateImagesConfig` — used in prototype but not confirmed in current official API reference
- `thinking_budget` parameter availability in `gemini-2.5-flash` (non-thinking variant)

---
*Research completed: 2026-02-26*
*Ready for roadmap: yes*
