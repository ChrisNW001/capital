# Stack Research

**Domain:** Visual slide generation — Gemini/Imagen pipeline additions to existing Python CLI pitchdeck tool
**Researched:** 2026-02-26
**Confidence:** HIGH (all versions verified against PyPI and official Google AI docs)

## Context: What Already Exists (Do NOT Re-Add)

The following are already in `pyproject.toml` and cover their domains fully:

| Existing Dep | Version | Covers |
|---|---|---|
| `anthropic` | >=0.82.0 | Claude API — content generation and validation |
| `typer[all]` | >=0.24.0 | CLI framework + Rich console output |
| `pydantic` | >=2.0 | All data models |
| `python-dotenv` | >=1.0 | `.env` loading for API keys (GEMINI_API_KEY slots in here) |
| `ruamel.yaml` | >=0.19 | YAML parsing (VC profiles) |
| `pymupdf` / `pymupdf4llm` | current | PDF/DOCX reading |
| `python-docx` | >=1.2.0 | DOCX parsing |
| `questionary` | >=2.0 | Interactive gap-filling prompts |

XML parsing for design systems uses Python's built-in `xml.etree.ElementTree` — no new dependency needed for 1000-line XML files that fit comfortably in memory.

---

## New Dependencies Required

### Core Technologies

| Technology | Version Constraint | Purpose | Why Recommended |
|---|---|---|---|
| `google-genai` | `>=1.65.0` | Gemini text elaboration + Imagen 4 image generation | Official Google Python SDK; single package covers both Gemini text and Imagen APIs; current stable release is 1.65.0 (released 2026-02-26); replaces deprecated `google-generativeai` |
| `Pillow` | `>=12.1.0` | Image processing, resizing, format conversion, and multi-page PDF assembly | De facto standard for Python image handling; version 12.1.1 is current stable; natively saves multi-image PDFs via `save(..., save_all=True, append_images=[...])`; already an indirect dep of pymupdf |
| `img2pdf` | `>=0.6.3` | Lossless PNG/JPEG → PDF assembly | Where Pillow re-encodes pixels on PDF save, img2pdf embeds image bytes directly into the PDF container without re-compression; preserves 4K fidelity; fast; version 0.6.3 is current stable |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---|---|---|---|
| `zipfile` (stdlib) | built-in | ZIP export of slide image set | Always — no dependency needed; `zipfile.ZipFile` in write mode assembles images into a ZIP archive |
| `xml.etree.ElementTree` (stdlib) | built-in | Parse 3 XML design system files | Always — design system XMLs are ~1000 lines each; `ET.parse()` loads entire tree into memory without issue; full XPath subset available for attribute/element queries |
| `io.BytesIO` (stdlib) | built-in | Buffer Imagen API image bytes before writing to disk | Always — Imagen returns `image.image_bytes`; wrap in BytesIO before Pillow `Image.open()` |

### Development Tools

| Tool | Purpose | Notes |
|---|---|---|
| `pytest-mock` (already via pytest patterns) | Mock `google-genai` client calls in tests | Follow same pattern as existing `anthropic` mocking in `tests/test_engine.py` and `tests/test_validator.py`; mock `client.models.generate_images` and `client.models.generate_content` |

---

## Model Selection

### Gemini Text Model (prompt elaboration step)

**Recommended:** `gemini-2.5-flash`

Use for the prompt elaboration step (converting deck slide content + XML design system template into a detailed Imagen prompt). Gemini 2.5 Flash is stable (non-preview), fast, cost-efficient, and handles structured reasoning over ~1000-line XML context. Gemini 2.5 Pro is overkill for prompt expansion and adds latency + cost.

**Do NOT use:** `gemini-3.1-flash-image-preview` or `gemini-3.1-pro` — these are preview/experimental as of 2026-02-26. The NW Slide AI reference uses a Gemini Pro model for elaboration; `gemini-2.5-flash` is the production-stable equivalent.

### Imagen 4 Model (image generation step)

**Recommended:** `imagen-4.0-generate-001`

Standard Imagen 4 model. Produces 1K (default) or 2K images. For 16:9 slides use `aspectRatio="16:9"`; for A4 brochure use `aspectRatio="3:4"`.

**Resolution reality check:** Imagen 4 API exposes `1K` and `2K` as `imageSize` options, not 4K. The PROJECT.md target of "4K (3840x2160)" is NOT directly achievable via the Imagen 4 API without post-processing. Mitigation: generate at `2K` via API, then use Pillow's `Image.resize()` with `LANCZOS` resampling to upscale to 3840x2160 for 16:9 or 3072x4096 for A4. This matches industry practice for AI-generated slide upscaling.

**Ultra model (`imagen-4.0-ultra-generate-001`):** Higher fidelity but slower and more expensive. Reserve for final production export, not development iteration.

**Fast model (`imagen-4.0-fast-generate-001`):** Use during development and testing loops; faster generation at lower fidelity.

---

## API Integration Patterns

### Gemini Client Initialization

```python
from google import genai

# Client picks up GEMINI_API_KEY from environment automatically
# (python-dotenv already loads .env at CLI startup)
client = genai.Client()
```

The `google-genai` SDK reads `GEMINI_API_KEY` from environment automatically — consistent with how `anthropic` SDK reads `ANTHROPIC_API_KEY`. No extra wiring needed beyond adding `GEMINI_API_KEY` to `.env`.

### Imagen Image Generation

```python
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

response = client.models.generate_images(
    model='imagen-4.0-generate-001',
    prompt=elaborated_prompt,
    config=types.GenerateImagesConfig(
        number_of_images=1,
        aspect_ratio="16:9",   # "16:9" for standard slides, "3:4" for A4
        image_size="2K",       # "1K" or "2K"; upscale to 4K in post via Pillow
        output_mime_type="image/png",
    ),
)

image_bytes = response.generated_images[0].image.image_bytes
img = Image.open(BytesIO(image_bytes))
# Upscale to target resolution
img_4k = img.resize((3840, 2160), Image.LANCZOS)
img_4k.save(output_path, format="PNG")
```

### Multi-Page PDF Assembly (img2pdf — recommended)

```python
import img2pdf

png_paths = [str(p) for p in sorted(slides_dir.glob("*.png"))]
with open(output_pdf, "wb") as f:
    f.write(img2pdf.convert(png_paths))
```

Use `img2pdf` over Pillow PDF save because img2pdf embeds PNG bytes losslessly. Pillow's PDF writer re-encodes and degrades 4K image quality.

### ZIP Export

```python
import zipfile
from pathlib import Path

with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_STORED) as zf:
    for png_path in sorted(slides_dir.glob("*.png")):
        zf.write(png_path, png_path.name)
```

`ZIP_STORED` (no compression) is correct — PNG files are already compressed.

### XML Design System Loading

```python
import xml.etree.ElementTree as ET

tree = ET.parse(design_system_path)
root = tree.getroot()

# Example: extract slide type templates
for slide_template in root.findall(".//slide-type"):
    slide_name = slide_template.get("name")
    layout = slide_template.find("layout")
    # ...
```

No external library needed. Design system XMLs are ~1000 lines — `ET.parse()` is appropriate.

---

## Installation

```toml
# Add to pyproject.toml [project] dependencies:
"google-genai>=1.65.0",
"Pillow>=12.1.0",
"img2pdf>=0.6.3",
```

```bash
# Install new deps into existing virtualenv:
pip install "google-genai>=1.65.0" "Pillow>=12.1.0" "img2pdf>=0.6.3"
```

---

## Alternatives Considered

| Recommended | Alternative | Why Not |
|---|---|---|
| `google-genai` | `google-generativeai` | Deprecated; `google-genai` is the successor and only SDK receiving active updates as of 2025 |
| `img2pdf` for PDF assembly | `reportlab` | ReportLab is a full PDF layout engine (overkill); it re-encodes images at lower quality by default; complex API for what is a simple image-stacking operation |
| `img2pdf` for PDF assembly | Pillow `save(..., save_all=True)` | Pillow re-encodes PNG pixels during PDF save, degrading 4K slide quality |
| `xml.etree.ElementTree` (stdlib) | `lxml` | `lxml` (v6.0.2) is powerful but adds a C-extension dependency with binary wheels; design system XML is flat/predictable structure not requiring XPath 2.0 or XSLT; stdlib ET is sufficient |
| `zipfile` (stdlib) | `shutil.make_archive` | `make_archive` creates zip from a directory but can't selectively include/exclude files; `zipfile` gives explicit control over what enters the archive |
| Pillow `LANCZOS` for upscaling | `waifu2x` / AI upscalers | Massively heavier dependency; Pillow LANCZOS is sufficient for upscaling clean AI-generated slides from 2K to 4K |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|---|---|---|
| `google-generativeai` | Deprecated Python SDK; superseded by `google-genai`; no longer receiving API updates | `google-genai>=1.65.0` |
| `fpdf2` / `pdfkit` | Not designed for high-fidelity image-to-PDF; `pdfkit` requires wkhtmltopdf binary install | `img2pdf` |
| `OpenCV` (`cv2`) | Massive dependency for image processing we don't need; Pillow covers all required operations (resize, format convert, save) | `Pillow` |
| `matplotlib` | Not a slide renderer; sometimes used as a quick image saver but wrong tool here | `Pillow` + `img2pdf` |
| Gemini 3.x preview models | Preview/experimental as of 2026-02-26; not stable for production; model IDs may change | `gemini-2.5-flash` (stable) |

---

## Version Compatibility

| Package | Compatible With | Notes |
|---|---|---|
| `google-genai>=1.65.0` | Python 3.10+ | Matches project `requires-python = ">=3.10"` |
| `Pillow>=12.1.0` | Python 3.9+ | No conflict; 12.x dropped Python 3.8 support |
| `img2pdf>=0.6.3` | Python 3.6+ | No conflicts; pure Python with optional C extension |
| `google-genai` + `anthropic` | No overlap | Different API clients; no version conflicts expected; both read env vars independently |

---

## Engine Module Integration Notes

The new `design` command follows the same pattern as existing engine modules:

1. **New file:** `src/pitchdeck/engine/designer.py` — contains `generate_slides()` taking typed Pydantic models, checking `GEMINI_API_KEY` at call time, raising `PitchDeckError` if missing
2. **New file:** `src/pitchdeck/engine/design_systems.py` — XML loader returning typed Pydantic models for design system config
3. **New CLI command:** `pitchdeck design` in `cli.py` following existing `Annotated` option pattern
4. **New models:** Design-related Pydantic models added to `models.py` (DesignSystem, SlideDesignConfig, GeneratedSlide)
5. **GEMINI_API_KEY:** Loaded by existing `python-dotenv` `.env` mechanism; just needs to be documented in `.env.example`

---

## Sources

- PyPI `google-genai` — version 1.65.0 confirmed (https://pypi.org/project/google-genai/); HIGH confidence
- Google AI Docs Imagen — model names, aspect ratios, imageSize options (https://ai.google.dev/gemini-api/docs/imagen); HIGH confidence
- Google AI Docs Models — `gemini-2.5-flash` as stable production model (https://ai.google.dev/gemini-api/docs/models/gemini); HIGH confidence
- googleapis.github.io python-genai — GenerateImagesConfig API, generate_images() call signature; HIGH confidence
- PyPI `Pillow` — version 12.1.1 confirmed (https://pypi.org/project/Pillow/); HIGH confidence
- PyPI `img2pdf` — version 0.6.3, lossless PNG-to-PDF assembly (https://pypi.org/project/img2pdf/); HIGH confidence
- PyPI `reportlab` — version 4.4.10, ruled out (https://pypi.org/project/reportlab/); HIGH confidence
- Python docs `xml.etree.ElementTree` — stdlib XML parsing adequacy for 1000-line files; HIGH confidence
- PyPI `lxml` — version 6.0.2, ruled out as overkill (https://pypi.org/project/lxml/); HIGH confidence

---

*Stack research for: Gemini/Imagen visual slide generation additions to pitchdeck CLI*
*Researched: 2026-02-26*
