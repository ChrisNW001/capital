# Architecture Research

**Domain:** Visual slide generation pipeline integrated into existing Python pitchdeck CLI
**Researched:** 2026-02-26
**Confidence:** HIGH — existing codebase fully analyzed; reference implementation (NW Slide AI) available in /tmp/nw-slide-ai; Gemini/Imagen API patterns verified from generate_slides.py

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                          CLI Layer (cli.py)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │ generate │  │ validate │  │ profiles │  │       design         │ │
│  └────┬─────┘  └──────────┘  └──────────┘  └──────────┬───────────┘ │
├───────┼────────────────────────────────────────────────┼─────────────┤
│       │        Content Engine (existing)               │ Design Engine (new)  │
│  ┌────┴──────────────────────────────────┐  ┌──────────┴──────────────────┐ │
│  │  narrative.py  gaps.py  validator.py  │  │  engine/design.py (NEW)     │ │
│  └────┬──────────────────────────────────┘  └──────────┬──────────────────┘ │
├───────┼────────────────────────────────────────────────┼─────────────┤
│       │         Output Layer                           │             │
│  ┌────┴─────────────────┐  ┌─────────────────────────┐ │             │
│  │ markdown.py          │  │ output/slides.py (NEW)  │◄┘             │
│  │ validation_report.py │  │ output/export.py (NEW)  │               │
│  └──────────────────────┘  └─────────────────────────┘               │
├──────────────────────────────────────────────────────────────────────┤
│                          Models Layer (models.py)                    │
│  ┌────────────┐  ┌──────────────────┐  ┌────────────────────────┐   │
│  │ PitchDeck  │  │ SlideContent     │  │ DesignJob + SlideImage │   │
│  │ (existing) │  │ (existing)       │  │ (NEW additions)        │   │
│  └────────────┘  └──────────────────┘  └────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────┤
│                    External APIs                                      │
│  ┌──────────────────────┐       ┌────────────────────────────────┐   │
│  │  Anthropic Claude    │       │  Google Gemini + Imagen 4      │   │
│  │  (generation/valid.) │       │  (elaboration + image gen)     │   │
│  └──────────────────────┘       └────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────┤
│                    Static Resources                                   │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  design_systems/                                               │   │
│  │    consulting_light.xml   training_dark.xml   brochure_a4.xml  │   │
│  └────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | New or Existing |
|-----------|---------------|-----------------|
| `cli.py` — `design` command | Orchestrate design pipeline: load deck JSON, select design system, call engine, report progress | Modified (add command) |
| `engine/design.py` | Transform SlideContent → #Folie format → call Gemini → call Imagen 4 → return SlideImage list | New |
| `output/slides.py` | Save PNG files, assemble ZIP, assemble PDF | New |
| `models.py` — `DesignJob`, `SlideImage`, `DesignSystemName` | Typed data shapes for design pipeline inputs and outputs | Modified (add models) |
| `design_systems/` | Static XML files for each design system, loaded at runtime | New directory |
| `profiles/loader.py` | Unchanged — no design system data lives in VC profiles | Unchanged |

---

## Recommended Project Structure

```
src/pitchdeck/
├── cli.py                          # Add: design() @app.command()
├── models.py                       # Add: DesignSystemName, SlideImage, DesignJob, DesignResult
├── engine/
│   ├── narrative.py                # Unchanged
│   ├── validator.py                # Unchanged
│   ├── gaps.py                     # Unchanged
│   ├── slides.py                   # Unchanged
│   └── design.py                   # NEW: Gemini elaboration + Imagen 4 generation pipeline
├── output/
│   ├── markdown.py                 # Unchanged
│   ├── validation_report.py        # Unchanged
│   └── slides_output.py            # NEW: PNG save, ZIP assembly, PDF assembly
└── design_systems/                 # NEW: Static XML design system files
    ├── __init__.py                 # loader: load_design_system(name) -> str
    ├── consulting_light.xml        # Ported from NW Slide AI CONSULTING_LIGHT_DESIGN_SYSTEM
    ├── training_dark.xml           # Ported from NW Slide AI TRAINING_DARK_DESIGN_SYSTEM
    └── brochure_a4.xml             # Ported from NW Slide AI BROCHURE_A4_DESIGN_SYSTEM

design_systems/                     # Alternative: top-level alongside profiles/
                                    # (see rationale below — src/pitchdeck/ preferred)
```

### Structure Rationale

- **`engine/design.py`:** Follows existing pattern — each engine module takes typed model args, returns typed models. Pure logic, no I/O. Parallel to `narrative.py` in structure: API key checked at call time, errors wrapped as `PitchDeckError`.
- **`output/slides_output.py`:** Follows existing pattern — `output/` contains only renderers, no business logic. PNG save, ZIP assembly, PDF are rendering concerns not engine concerns.
- **`design_systems/` inside `src/pitchdeck/`:** Keeps design system files as importable package resources (accessible via `importlib.resources` or direct path). Makes packaging correct — `pip install` includes them. Avoids brittle relative path discovery. Alternative is top-level like `profiles/`, but `profiles/` are user-editable data while design systems are read-only package resources.
- **`design_systems/__init__.py` with `load_design_system(name)`:** Centralizes loading logic. Validates names early. Pattern mirrors `profiles/loader.py`.

---

## Architectural Patterns

### Pattern 1: Engine Function Takes Typed Args, Returns Typed Models

This is the established pattern in the codebase. `design.py` should follow it exactly.

**What:** Engine functions receive Pydantic models as input, return Pydantic models as output. No I/O inside engine functions. API key checked at function entry.

**When to use:** Any time business logic calls an external API or transforms data.

**Example:**
```python
# src/pitchdeck/engine/design.py

def generate_slide_images(
    deck: PitchDeck,
    design_system_name: DesignSystemName,
    viz_hints: dict[str, str] | None = None,
) -> DesignResult:
    """Generate 4K slide images for every slide in a PitchDeck.

    Raises PitchDeckError for all API and configuration failures.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise PitchDeckError(
            "GEMINI_API_KEY environment variable not set. "
            "Get your key at https://aistudio.google.com/"
        )

    design_xml = load_design_system(design_system_name)
    client = genai.Client(api_key=api_key)

    images: list[SlideImage] = []
    for slide in deck.slides:
        description = _slide_to_folie_format(slide, viz_hints)
        xml_prompt = _elaborate_slide(client, description, design_xml, slide.slide_number)
        image_bytes = _generate_image(client, xml_prompt, design_system_name)
        images.append(SlideImage(
            slide_number=slide.slide_number,
            slide_type=slide.slide_type,
            image_bytes=image_bytes,
            xml_prompt=xml_prompt,
        ))

    return DesignResult(
        company_name=deck.company_name,
        design_system=design_system_name,
        generated_at=datetime.now().isoformat(),
        slides=images,
    )
```

### Pattern 2: Neurawork #Folie Format Transformation

**What:** `SlideContent` (PitchDeck model) is transformed into the `#Folie[Nr]` text format that Gemini understands, with visualization hints appended. This is a pure string transformation, no API calls.

**When to use:** Between deck loading and Gemini elaboration. Isolate as private function `_slide_to_folie_format()`.

**Trade-offs:** The VIZ_HINTS dict in `generate_slides.py` is currently hardcoded per slide type. Port it verbatim as a module-level constant `VIZ_HINTS: dict[str, str]` in `engine/design.py`. It can later be made configurable per design system or VC profile.

**Example:**
```python
# Mirrors generate_slides.py::slide_to_description() exactly

VIZ_HINTS: dict[str, str] = {
    "cover": "Visualization: Dark navy background (#0A2540), ...",
    "problem": "Visualization: White background, bold headline...",
    # ... all 15 slide types
}

def _slide_to_folie_format(
    slide: SlideContent,
    viz_hints: dict[str, str] | None = None
) -> str:
    hints = viz_hints or VIZ_HINTS
    parts = [
        f"#Folie{slide.slide_number}: {slide.title}",
        f"Typ: {slide.slide_type}",
        f"Headline: {slide.headline}",
    ]
    if slide.bullets:
        parts.append("\nInhalt:")
        parts.extend(f"- {b}" for b in slide.bullets)
    if slide.metrics:
        parts.append("\nKennzahlen:")
        parts.extend(f"- {m}" for m in slide.metrics)
    viz = hints.get(slide.slide_type, "")
    if viz:
        parts.append(f"\n{viz}")
    return "\n".join(parts)
```

### Pattern 3: Design System as Loadable Static Resource

**What:** Each design system is a separate XML file stored in `src/pitchdeck/design_systems/`. A loader function reads them by name and returns the raw XML string for inclusion in Gemini prompts.

**When to use:** At the start of each `generate_slide_images()` call. Cache in memory if multiple slides in same run (no repeated disk reads).

**Trade-offs:** XML files are ~1000 lines each (~30KB). Reading all three at startup is fine; reading on demand per call is also fine. Keep them as plain text files (not parsed XML) — Gemini receives the full XML string as a prompt ingredient, not a parsed structure.

**Example:**
```python
# src/pitchdeck/design_systems/__init__.py

from importlib.resources import files
from pitchdeck.models import DesignSystemName, PitchDeckError

_DESIGN_SYSTEM_FILES: dict[str, str] = {
    "consulting-light": "consulting_light.xml",
    "training-dark": "training_dark.xml",
    "brochure-a4": "brochure_a4.xml",
}

def load_design_system(name: DesignSystemName) -> str:
    """Load design system XML by name. Returns full XML string."""
    filename = _DESIGN_SYSTEM_FILES.get(name)
    if not filename:
        raise PitchDeckError(
            f"Unknown design system '{name}'. "
            f"Available: {list(_DESIGN_SYSTEM_FILES.keys())}"
        )
    resource = files("pitchdeck.design_systems").joinpath(filename)
    return resource.read_text(encoding="utf-8")
```

---

## Data Flow

### Design Pipeline: `pitchdeck design deck.json --design consulting-light`

```
User: pitchdeck design deck.json --design consulting-light --output slides/
    |
    v
CLI: design() command
    - Check GEMINI_API_KEY env var
    - Load deck.json → PitchDeck.model_validate_json()
    - Validate design system name (Literal)
    - Call engine/design.py: generate_slide_images(deck, design_system_name)
    |
    v
engine/design.py: generate_slide_images()
    - load_design_system("consulting-light") → XML string (~30KB)
    - Init google.genai.Client(api_key=...)
    - For each SlideContent in PitchDeck.slides:
        |
        v
        _slide_to_folie_format(slide, VIZ_HINTS) → #Folie text string
        |
        v
        _elaborate_slide(client, description, design_xml, slide_number)
          - Gemini API: gemini-2.5-flash with thinking_budget=2000
          - Returns: XML ImageSpecification string
          - Strip markdown fences from response
        |
        v
        _generate_image(client, xml_prompt, design_system_name)
          - Imagen API: imagen-4.0-generate-001
          - aspect_ratio: "16:9" (consulting-light, training-dark) or "3:4" (brochure-a4)
          - Returns: raw PNG bytes
        |
        v
        SlideImage(slide_number, slide_type, image_bytes, xml_prompt)
    |
    v
    Return DesignResult(company_name, design_system, generated_at, slides=[SlideImage...])
    |
    v
CLI: receives DesignResult
    - Call output/slides_output.py: save_slide_images(result, output_dir)
        - Create output_dir if not exists
        - Write slide_01.png ... slide_15.png
    - Call output/slides_output.py: create_zip(result, zip_path)
        - JSZip equivalent: zipfile.ZipFile with all PNGs
    - Call output/slides_output.py: create_pdf(result, pdf_path) [optional --pdf flag]
        - reportlab or fpdf2: one PNG per page, A4 or 16:9 dimensions
    - Print progress and file locations via Rich
```

### Key Data Flows

1. **PitchDeck → DesignResult:** `PitchDeck.slides` (List[SlideContent]) flows into the engine; each `SlideContent` becomes a `SlideImage`; result is `DesignResult` with same length list.

2. **Design System Selection → Aspect Ratio:** The `DesignSystemName` literal controls both which XML is loaded AND what `aspect_ratio` is passed to Imagen. `brochure-a4` uses `"3:4"`, all others use `"16:9"`. This logic lives in `engine/design.py`, not in `output/`.

3. **GEMINI_API_KEY pattern:** Mirrors `ANTHROPIC_API_KEY` pattern exactly — checked at engine function entry, never at CLI level (only CLI checks existence and prints hint; engine raises `PitchDeckError` if missing).

---

## New Models (additions to models.py)

Following existing patterns: `List[X]` from typing, `Field(default_factory=list)`, `Literal` for constrained strings.

```python
# Add to src/pitchdeck/models.py

DesignSystemName = Literal["consulting-light", "training-dark", "brochure-a4"]


class SlideImage(BaseModel):
    """Generated image for a single slide."""
    slide_number: int
    slide_type: str
    image_bytes: bytes
    xml_prompt: str = ""          # The elaborated XML prompt used for generation
    error: Optional[str] = None   # Set if generation failed for this slide


class DesignJob(BaseModel):
    """Input specification for a design run."""
    deck_path: str
    design_system: DesignSystemName
    output_dir: str
    create_zip: bool = True
    create_pdf: bool = False


class DesignResult(BaseModel):
    """Output of the full design pipeline."""
    company_name: str
    design_system: DesignSystemName
    generated_at: str
    slides: List[SlideImage]
    failed_slides: List[int] = Field(default_factory=list)

    @computed_field
    @property
    def success_count(self) -> int:
        return sum(1 for s in self.slides if s.error is None)

    @computed_field
    @property
    def failed_count(self) -> int:
        return len(self.failed_slides)
```

Note: `image_bytes: bytes` works in Pydantic v2 but is not serializable via `model_dump_json()`. This is intentional — `DesignResult` is transient (CLI → output layer), not saved to disk as JSON. PNG bytes go directly to files.

---

## New Error Types (additions to models.py)

```python
class DesignError(PitchDeckError):
    """Raised when visual slide generation fails."""
    pass

class SlideGenerationError(DesignError):
    """Raised when a single slide fails to generate (non-fatal — others continue)."""
    def __init__(self, slide_number: int, reason: str):
        self.slide_number = slide_number
        self.reason = reason
        super().__init__(f"Slide {slide_number} generation failed: {reason}")
```

Single-slide failures are non-fatal: the pipeline continues, failed slide numbers are collected in `DesignResult.failed_slides`, and the CLI reports partial success. This differs from the content generation pipeline where any failure aborts entirely.

---

## Design System Storage

**Decision: Port XML out of constants.tsx into standalone .xml files.**

The NW Slide AI reference stores all three design systems as TypeScript template literals in `constants.tsx` (3045 lines total). For the Python CLI:

- Extract each design system's XML block into its own file
- Store as UTF-8 text files in `src/pitchdeck/design_systems/`
- Load via `importlib.resources.files()` to work correctly after `pip install`
- Do NOT parse or process the XML — pass raw text directly to Gemini prompts

**Extraction pattern:** The XML for each system starts immediately after the backtick in `export const X_DESIGN_SYSTEM = \`` and ends at the closing `\``. See constants.tsx lines 1, 1255, 2222.

**File sizes (approximate):**
- `consulting_light.xml`: ~1254 lines, ~35KB
- `training_dark.xml`: ~967 lines, ~28KB
- `brochure_a4.xml`: ~823 lines, ~25KB

**Aspect ratios by design system:**
- `consulting-light`: 16:9 landscape (3840x2160)
- `training-dark`: 16:9 landscape (3840x2160)
- `brochure-a4`: 3:4 portrait (mapped to 3072x4096 per PROJECT.md constraints)

---

## Integration Points with Existing Code

### What is Unchanged

| Existing Component | Why Unchanged |
|-------------------|---------------|
| `models.py` — PitchDeck, SlideContent | Design pipeline reads PitchDeck.slides; no modification needed |
| `engine/narrative.py` | Content generation is complete before design runs |
| `engine/validator.py` | Validation is independent of visual generation |
| `engine/gaps.py` | Gap detection is a content-generation concern |
| `engine/slides.py` | SLIDE_TEMPLATES unchanged; VIZ_HINTS in design.py covers the visual mapping |
| `output/markdown.py` | Markdown output unchanged |
| `profiles/loader.py` | VC profiles don't contain design system data |
| `parsers/` | Document parsing unchanged |

### What is Modified

| Existing Component | Modification |
|-------------------|--------------|
| `cli.py` | Add `design()` @app.command() following validate() command pattern |
| `models.py` | Add DesignSystemName, SlideImage, DesignJob, DesignResult, DesignError, SlideGenerationError |
| `pyproject.toml` | Add google-genai, Pillow (image handling), fpdf2 or reportlab (PDF) |

### What is Added New

| New Component | Purpose |
|--------------|---------|
| `engine/design.py` | Full Gemini elaboration + Imagen 4 generation pipeline |
| `output/slides_output.py` | PNG save, ZIP assembly, PDF assembly |
| `design_systems/__init__.py` | Design system loader with name validation |
| `design_systems/consulting_light.xml` | Ported from NW Slide AI |
| `design_systems/training_dark.xml` | Ported from NW Slide AI |
| `design_systems/brochure_a4.xml` | Ported from NW Slide AI |
| `tests/test_design.py` | Unit tests for design engine; mock all Gemini/Imagen calls |
| `tests/test_slides_output.py` | Tests for PNG/ZIP/PDF output functions |

---

## CLI Command Design

The `design` command mirrors the `validate` command pattern:

```python
@app.command()
def design(
    deck_file: Annotated[
        str,
        typer.Argument(help="Path to deck JSON file (output of 'pitchdeck generate')"),
    ],
    design_system: Annotated[
        str,
        typer.Option("--design", "-d", help="Design system: consulting-light, training-dark, brochure-a4"),
    ] = "consulting-light",
    output_dir: Annotated[
        str,
        typer.Option("--output", "-o", help="Output directory for slide PNGs"),
    ] = "slides/",
    create_zip: Annotated[
        bool,
        typer.Option("--zip/--no-zip", help="Create ZIP archive of all slides"),
    ] = True,
    create_pdf: Annotated[
        bool,
        typer.Option("--pdf", help="Assemble slides into a PDF"),
    ] = False,
):
    """Generate 4K visual slides from a pitch deck JSON file."""
```

Progress reporting: use Rich `Progress` with `SpinnerColumn` + slide counter. Each slide's Gemini elaboration and Imagen call should be reported individually (not just a single spinner for the whole deck). Pattern: `[X/15] Generating slide N: {slide.title[:40]}`.

---

## Suggested Build Order

Build order respects dependencies: lower layers before higher, data models before logic that uses them.

### Phase 1: Foundation (no external API calls)

1. **Add models to `models.py`** — `DesignSystemName`, `SlideImage`, `DesignResult`, `DesignError`, `SlideGenerationError`
   - Enables all downstream code to import types
   - No new dependencies

2. **Port and store design system XML files** — Extract from `constants.tsx`, write as `src/pitchdeck/design_systems/*.xml`
   - Pure file operation, no code
   - Write `design_systems/__init__.py` with `load_design_system()` loader

3. **Implement `_slide_to_folie_format()`** in `engine/design.py` — Port from `generate_slides.py::slide_to_description()`
   - Pure function, no API calls, immediately testable
   - Port `VIZ_HINTS` dict as module constant

### Phase 2: Engine (mocked in tests, real API in integration)

4. **Implement `_elaborate_slide()`** — Gemini API call pattern (mirrors `_parse_deck_response()` from narrative.py)
   - Add `google-genai` to pyproject.toml dependencies
   - Handle Gemini error types the same way Anthropic errors are handled

5. **Implement `_generate_image()`** — Imagen 4 API call; returns `bytes`
   - Aspect ratio selection based on `DesignSystemName`
   - Return raw PNG bytes; no file I/O in engine

6. **Implement `generate_slide_images()`** — Orchestrate the pipeline; collect `SlideImage` instances; non-fatal per-slide failure handling

### Phase 3: Output

7. **Implement `output/slides_output.py`** — `save_slide_images()`, `create_zip()`, `create_pdf()`
   - Add `Pillow` and `fpdf2` (or `reportlab`) to pyproject.toml
   - `save_slide_images()`: write `slide_{n:02d}.png` files from `DesignResult.slides`
   - `create_zip()`: `zipfile.ZipFile` — simpler than JSZip equivalent, stdlib only
   - `create_pdf()`: one image per page, appropriate page size

### Phase 4: CLI Integration

8. **Add `design()` command to `cli.py`** — Wire all components together
   - Check `GEMINI_API_KEY` early; print hint if missing
   - Load `PitchDeck` from JSON (same pattern as `validate` command)
   - Validate `design_system` name; map string to `DesignSystemName` Literal
   - Call engine, then output layer
   - Report per-slide progress; show summary (N succeeded, M failed)

### Phase 5: Tests

9. **Write `tests/test_design.py`** — Mock `google.genai.Client`; test `_slide_to_folie_format()`, format of Gemini prompt, PNG byte handling
10. **Write `tests/test_slides_output.py`** — Test file naming, ZIP contents, PDF page count
11. **Write `tests/test_cli_design.py`** — Integration test for design command with mocked engine

---

## Anti-Patterns

### Anti-Pattern 1: Embedding XML Design Systems as Python Strings

**What people do:** Keep the XML content as Python string constants in a `.py` file (mirroring the TypeScript constants.tsx).

**Why it's wrong:** 3000+ lines of XML in Python modules makes the codebase noisy, hurts readability, and couples content changes to Python module reloads. The XML is not Python — it should not live in Python.

**Do this instead:** Store as `.xml` files in `design_systems/`, load via `importlib.resources`. Packaging picks them up via `hatchling` build config.

### Anti-Pattern 2: File I/O Inside Engine Functions

**What people do:** Save PNGs directly from `_generate_image()` or `generate_slide_images()`.

**Why it's wrong:** Breaks the existing architectural pattern where engine modules contain no I/O. Makes testing harder (must mock filesystem). Prevents the CLI from controlling output paths.

**Do this instead:** Engine returns `bytes` (in `SlideImage.image_bytes`); `output/slides_output.py` handles all file writing. Engine is pure computation.

### Anti-Pattern 3: Aborting on First Slide Failure

**What people do:** Let a single Imagen API failure raise an exception and abort the entire run.

**Why it's wrong:** Imagen 4 has known rate limits and occasional transient failures. A 15-slide deck failing at slide 12 and losing all progress is terrible UX.

**Do this instead:** Catch `SlideGenerationError` per slide, store the failure in `DesignResult.failed_slides`, continue to next slide. Report partial success. Optionally add a `--fail-fast` flag for users who want strict behavior.

### Anti-Pattern 4: Re-Parsing PitchDeck JSON Inside engine/design.py

**What people do:** Accept a file path in the engine function and parse JSON there.

**Why it's wrong:** The CLI's job is to validate inputs and pass typed models to engines. Engine functions receive typed models, not file paths. This matches every other engine function in the codebase.

**Do this instead:** CLI loads and validates `PitchDeck` from JSON (same as `validate` command), then passes the typed model to `generate_slide_images(deck, ...)`.

### Anti-Pattern 5: Hardcoding Gemini Model Name

**What people do:** Hardcode `"gemini-2.5-flash"` and `"imagen-4.0-generate-001"` as string literals deep in function calls.

**Why it's wrong:** The existing codebase already has a known tech debt issue: Claude model names hardcoded in narrative.py and validator.py. Do not repeat this.

**Do this instead:** Define module-level constants in `engine/design.py`:
```python
GEMINI_ELABORATION_MODEL = "gemini-2.5-flash"
IMAGEN_GENERATION_MODEL = "imagen-4.0-generate-001"
```
This makes model updates a one-line change and is consistent with how SLIDE_TEMPLATES and SCORING_DIMENSIONS are handled.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Google Gemini API | `google.genai.Client(api_key=...).models.generate_content()` | Use `thinking_budget: 2000` as in reference impl. Model: `gemini-2.5-flash`. Strip markdown fences from response text. |
| Imagen 4 API | `client.models.generate_images()` with `aspect_ratio`, `output_mime_type: "image/png"` | Returns `response.generated_images[0].image.image_bytes` (raw bytes). Handle `"Requested entity was not found"` → KEY_RESET_REQUIRED pattern from geminiService.ts. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| CLI → engine/design.py | Direct function call: `generate_slide_images(deck: PitchDeck, design_system: DesignSystemName)` | Same pattern as `generate_deck()` and `validate_deck()` |
| engine/design.py → design_systems/ | `load_design_system(name)` → returns XML string | Called once per pipeline run; result passed per-slide to Gemini |
| engine/design.py → output/slides_output.py | No direct call — CLI orchestrates both | Engine returns `DesignResult`; CLI passes to output functions |
| CLI → output/slides_output.py | `save_slide_images(result, dir)`, `create_zip(result, path)`, `create_pdf(result, path)` | All output to filesystem is in output layer |

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1-15 slides (typical deck) | Sequential processing is correct. No parallelism needed. Gemini + Imagen calls are fast enough. |
| 30+ slides | Still sequential, but add `--resume` flag to skip already-generated PNGs (check `slide_{n:02d}.png` exists before calling API). |
| Multiple decks batch | Out of scope for v1.1. Shell loop (`for f in *.json; do pitchdeck design $f; done`) is the workaround. |

### Scaling Priorities

1. **First bottleneck:** Imagen 4 rate limits. Mitigation: catch rate limit errors, add `time.sleep(retry_after)` between retries. Keep retry logic in `_generate_image()`.
2. **Second bottleneck:** Large deck with many slides (30+) taking 10+ minutes. Mitigation: resume from checkpoint (`--resume` flag in Phase 2).

---

## Sources

- NW Slide AI reference implementation: `/tmp/nw-slide-ai/` (App.tsx, geminiService.ts, constants.tsx, types.ts)
- Existing codebase: `.planning/codebase/ARCHITECTURE.md`, `STRUCTURE.md`, `INTEGRATIONS.md`
- Reference script: `/root/projects/capital/generate_slides.py` (working Gemini+Imagen pipeline in Python)
- PROJECT.md: `/root/projects/capital/.planning/PROJECT.md` (design system constraints, output resolutions)
- google-genai Python SDK: Verified via `generate_slides.py` usage (`google.genai.Client`, `client.models.generate_content`, `client.models.generate_images`)
- Pydantic v2 docs: `bytes` fields supported, not JSON-serializable by default (acceptable for transient DesignResult)

---

*Architecture research for: Visual slide generation pipeline (pitchdeck v1.1)*
*Researched: 2026-02-26*
