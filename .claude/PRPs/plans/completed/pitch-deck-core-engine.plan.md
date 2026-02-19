# Feature: Pitch Deck Core Engine

## Summary

Build a Python CLI tool that ingests company documents (PDF/DOCX) and VC profile configs (YAML), then uses Claude's structured output API to generate a complete 15-18 slide pitch deck as Markdown. The first target is generating the NeuraPlox pitch deck for Earlybird Capital. The tool interactively fills information gaps, uses prompt caching for cost efficiency, and outputs slide-by-slide content with titles, bullet points, metrics, and speaker notes.

## User Story

As a technical founder with limited VC pitch experience
I want to generate a complete, VC-tailored pitch deck from my company documents
So that I can focus on telling my story confidently instead of guessing what belongs on each slide

## Problem Statement

Technical founders pitching to VCs waste critical time guessing narrative structure, missing key slides, and over-indexing on architecture while under-indexing on business proof. The tool must transform raw company documents + VC research into a complete, scored, slide-by-slide deck in under 30 minutes.

## Solution Statement

A Python CLI application that:
1. Parses company PDFs/DOCXs into LLM-ready Markdown (pymupdf4llm)
2. Loads VC-specific profiles from YAML configs (Earlybird first)
3. Detects missing data points and interactively fills gaps
4. Generates 15-18 slides via Claude structured output API (Pydantic models)
5. Outputs the complete deck as Markdown with speaker notes

## Metadata

| Field            | Value                                                        |
| ---------------- | ------------------------------------------------------------ |
| Type             | NEW_CAPABILITY                                               |
| Complexity       | HIGH                                                         |
| Systems Affected | New Python package (greenfield)                              |
| Dependencies     | anthropic>=0.82.0, pymupdf>=1.27, pymupdf4llm, python-docx>=1.2.0, typer>=0.24.0, ruamel.yaml>=0.19, pydantic>=2.0, questionary>=2.0 |
| Estimated Tasks  | 14                                                           |

---

## UX Design

### Before State

```
+-----------------------------------------------------------------------+
|                          BEFORE STATE                                  |
+-----------------------------------------------------------------------+
|                                                                        |
|   [Company Docs]     [VC Research]      [Best Practices]              |
|   ZIM app, arch      Google searches    Blog posts, podcasts          |
|   docs, financials   Earlybird website  TechCrunch reviews            |
|        |                  |                    |                       |
|        v                  v                    v                       |
|   +----------------------------------------------------+              |
|   |        FOUNDER'S BRAIN (manual assembly)           |              |
|   |  - Guessing slide order                            |              |
|   |  - Unsure what metrics to highlight                |              |
|   |  - Over-indexing on architecture                   |              |
|   |  - Missing competitive positioning                 |              |
|   +----------------------------------------------------+              |
|        |                                                               |
|        v                                                               |
|   [Incomplete deck with wrong emphasis]                                |
|                                                                        |
|   PAIN: Days of manual work, still unsure if deck resonates           |
|   PAIN: No VC-specific tailoring or validation                        |
|   PAIN: Technical founder doesn't know "the game"                     |
+-----------------------------------------------------------------------+
```

### After State

```
+-----------------------------------------------------------------------+
|                           AFTER STATE                                  |
+-----------------------------------------------------------------------+
|                                                                        |
|   [Company Docs]     [VC Profile YAML]                                |
|   PDF / DOCX         earlybird.yaml                                   |
|        |                  |                                            |
|        v                  v                                            |
|   +----------------------------------------------------+              |
|   |  $ pitchdeck generate company.pdf --vc earlybird   |              |
|   +----------------------------------------------------+              |
|        |                                                               |
|        v                                                               |
|   +----------------------------------------------------+              |
|   |  GAP DETECTION (interactive)                       |              |
|   |  > Target raise amount ($M)? 5                     |              |
|   |  > Net Dollar Retention %? 115                     |              |
|   |  > Disclosable customer names? [select]            |              |
|   +----------------------------------------------------+              |
|        |                                                               |
|        v                                                               |
|   +----------------------------------------------------+              |
|   |  CLAUDE NARRATIVE ENGINE                           |              |
|   |  - Analyzes docs + VC thesis alignment             |              |
|   |  - Determines optimal slide order                  |              |
|   |  - Generates 15-18 slides with speaker notes       |              |
|   |  - Identifies company strengths to emphasize       |              |
|   +----------------------------------------------------+              |
|        |                                                               |
|        v                                                               |
|   [Complete Markdown deck]                                             |
|   - 15-18 slides with titles, bullets, metrics                        |
|   - Speaker notes per slide                                           |
|   - Narrative transitions between slides                              |
|   - VC-specific alignment callouts                                    |
|                                                                        |
|   VALUE: Complete deck in < 30 min, VC-tailored, no guessing         |
+-----------------------------------------------------------------------+
```

### Interaction Changes

| Location | Before | After | User Impact |
|----------|--------|-------|-------------|
| Terminal | No tool | `pitchdeck generate <file> --vc <profile>` | One command to generate deck |
| Gap filling | Founder doesn't know what's missing | Interactive prompts for missing data | No blind spots |
| Slide structure | Manual guessing | Proven 15-18 slide template | Correct structure guaranteed |
| VC tailoring | Generic deck | Earlybird thesis-aligned narrative | Higher investor resonance |
| Speaker notes | None | Auto-generated per slide | Founder knows what to say |
| Output | Scattered Google Docs | Single Markdown file, structured | Ready for rendering pipeline |

---

## Mandatory Reading

**CRITICAL: Implementation agent MUST read these files before starting any task:**

| Priority | File | Lines | Why Read This |
|----------|------|-------|---------------|
| P0 | `.claude/PRPs/prds/pitch-deck-generator.prd.md` | all | Full PRD context, requirements, research data |
| P0 | This plan file | all | Implementation blueprint |

**External Documentation:**

| Source | Section | Why Needed |
|--------|---------|------------|
| [Anthropic Structured Outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) | Pydantic integration | Core slide generation mechanism |
| [Anthropic Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | Ephemeral caching | Cost optimization for document context |
| [pymupdf4llm Docs](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) | to_markdown() | PDF extraction to LLM-ready format |
| [Typer Docs](https://typer.tiangolo.com/) | Prompts, Options | CLI interactive patterns |
| [python-docx Docs](https://python-docx.readthedocs.io/) | Paragraph access | DOCX structured extraction |
| [ruamel.yaml Docs](https://yaml.readthedocs.io/en/latest/) | Round-trip loading | YAML config parsing |

---

## Patterns to Mirror

**This is a greenfield project.** No existing codebase patterns. The following patterns are PRESCRIBED for this project based on research:

**PROJECT_STRUCTURE:**
```
capital/
├── pyproject.toml
├── README.md
├── src/
│   └── pitchdeck/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── models.py
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── pdf.py
│       │   └── docx_parser.py
│       ├── profiles/
│       │   ├── __init__.py
│       │   └── loader.py
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── slides.py
│       │   ├── narrative.py
│       │   └── gaps.py
│       └── output/
│           ├── __init__.py
│           └── markdown.py
├── profiles/
│   └── earlybird.yaml
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_parsers.py
    ├── test_profiles.py
    ├── test_models.py
    ├── test_engine.py
    └── test_output.py
```

**NAMING_CONVENTION:**
```python
# Snake case for modules and functions
# PascalCase for Pydantic models and classes
# UPPER_SNAKE_CASE for constants
# Example:
def generate_slide_content(company_data: CompanyProfile, slide_template: SlideTemplate) -> SlideContent:
    ...
```

**ERROR_HANDLING:**
```python
# Custom exceptions in each module, inherit from base
class PitchDeckError(Exception):
    """Base exception for pitch deck generator."""
    pass

class DocumentParseError(PitchDeckError):
    """Raised when document parsing fails."""
    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Failed to parse {path}: {reason}")

class ProfileNotFoundError(PitchDeckError):
    """Raised when VC profile YAML not found."""
    pass
```

**PYDANTIC_MODELS:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class SlideContent(BaseModel):
    slide_number: int
    slide_type: str
    title: str
    headline: str
    bullets: List[str]
    metrics: List[str] = Field(default_factory=list)
    speaker_notes: str
    transition_to_next: str = ""
```

**CLI_PATTERN:**
```python
import typer
from typing import Annotated

app = typer.Typer(rich_markup_mode="rich")

@app.command()
def generate(
    input_files: Annotated[List[str], typer.Argument(help="PDF or DOCX paths")],
    vc: Annotated[str, typer.Option("--vc", "-v", help="VC profile name")] = "earlybird",
    output: Annotated[str, typer.Option("--output", "-o", help="Output path")] = "deck.md",
):
    """Generate a pitch deck from company documents."""
    ...
```

**TEST_STRUCTURE:**
```python
# Using pytest
import pytest
from pitchdeck.models import SlideContent, CompanyProfile

class TestSlideContent:
    def test_creates_valid_slide(self):
        slide = SlideContent(
            slide_number=1,
            slide_type="cover",
            title="NeuraPlox",
            headline="The AI Control Plane for European SMEs",
            bullets=["EUR 2.3M revenue", "20 employees"],
            speaker_notes="Open with the vision...",
        )
        assert slide.slide_number == 1

    def test_rejects_empty_title(self):
        with pytest.raises(ValidationError):
            SlideContent(slide_number=1, slide_type="cover", title="", ...)
```

---

## Files to Change

| File | Action | Justification |
|------|--------|---------------|
| `pyproject.toml` | CREATE | Project config, dependencies, entry point |
| `src/pitchdeck/__init__.py` | CREATE | Package init with version |
| `src/pitchdeck/__main__.py` | CREATE | `python -m pitchdeck` support |
| `src/pitchdeck/cli.py` | CREATE | Typer CLI with generate command |
| `src/pitchdeck/models.py` | CREATE | All Pydantic models (company, VC, slides, deck) |
| `src/pitchdeck/parsers/__init__.py` | CREATE | Parser package |
| `src/pitchdeck/parsers/pdf.py` | CREATE | PyMuPDF/pymupdf4llm PDF extraction |
| `src/pitchdeck/parsers/docx_parser.py` | CREATE | python-docx DOCX extraction |
| `src/pitchdeck/profiles/__init__.py` | CREATE | Profiles package |
| `src/pitchdeck/profiles/loader.py` | CREATE | YAML profile loading + validation |
| `src/pitchdeck/engine/__init__.py` | CREATE | Engine package |
| `src/pitchdeck/engine/slides.py` | CREATE | Slide structure template (15-18 slides) |
| `src/pitchdeck/engine/narrative.py` | CREATE | Claude API narrative generation |
| `src/pitchdeck/engine/gaps.py` | CREATE | Gap detection + interactive filling |
| `src/pitchdeck/output/__init__.py` | CREATE | Output package |
| `src/pitchdeck/output/markdown.py` | CREATE | Markdown deck rendering |
| `profiles/earlybird.yaml` | CREATE | Earlybird Capital VC profile |
| `tests/__init__.py` | CREATE | Test package |
| `tests/conftest.py` | CREATE | Shared fixtures |
| `tests/test_models.py` | CREATE | Model validation tests |
| `tests/test_parsers.py` | CREATE | Parser unit tests |
| `tests/test_profiles.py` | CREATE | Profile loading tests |
| `tests/test_engine.py` | CREATE | Engine logic tests |
| `tests/test_output.py` | CREATE | Markdown output tests |

---

## NOT Building (Scope Limits)

Explicit exclusions to prevent scope creep:

- **Validation/scoring engine** — Phase 2 handles rubric scoring, per-slide scoring, and Earlybird-specific validation checks
- **JSON export** — Phase 3 handles structured JSON output for Imagen3 pipeline
- **Q&A/objection document generation** — Phase 3 scope
- **Visual slide rendering** — Phase 4 (optional), Imagen3 integration
- **Multi-VC profile management UI** — just file-based YAML configs for now
- **Deck versioning/iteration tracking** — "Could" priority in PRD, not Phase 1
- **Competitor positioning auto-generation** — "Should" priority; the narrative engine generates competitive slide content from inputs, but no automated competitor research
- **Database or persistence** — file I/O only, no database
- **Web UI** — CLI only

---

## Step-by-Step Tasks

Execute in order. Each task is atomic and independently verifiable.

### Task 1: CREATE `pyproject.toml` — Project Setup

- **ACTION**: Create project configuration with all dependencies
- **IMPLEMENT**:
  ```toml
  [build-system]
  requires = ["hatchling"]
  build-backend = "hatchling.build"

  [project]
  name = "pitchdeck"
  version = "0.1.0"
  description = "Pitch deck generator and validator for B2B AI/SaaS companies"
  requires-python = ">=3.10"
  dependencies = [
      "anthropic>=0.82.0",
      "pymupdf>=1.27",
      "pymupdf4llm>=0.0.17",
      "python-docx>=1.2.0",
      "typer[all]>=0.24.0",
      "ruamel.yaml>=0.19",
      "pydantic>=2.0",
      "questionary>=2.0",
  ]

  [project.optional-dependencies]
  dev = [
      "pytest>=8.0",
      "pytest-cov>=5.0",
  ]

  [project.scripts]
  pitchdeck = "pitchdeck.cli:app"

  [tool.hatch.build.targets.wheel]
  packages = ["src/pitchdeck"]

  [tool.pytest.ini_options]
  testpaths = ["tests"]
  pythonpath = ["src"]
  ```
- **GOTCHA**: Use `typer[all]` to bundle Rich and Shellingham. Use `pymupdf` not `PyMuPDF` as the pip package name. The `pythonpath = ["src"]` in pytest config is essential for src-layout imports.
- **VALIDATE**: `pip install -e ".[dev]"` — must install without errors

### Task 2: CREATE `src/pitchdeck/__init__.py` and `src/pitchdeck/__main__.py`

- **ACTION**: Create package init and __main__ entry point
- **IMPLEMENT**:
  ```python
  # __init__.py
  """Pitch deck generator for B2B AI/SaaS companies."""
  __version__ = "0.1.0"
  ```
  ```python
  # __main__.py
  """Allow running as: python -m pitchdeck"""
  from pitchdeck.cli import app
  app()
  ```
- **VALIDATE**: `python -c "import pitchdeck; print(pitchdeck.__version__)"` — prints "0.1.0"

### Task 3: CREATE `src/pitchdeck/models.py` — All Pydantic Data Models

- **ACTION**: Define all data models used throughout the application
- **IMPLEMENT**: Create these Pydantic models:

  **CompanyProfile** — structured company data:
  ```python
  class CompanyProfile(BaseModel):
      name: str
      product_name: str
      one_liner: str  # e.g., "The AI Control Plane for European SMEs"
      founded_year: int
      employee_count: int
      revenue_eur: float  # annual revenue in EUR
      revenue_type: str  # "ARR", "revenue", "GMV"
      growth_rate_yoy: Optional[float] = None  # percentage
      customer_count: Optional[int] = None
      key_customers: List[str] = Field(default_factory=list)
      funding_stage: str  # "bootstrapped", "seed", "series-a"
      funding_raised_eur: float = 0  # total raised
      target_raise_eur: Optional[float] = None
      use_of_funds: List[str] = Field(default_factory=list)
      team_highlights: List[TeamMember] = Field(default_factory=list)
      product_description: str = ""
      technology_description: str = ""
      market_description: str = ""
      competitors: List[str] = Field(default_factory=list)
      differentiators: List[str] = Field(default_factory=list)
      ndr_percent: Optional[float] = None  # net dollar retention
      gross_margin_percent: Optional[float] = None
      burn_rate_monthly_eur: Optional[float] = None
      raw_document_text: str = ""  # full extracted text from docs
  ```

  **TeamMember**:
  ```python
  class TeamMember(BaseModel):
      name: str
      role: str
      background: str  # key credential
  ```

  **VCProfile** — VC-specific preferences and thesis:
  ```python
  class VCProfile(BaseModel):
      name: str
      fund_name: str
      aum_eur: Optional[float] = None
      stage_focus: List[str]  # ["seed", "series-a"]
      sector_focus: List[str]  # ["enterprise-ai", "deep-tech"]
      geo_focus: List[str]  # ["DACH", "Western Europe"]
      thesis_points: List[str]  # key thesis alignment points
      portfolio_companies: List[str] = Field(default_factory=list)
      key_partners: List[VCPartner] = Field(default_factory=list)
      deck_preferences: DeckPreferences = Field(default_factory=DeckPreferences)
      custom_checks: List[str] = Field(default_factory=list)  # VC-specific validation
  ```

  **VCPartner**:
  ```python
  class VCPartner(BaseModel):
      name: str
      focus: str
      background: str = ""
  ```

  **DeckPreferences**:
  ```python
  class DeckPreferences(BaseModel):
      preferred_slide_count: int = 15
      must_include_slides: List[str] = Field(default_factory=list)
      metrics_emphasis: List[str] = Field(default_factory=list)  # which metrics they care about
      narrative_style: str = "data-driven"  # "data-driven", "vision-first", "balanced"
      market_sizing_approach: str = "bottom-up"  # "bottom-up", "top-down", "both"
  ```

  **SlideTemplate** — defines purpose/structure of each slide type:
  ```python
  class SlideTemplate(BaseModel):
      slide_type: str  # "cover", "problem", "solution", etc.
      purpose: str
      required_elements: List[str]
      optional_elements: List[str] = Field(default_factory=list)
      metrics_needed: List[str] = Field(default_factory=list)
      max_bullets: int = 5
      word_limit: int = 150
  ```

  **SlideContent** — generated content for a single slide:
  ```python
  class SlideContent(BaseModel):
      slide_number: int
      slide_type: str
      title: str
      headline: str
      bullets: List[str]
      metrics: List[str] = Field(default_factory=list)
      speaker_notes: str
      transition_to_next: str = ""
      vc_alignment_notes: List[str] = Field(default_factory=list)
  ```

  **PitchDeck** — the full deck output:
  ```python
  class PitchDeck(BaseModel):
      company_name: str
      target_vc: str
      generated_at: str
      slides: List[SlideContent]
      narrative_arc: str  # overall story summary
      gaps_identified: List[str] = Field(default_factory=list)
      gaps_filled: dict[str, str] = Field(default_factory=dict)
  ```

  **GapQuestion** — a missing data point to fill:
  ```python
  class GapQuestion(BaseModel):
      field: str  # which model field this fills
      question: str  # human-readable question
      importance: str  # "critical", "important", "nice-to-have"
      default: Optional[str] = None
      choices: List[str] = Field(default_factory=list)  # if multiple choice
  ```

- **GOTCHA**: Use `Optional[X] = None` not `X | None` for Python 3.10 compat. Use `Field(default_factory=list)` for mutable defaults. Import from `pydantic` not `pydantic.v1`.
- **VALIDATE**: `python -c "from pitchdeck.models import PitchDeck, CompanyProfile, VCProfile; print('OK')"`

### Task 4: CREATE `src/pitchdeck/parsers/pdf.py` — PDF Document Parser

- **ACTION**: Create PDF text extraction using pymupdf4llm
- **IMPLEMENT**:
  ```python
  import pymupdf4llm

  def extract_pdf(path: str) -> str:
      """Extract PDF content as LLM-ready Markdown.

      Uses pymupdf4llm which preserves headings, tables, and lists
      in a format optimized for LLM consumption.
      """
      if not os.path.exists(path):
          raise DocumentParseError(path, "File not found")
      try:
          return pymupdf4llm.to_markdown(path)
      except Exception as e:
          raise DocumentParseError(path, str(e)) from e
  ```
- **IMPORTS**: `import os`, `from pitchdeck.models import DocumentParseError` (add DocumentParseError to models if not using separate errors)
- **GOTCHA**: pymupdf4llm.to_markdown() can fail on password-protected PDFs — catch and raise DocumentParseError. The function returns a single string with full Markdown formatting.
- **VALIDATE**: Create a simple test PDF and verify extraction: `python -c "from pitchdeck.parsers.pdf import extract_pdf; print(extract_pdf('test.pdf')[:200])"`

### Task 5: CREATE `src/pitchdeck/parsers/docx_parser.py` — DOCX Document Parser

- **ACTION**: Create DOCX text extraction preserving structure
- **IMPLEMENT**:
  ```python
  from docx import Document

  def extract_docx(path: str) -> str:
      """Extract DOCX content as Markdown-formatted text.

      Preserves heading hierarchy and paragraph structure.
      """
      doc = Document(path)
      sections = []
      for para in doc.paragraphs:
          style = para.style.name
          text = para.text.strip()
          if not text:
              continue
          if style.startswith("Heading"):
              level_str = style.split()[-1]
              try:
                  level = int(level_str)
              except ValueError:
                  level = 2
              sections.append(f"{'#' * level} {text}")
          else:
              sections.append(text)
      return "\n\n".join(sections)
  ```
- **ALSO**: Create `src/pitchdeck/parsers/__init__.py` with a unified `extract_document(path)` function that dispatches to pdf or docx based on extension:
  ```python
  def extract_document(path: str) -> str:
      """Extract text from PDF or DOCX file."""
      if path.lower().endswith(".pdf"):
          from .pdf import extract_pdf
          return extract_pdf(path)
      elif path.lower().endswith((".docx", ".doc")):
          from .docx_parser import extract_docx
          return extract_docx(path)
      else:
          raise DocumentParseError(path, f"Unsupported format. Use PDF or DOCX.")
  ```
- **GOTCHA**: Name the file `docx_parser.py` not `docx.py` to avoid shadowing the `docx` package import. The `.doc` format (legacy Word) is NOT supported by python-docx — only `.docx`.
- **VALIDATE**: `python -c "from pitchdeck.parsers import extract_document; print('OK')"`

### Task 6: CREATE `src/pitchdeck/profiles/loader.py` — VC Profile Loader

- **ACTION**: Create YAML-based VC profile loading with Pydantic validation
- **IMPLEMENT**:
  ```python
  from ruamel.yaml import YAML
  from pitchdeck.models import VCProfile, ProfileNotFoundError

  PROFILES_DIR = Path(__file__).parent.parent.parent.parent / "profiles"

  def load_vc_profile(name: str, profiles_dir: Optional[Path] = None) -> VCProfile:
      """Load a VC profile from YAML config.

      Searches for {name}.yaml in the profiles directory.
      """
      search_dir = profiles_dir or PROFILES_DIR
      profile_path = search_dir / f"{name}.yaml"
      if not profile_path.exists():
          available = [p.stem for p in search_dir.glob("*.yaml")]
          raise ProfileNotFoundError(
              f"Profile '{name}' not found. Available: {', '.join(available)}"
          )
      yaml = YAML()
      with open(profile_path) as f:
          raw = yaml.load(f)
      return VCProfile(**raw)

  def list_profiles(profiles_dir: Optional[Path] = None) -> list[str]:
      """List available VC profile names."""
      search_dir = profiles_dir or PROFILES_DIR
      return sorted(p.stem for p in search_dir.glob("*.yaml"))
  ```
- **ALSO**: Create `src/pitchdeck/profiles/__init__.py` re-exporting `load_vc_profile`, `list_profiles`
- **GOTCHA**: Use `ruamel.yaml` (YAML 1.2) not PyYAML (YAML 1.1) — avoids the "Norway problem" where unquoted `No` parses as boolean `False`. The `PROFILES_DIR` path traversal must account for src-layout (4 levels up from loader.py to project root).
- **VALIDATE**: `python -c "from pitchdeck.profiles import list_profiles; print(list_profiles())"` — should show `['earlybird']` after Task 7

### Task 7: CREATE `profiles/earlybird.yaml` — Earlybird Capital Profile

- **ACTION**: Create the first VC profile based on research
- **IMPLEMENT**: Full Earlybird profile based on research findings:
  ```yaml
  name: Earlybird Capital
  fund_name: Fund VII
  aum_eur: 2000000000  # EUR 2B total AUM
  stage_focus:
    - pre-seed
    - seed
    - series-a
  sector_focus:
    - enterprise-software
    - enterprise-ai
    - deep-tech
    - fintech
    - sustainability
  geo_focus:
    - DACH
    - Western Europe
    - Central Europe
    - Eastern Europe
  thesis_points:
    - European digital sovereignty — AI infrastructure that keeps European data and decisions in European hands
    - Category creation — companies defining new market categories (like UiPath defined RPA, remberg defined XRM)
    - Capital-efficient growth — burn multiple below 1.5x, revenue-to-raised ratio near 1:1
    - AI as infrastructure, not veneer — proprietary data moats, workflow automation, vertical specialization
    - Deep tech with clear commercialization path — not pure research, but applied AI solving real enterprise problems
    - Global winner potential from European base — can this company lead globally?
    - Industrial/enterprise domain expertise — founders who deeply understand the vertical they serve
  portfolio_companies:
    - Aleph Alpha (AI sovereignty, foundation models)
    - remberg (AI maintenance platform for industrials)
    - HiveMQ (IoT infrastructure)
    - EthonAI (industrial AI quality inspection)
    - Mostly AI (synthetic data)
    - Energy Robotics (industrial robotics)
    - Sikoia (fintech data unification)
  key_partners:
    - name: Dr. Andre Retterath
      focus: Enterprise Software, AI infrastructure, data tools, developer tools, robotics, OSS
      background: PhD TU Munich (ML in VC), ex-ThyssenKrupp process automation, ex-GE management consulting
  deck_preferences:
    preferred_slide_count: 15
    must_include_slides:
      - cover
      - executive-summary
      - problem
      - why-now
      - solution
      - product
      - market-sizing
      - business-model
      - traction
      - go-to-market
      - competitive-landscape
      - team
      - financials
      - the-ask
      - ai-architecture
    metrics_emphasis:
      - ARR and YoY growth rate
      - Net Dollar Retention (NDR)
      - Gross margin trajectory
      - Burn multiple (new ARR / cash burned)
      - Capital efficiency ratio (revenue / total raised)
      - Customer count and logo quality
      - ACV and expansion revenue
      - Bottom-up SOM with methodology
    narrative_style: data-driven
    market_sizing_approach: bottom-up
  custom_checks:
    - European sovereignty angle must be present
    - Bottom-up market sizing required (not just top-down TAM)
    - Capital efficiency must be explicitly highlighted
    - Named or anonymized customer evidence with quantified ROI
    - AI commoditization risk must be proactively addressed
    - Gross margin trajectory must be shown or discussed
    - Category creation narrative should be present
  ```
- **GOTCHA**: All string values that could be confused with YAML booleans (like "No") should be quoted. Use `#` comments for documentation. Use full EUR amounts (not millions) for aum_eur to avoid ambiguity.
- **VALIDATE**: `python -c "from pitchdeck.profiles import load_vc_profile; p = load_vc_profile('earlybird'); print(p.name, len(p.thesis_points))"`

### Task 8: CREATE `src/pitchdeck/engine/slides.py` — Slide Structure Template

- **ACTION**: Define the 15-slide deck structure with per-slide templates
- **IMPLEMENT**: Create a `SLIDE_TEMPLATES` list of `SlideTemplate` objects defining each slide's purpose, required elements, and metrics. Based on the proven Series A B2B SaaS/AI structure:

  ```python
  SLIDE_TEMPLATES: list[SlideTemplate] = [
      SlideTemplate(
          slide_type="cover",
          purpose="10-second filter — company name, one-liner, stage, contact",
          required_elements=["company_name", "product_name", "one_liner", "funding_stage"],
          metrics_needed=[],
          max_bullets=0,
          word_limit=30,
      ),
      SlideTemplate(
          slide_type="executive-summary",
          purpose="Value prop, competitive edge, flagship results in 30 seconds",
          required_elements=["value_proposition", "key_metric_1", "key_metric_2", "competitive_edge"],
          metrics_needed=["revenue", "growth_rate", "customer_count"],
          max_bullets=4,
          word_limit=100,
      ),
      SlideTemplate(
          slide_type="problem",
          purpose="Systemic pain with market data — not anecdotes",
          required_elements=["problem_statement", "market_evidence", "cost_of_problem", "who_feels_it"],
          metrics_needed=["market_data_citation"],
          max_bullets=4,
          word_limit=120,
      ),
      SlideTemplate(
          slide_type="why-now",
          purpose="Macro tailwind making this the right moment",
          required_elements=["timing_catalyst", "market_shift", "technology_enabler"],
          optional_elements=["regulatory_driver"],
          metrics_needed=[],
          max_bullets=4,
          word_limit=120,
      ),
      SlideTemplate(
          slide_type="solution",
          purpose="Product type, end user, vertical, quantified impact",
          required_elements=["product_description", "target_user", "key_benefit", "quantified_impact"],
          metrics_needed=["roi_metric"],
          max_bullets=5,
          word_limit=150,
      ),
      SlideTemplate(
          slide_type="product",
          purpose="Architecture overview, key capabilities, differentiation",
          required_elements=["architecture_overview", "key_capabilities", "technical_moat"],
          optional_elements=["demo_description", "screenshot_placeholder"],
          metrics_needed=[],
          max_bullets=5,
          word_limit=150,
      ),
      SlideTemplate(
          slide_type="market-sizing",
          purpose="TAM/SAM/SOM with bottom-up methodology",
          required_elements=["tam", "sam", "som", "methodology_explanation"],
          metrics_needed=["tam_eur", "sam_eur", "som_eur", "icp_count", "arpu"],
          max_bullets=4,
          word_limit=120,
      ),
      SlideTemplate(
          slide_type="business-model",
          purpose="Pricing model, unit economics, gross margin",
          required_elements=["pricing_model", "price_range", "unit_economics_summary"],
          metrics_needed=["acv", "gross_margin", "ltv", "cac", "payback_period"],
          max_bullets=5,
          word_limit=130,
      ),
      SlideTemplate(
          slide_type="traction",
          purpose="Growth proof — most scrutinized slide by VCs",
          required_elements=["revenue_metric", "growth_trajectory", "customer_evidence"],
          metrics_needed=["arr_or_revenue", "yoy_growth", "customer_count", "ndr", "logo_names_or_anonymized"],
          max_bullets=5,
          word_limit=130,
      ),
      SlideTemplate(
          slide_type="go-to-market",
          purpose="ICP, sales motion, channels, partnerships",
          required_elements=["icp_definition", "sales_motion", "channel_strategy"],
          optional_elements=["partnership_strategy", "expansion_playbook"],
          metrics_needed=["cac", "sales_cycle_days"],
          max_bullets=5,
          word_limit=130,
      ),
      SlideTemplate(
          slide_type="competitive-landscape",
          purpose="2-axis positioning matrix with differentiated axes",
          required_elements=["positioning_matrix_description", "key_differentiators", "competitive_moat"],
          optional_elements=["win_rate"],
          metrics_needed=[],
          max_bullets=4,
          word_limit=120,
      ),
      SlideTemplate(
          slide_type="team",
          purpose="Domain expertise, key hires, credibility foundation",
          required_elements=["founders_with_credentials", "key_hires", "domain_expertise_proof"],
          optional_elements=["advisors", "board_members"],
          metrics_needed=["years_domain_experience"],
          max_bullets=5,
          word_limit=150,
      ),
      SlideTemplate(
          slide_type="financials",
          purpose="Revenue trajectory, burn rate, runway",
          required_elements=["revenue_trajectory", "cost_structure", "path_to_profitability"],
          metrics_needed=["current_mrr", "burn_rate", "runway_months", "burn_multiple"],
          max_bullets=4,
          word_limit=120,
      ),
      SlideTemplate(
          slide_type="the-ask",
          purpose="Amount, use of funds, milestones to next round",
          required_elements=["raise_amount", "use_of_funds_breakdown", "key_milestones_18_months"],
          metrics_needed=["raise_amount_eur", "target_arr_18_months"],
          max_bullets=5,
          word_limit=130,
      ),
      SlideTemplate(
          slide_type="ai-architecture",
          purpose="Technical depth for AI-specific investors — moat and defensibility",
          required_elements=["architecture_layers", "data_moat", "ai_approach"],
          optional_elements=["performance_benchmarks", "ip_description"],
          metrics_needed=[],
          max_bullets=5,
          word_limit=150,
      ),
  ]
  ```

  Also include a helper:
  ```python
  def get_slide_templates(vc_profile: VCProfile) -> list[SlideTemplate]:
      """Return slide templates filtered and ordered by VC preferences."""
      must_include = set(vc_profile.deck_preferences.must_include_slides)
      return [t for t in SLIDE_TEMPLATES if t.slide_type in must_include]

  def get_narrative_arc() -> str:
      """Return the narrative psychology arc description for the prompt."""
      return """..."""  # The 6-stage arc from research
  ```

- **GOTCHA**: The slide order matters — it follows investor psychology: Hook > Problem urgency > Solution credibility > Market validation > Execution capability > Investment thesis. Don't reorder without reason.
- **VALIDATE**: `python -c "from pitchdeck.engine.slides import SLIDE_TEMPLATES; print(f'{len(SLIDE_TEMPLATES)} slides defined')"`

### Task 9: CREATE `src/pitchdeck/engine/gaps.py` — Gap Detection and Interactive Filling

- **ACTION**: Detect missing company data and prompt user interactively
- **IMPLEMENT**:
  ```python
  import questionary
  from pitchdeck.models import CompanyProfile, GapQuestion, SlideTemplate

  # Define known gaps with their questions
  GAP_DEFINITIONS: list[GapQuestion] = [
      GapQuestion(
          field="target_raise_eur",
          question="Target fundraise amount (EUR)?",
          importance="critical",
      ),
      GapQuestion(
          field="ndr_percent",
          question="Net Dollar Retention (NDR) percentage?",
          importance="critical",
      ),
      GapQuestion(
          field="gross_margin_percent",
          question="Gross margin percentage?",
          importance="important",
      ),
      GapQuestion(
          field="burn_rate_monthly_eur",
          question="Monthly burn rate (EUR)?",
          importance="important",
      ),
      GapQuestion(
          field="growth_rate_yoy",
          question="Year-over-year revenue growth rate (%)?",
          importance="critical",
      ),
      GapQuestion(
          field="customer_count",
          question="Number of paying customers?",
          importance="important",
      ),
      # ... more gaps
  ]

  def detect_gaps(profile: CompanyProfile, templates: list[SlideTemplate]) -> list[GapQuestion]:
      """Identify missing data points needed for slide generation."""
      gaps = []
      for gap_def in GAP_DEFINITIONS:
          value = getattr(profile, gap_def.field, None)
          if value is None or value == "" or value == 0:
              gaps.append(gap_def)
      return gaps

  def fill_gaps_interactive(profile: CompanyProfile, gaps: list[GapQuestion]) -> CompanyProfile:
      """Prompt user to fill missing data points."""
      updates = {}
      for gap in gaps:
          label = f"[{gap.importance.upper()}]" if gap.importance == "critical" else f"[{gap.importance}]"
          if gap.choices:
              answer = questionary.select(
                  f"{label} {gap.question}",
                  choices=gap.choices + ["Skip"],
              ).ask()
          else:
              answer = questionary.text(
                  f"{label} {gap.question}",
                  default=gap.default or "",
              ).ask()
          if answer and answer != "Skip":
              updates[gap.field] = _coerce_value(gap.field, answer)
      return profile.model_copy(update=updates)

  def _coerce_value(field: str, value: str):
      """Coerce string input to the appropriate type."""
      # numeric fields
      numeric_fields = {"target_raise_eur", "ndr_percent", "gross_margin_percent",
                        "burn_rate_monthly_eur", "growth_rate_yoy", "revenue_eur"}
      if field in numeric_fields:
          return float(value.replace(",", "").replace("EUR", "").strip())
      int_fields = {"customer_count", "employee_count"}
      if field in int_fields:
          return int(value.replace(",", "").strip())
      return value
  ```
- **GOTCHA**: `questionary` is a separate package from `typer` prompts — it provides richer UX (checkboxes, autocomplete). Use `model_copy(update=...)` (Pydantic v2) not `.copy(update=...)` (deprecated Pydantic v1 pattern). Handle Ctrl+C gracefully in interactive prompts.
- **VALIDATE**: `python -c "from pitchdeck.engine.gaps import detect_gaps, GAP_DEFINITIONS; print(f'{len(GAP_DEFINITIONS)} gap definitions')"`

### Task 10: CREATE `src/pitchdeck/engine/narrative.py` — Claude API Narrative Engine

- **ACTION**: Create the core LLM-powered slide generation using Anthropic structured outputs
- **IMPLEMENT**: This is the most complex module. Key components:

  1. **System prompt construction** — combine VC thesis, slide structure rules, and pitch best practices
  2. **Company document caching** — use prompt caching for the large document context
  3. **Slide generation** — use structured output (Pydantic) for typed slide content
  4. **Full-deck generation** — generate all slides in one call for narrative coherence

  ```python
  from anthropic import Anthropic
  from pitchdeck.models import (
      CompanyProfile, VCProfile, PitchDeck, SlideContent, SlideTemplate
  )
  from pitchdeck.engine.slides import get_slide_templates, get_narrative_arc

  SYSTEM_PROMPT = """You are an expert pitch deck writer for B2B SaaS and enterprise AI companies
  raising Series A from European VCs. You generate investor-grade slide content that:

  1. Follows proven narrative structures (Hook > Problem > Solution > Market > Execution > Ask)
  2. Is data-driven with specific metrics on every applicable slide
  3. Uses concise, impactful language (no fluff, no generic claims)
  4. Tailors the narrative to the specific VC's investment thesis
  5. Addresses common investor objections proactively
  6. Includes actionable speaker notes for each slide

  RULES:
  - Never fabricate metrics — if data is missing, note it in the gaps
  - Keep bullets to {max_bullets} or fewer per slide
  - Each slide must have a clear "so what" — why should the investor care?
  - Speaker notes should tell the founder exactly what to SAY, not what the slide shows
  - Transitions between slides must be explicit narrative connectors
  """

  def generate_deck(
      company: CompanyProfile,
      vc_profile: VCProfile,
      slide_templates: list[SlideTemplate],
  ) -> PitchDeck:
      """Generate a complete pitch deck using Claude structured output."""
      client = Anthropic()

      # Build the VC-specific context
      vc_context = _build_vc_context(vc_profile)
      slide_instructions = _build_slide_instructions(slide_templates)
      narrative_arc = get_narrative_arc()

      # Build system messages with caching for the large document
      system_messages = [
          {"type": "text", "text": SYSTEM_PROMPT},
          {
              "type": "text",
              "text": f"""<company_document>
  {company.raw_document_text}
  </company_document>

  <company_profile>
  {company.model_dump_json(indent=2)}
  </company_profile>

  <vc_profile>
  {vc_context}
  </vc_profile>""",
              "cache_control": {"type": "ephemeral"},
          },
      ]

      user_prompt = f"""Generate a complete {len(slide_templates)}-slide pitch deck for
  {company.product_name} targeting {vc_profile.name}.

  NARRATIVE ARC:
  {narrative_arc}

  SLIDE STRUCTURE:
  {slide_instructions}

  Generate ALL slides in order. For each slide:
  1. Title: concise, impactful (5-8 words)
  2. Headline: the key takeaway (one sentence)
  3. Bullets: {slide_templates[0].max_bullets} or fewer, each with specific data
  4. Metrics: quantified data points for this slide
  5. Speaker notes: 2-3 sentences of what to SAY (not what the slide shows)
  6. Transition: one sentence connecting to the next slide
  7. VC alignment: how this slide maps to {vc_profile.name}'s thesis

  If any critical data is missing, include it in gaps_identified.
  """

      response = client.messages.create(
          model="claude-sonnet-4-6",
          max_tokens=8096,
          system=system_messages,
          messages=[{"role": "user", "content": user_prompt}],
      )

      # Parse the response into structured PitchDeck
      return _parse_deck_response(response, company, vc_profile)
  ```

  Also implement:
  - `_build_vc_context(vc_profile)` — formats VC thesis points, preferences, and custom checks into prompt text
  - `_build_slide_instructions(templates)` — formats slide templates into numbered instructions
  - `_parse_deck_response(response, company, vc_profile)` — extracts structured content from Claude response into PitchDeck model

  **IMPORTANT DESIGN DECISION**: Use a single generation call for the full deck (not per-slide) to ensure narrative coherence and transitions. The response will be large but within Claude's output limits at 8096 tokens. If needed, increase `max_tokens` to 16384.

  **Alternative approach if structured output is unreliable**: Generate as Markdown with clear delimiters, then parse. This is more robust for very long outputs:
  ```python
  # Fallback: Generate Markdown, parse manually
  # Use XML-tagged sections for reliable parsing:
  # <slide number="1" type="cover">
  #   <title>...</title>
  #   <bullets>...</bullets>
  #   <speaker_notes>...</speaker_notes>
  # </slide>
  ```

- **GOTCHA**:
  - `client.messages.parse()` with `output_format=PitchDeck` gives typed Pydantic output BUT cannot stream simultaneously. For a CLI with progress feedback, use regular `client.messages.create()` and parse manually, or accept no streaming.
  - Prompt caching minimum is 1,024 tokens for Sonnet 4.6 — company docs will easily exceed this.
  - `max_tokens=8096` may not be enough for 15 slides with full speaker notes. Test and increase to 16384 if truncated.
  - The `ANTHROPIC_API_KEY` env var must be set. Raise a clear error if missing.
  - Cost estimate per full deck generation: ~$0.10-0.30 with Sonnet 4.6 + caching
- **VALIDATE**: `python -c "from pitchdeck.engine.narrative import generate_deck; print('OK')"` — import check only; full test requires API key

### Task 11: CREATE `src/pitchdeck/output/markdown.py` — Markdown Deck Output

- **ACTION**: Render a PitchDeck model as a well-formatted Markdown file
- **IMPLEMENT**:
  ```python
  from pitchdeck.models import PitchDeck

  def render_markdown(deck: PitchDeck) -> str:
      """Render a PitchDeck as formatted Markdown."""
      lines = [
          f"# {deck.company_name} — Pitch Deck",
          f"**Target**: {deck.target_vc}",
          f"**Generated**: {deck.generated_at}",
          "",
          f"## Narrative Arc",
          f"{deck.narrative_arc}",
          "",
          "---",
          "",
      ]

      for slide in deck.slides:
          lines.extend([
              f"## Slide {slide.slide_number}: {slide.title}",
              f"*Type: {slide.slide_type}*",
              "",
              f"**{slide.headline}**",
              "",
          ])

          if slide.bullets:
              for bullet in slide.bullets:
                  lines.append(f"- {bullet}")
              lines.append("")

          if slide.metrics:
              lines.append("**Key Metrics:**")
              for metric in slide.metrics:
                  lines.append(f"- {metric}")
              lines.append("")

          if slide.speaker_notes:
              lines.extend([
                  "<details>",
                  "<summary>Speaker Notes</summary>",
                  "",
                  slide.speaker_notes,
                  "",
                  "</details>",
                  "",
              ])

          if slide.vc_alignment_notes:
              lines.append(f"> **VC Alignment**: {'; '.join(slide.vc_alignment_notes)}")
              lines.append("")

          if slide.transition_to_next:
              lines.append(f"*Transition: {slide.transition_to_next}*")
              lines.append("")

          lines.extend(["---", ""])

      if deck.gaps_identified:
          lines.extend([
              "## Information Gaps",
              "",
              "The following data points were missing and could strengthen the deck:",
              "",
          ])
          for gap in deck.gaps_identified:
              lines.append(f"- [ ] {gap}")
          lines.append("")

      return "\n".join(lines)

  def save_markdown(deck: PitchDeck, path: str) -> None:
      """Save deck as Markdown file."""
      content = render_markdown(deck)
      with open(path, "w") as f:
          f.write(content)
  ```
- **ALSO**: Create `src/pitchdeck/output/__init__.py` re-exporting `render_markdown`, `save_markdown`
- **GOTCHA**: Use `<details>` HTML tags for speaker notes — they render as collapsible sections in GitHub Markdown and most viewers. Ensure proper newlines around HTML tags for Markdown rendering.
- **VALIDATE**: `python -c "from pitchdeck.output import render_markdown; print('OK')"`

### Task 12: CREATE `src/pitchdeck/cli.py` — Typer CLI Application

- **ACTION**: Create the main CLI entry point that orchestrates the full pipeline
- **IMPLEMENT**:
  ```python
  import typer
  from typing import Annotated, Optional
  from pathlib import Path
  from rich.console import Console
  from rich.progress import Progress, SpinnerColumn, TextColumn
  import sys

  app = typer.Typer(
      name="pitchdeck",
      help="Generate investor-grade pitch decks from company documents.",
      rich_markup_mode="rich",
  )
  console = Console()

  @app.command()
  def generate(
      input_files: Annotated[
          list[str],
          typer.Argument(help="Paths to company PDFs or DOCXs"),
      ],
      vc: Annotated[
          str,
          typer.Option("--vc", "-v", help="VC profile name (without .yaml)"),
      ] = "earlybird",
      output: Annotated[
          str,
          typer.Option("--output", "-o", help="Output Markdown file path"),
      ] = "deck.md",
      skip_gaps: Annotated[
          bool,
          typer.Option("--skip-gaps", help="Skip interactive gap-filling"),
      ] = False,
  ):
      """Generate a pitch deck from company documents."""
      from pitchdeck.parsers import extract_document
      from pitchdeck.profiles import load_vc_profile
      from pitchdeck.engine.slides import get_slide_templates
      from pitchdeck.engine.gaps import detect_gaps, fill_gaps_interactive
      from pitchdeck.engine.narrative import generate_deck
      from pitchdeck.output import save_markdown
      from pitchdeck.models import CompanyProfile
      import os

      # Check API key
      if not os.environ.get("ANTHROPIC_API_KEY"):
          console.print("[red]Error: ANTHROPIC_API_KEY environment variable not set[/red]")
          raise typer.Exit(1)

      # 1. Parse documents
      console.print(f"[bold]Parsing {len(input_files)} document(s)...[/bold]")
      combined_text = ""
      for path in input_files:
          try:
              text = extract_document(path)
              combined_text += f"\n\n--- Document: {Path(path).name} ---\n\n{text}"
              console.print(f"  [green]OK[/green] {path} ({len(text)} chars)")
          except Exception as e:
              console.print(f"  [red]FAIL[/red] {path}: {e}")
              raise typer.Exit(1)

      # 2. Load VC profile
      console.print(f"\n[bold]Loading VC profile: {vc}[/bold]")
      try:
          vc_profile = load_vc_profile(vc)
          console.print(f"  [green]OK[/green] {vc_profile.name} ({len(vc_profile.thesis_points)} thesis points)")
      except Exception as e:
          console.print(f"  [red]FAIL[/red] {e}")
          raise typer.Exit(1)

      # 3. Build initial company profile from extracted text
      # For MVP, create a minimal profile from the raw text
      # The narrative engine will extract structured data from the text
      company = CompanyProfile(
          name="",  # will be filled by gap detection or LLM
          product_name="",
          one_liner="",
          founded_year=0,
          employee_count=0,
          revenue_eur=0,
          revenue_type="revenue",
          funding_stage="bootstrapped",
          raw_document_text=combined_text,
      )

      # 4. Detect and fill gaps
      templates = get_slide_templates(vc_profile)
      gaps = detect_gaps(company, templates)
      if gaps and not skip_gaps:
          console.print(f"\n[bold yellow]Found {len(gaps)} information gaps:[/bold yellow]")
          company = fill_gaps_interactive(company, gaps)
      elif gaps:
          console.print(f"\n[dim]Skipping {len(gaps)} gaps (--skip-gaps)[/dim]")

      # 5. Generate deck
      console.print(f"\n[bold]Generating {len(templates)}-slide deck...[/bold]")
      with Progress(
          SpinnerColumn(),
          TextColumn("[progress.description]{task.description}"),
          console=console,
      ) as progress:
          task = progress.add_task("Generating slides with Claude...", total=None)
          deck = generate_deck(company, vc_profile, templates)
          progress.remove_task(task)

      # 6. Save output
      save_markdown(deck, output)
      console.print(f"\n[bold green]Deck saved to {output}[/bold green]")
      console.print(f"  Slides: {len(deck.slides)}")
      if deck.gaps_identified:
          console.print(f"  [yellow]Remaining gaps: {len(deck.gaps_identified)}[/yellow]")

  @app.command()
  def profiles():
      """List available VC profiles."""
      from pitchdeck.profiles import list_profiles
      available = list_profiles()
      if not available:
          console.print("[yellow]No profiles found in profiles/ directory[/yellow]")
      else:
          console.print("[bold]Available VC profiles:[/bold]")
          for name in available:
              console.print(f"  - {name}")

  if __name__ == "__main__":
      app()
  ```
- **GOTCHA**: Lazy imports inside commands (not at top of file) — avoids slow startup from pymupdf import. Use `raise typer.Exit(1)` not `sys.exit(1)` for proper Typer error handling. The `console` must be shared between progress bars and prints.
- **VALIDATE**: `python -m pitchdeck --help` — should show help text with `generate` and `profiles` commands

### Task 13: CREATE Engine `__init__.py` files — Package Structure

- **ACTION**: Create all remaining `__init__.py` files to complete the package
- **IMPLEMENT**:
  - `src/pitchdeck/engine/__init__.py` — empty or re-export key functions
  - `src/pitchdeck/parsers/__init__.py` — already covered in Task 5, verify re-exports
  - `src/pitchdeck/profiles/__init__.py` — already covered in Task 6, verify re-exports
  - `src/pitchdeck/output/__init__.py` — already covered in Task 11, verify re-exports
- **VALIDATE**: `python -c "from pitchdeck.engine.narrative import generate_deck; from pitchdeck.parsers import extract_document; from pitchdeck.profiles import load_vc_profile; from pitchdeck.output import render_markdown; print('All imports OK')"`

### Task 14: CREATE Tests — Unit Test Suite

- **ACTION**: Create comprehensive unit tests for all modules
- **IMPLEMENT**: Using pytest. Create these test files:

  **`tests/__init__.py`** — empty

  **`tests/conftest.py`** — shared fixtures:
  ```python
  import pytest
  from pitchdeck.models import CompanyProfile, VCProfile, SlideContent, PitchDeck

  @pytest.fixture
  def sample_company():
      return CompanyProfile(
          name="Neurawork",
          product_name="NeuraPlox",
          one_liner="The AI Control Plane for European SMEs",
          founded_year=2024,
          employee_count=20,
          revenue_eur=2300000,
          revenue_type="revenue",
          growth_rate_yoy=None,  # gap
          customer_count=4,
          funding_stage="bootstrapped",
          raw_document_text="Sample document text...",
      )

  @pytest.fixture
  def sample_vc_profile(tmp_path):
      # Create a temp YAML profile
      ...
  ```

  **`tests/test_models.py`** — test Pydantic model validation:
  - Valid model creation
  - Required field enforcement
  - Type coercion
  - Default values
  - model_copy with updates

  **`tests/test_parsers.py`** — test document parsers:
  - PDF extraction (mock pymupdf4llm)
  - DOCX extraction (create small test DOCX)
  - Unsupported format error
  - File not found error
  - Unified extract_document dispatch

  **`tests/test_profiles.py`** — test profile loading:
  - Load valid YAML profile
  - Profile not found error with available list
  - Pydantic validation of profile fields
  - list_profiles returns sorted names

  **`tests/test_engine.py`** — test engine components:
  - Slide template count and structure
  - get_slide_templates filters by VC preferences
  - Gap detection finds missing fields
  - Gap detection skips filled fields
  - Narrative arc generation (mock Claude API)

  **`tests/test_output.py`** — test Markdown rendering:
  - render_markdown produces valid Markdown
  - All slides present in output
  - Speaker notes in details tags
  - Gaps section rendered when gaps exist
  - save_markdown writes to file

- **GOTCHA**: Mock the Anthropic API in tests — never make real API calls in unit tests. Use `unittest.mock.patch` or `pytest-mock`. For PDF tests, mock `pymupdf4llm.to_markdown` rather than requiring a real PDF. For DOCX tests, create a minimal DOCX in the fixture using python-docx.
- **VALIDATE**: `python -m pytest tests/ -v` — all tests pass

---

## Testing Strategy

### Unit Tests to Write

| Test File | Test Cases | Validates |
|-----------|-----------|-----------|
| `tests/test_models.py` | Valid/invalid construction, defaults, type coercion, model_copy | Pydantic data models |
| `tests/test_parsers.py` | PDF extraction, DOCX extraction, error handling, dispatch | Document parsing |
| `tests/test_profiles.py` | YAML loading, validation, not-found, list profiles | Profile system |
| `tests/test_engine.py` | Templates, gap detection, narrative generation (mocked) | Core engine logic |
| `tests/test_output.py` | Markdown rendering, file saving, section formatting | Output generation |

### Edge Cases Checklist

- [ ] Empty document (0 text extracted from PDF/DOCX)
- [ ] Very large document (>100K chars — test prompt caching threshold)
- [ ] Missing ANTHROPIC_API_KEY environment variable
- [ ] Corrupted/password-protected PDF
- [ ] DOCX with no headings (all body paragraphs)
- [ ] VC profile with empty thesis_points list
- [ ] All gaps skipped (--skip-gaps flag)
- [ ] User Ctrl+C during interactive gap filling
- [ ] Claude API rate limit / timeout
- [ ] Claude response truncated (max_tokens too low)
- [ ] Profile YAML with unquoted boolean-like values ("No", "Yes")
- [ ] Multiple input files with overlapping content

---

## Validation Commands

### Level 1: STATIC_ANALYSIS

```bash
python -m py_compile src/pitchdeck/cli.py && python -m py_compile src/pitchdeck/models.py && python -m py_compile src/pitchdeck/engine/narrative.py
```

**EXPECT**: Exit 0, no syntax errors

### Level 2: IMPORT_CHECK

```bash
python -c "from pitchdeck.cli import app; from pitchdeck.models import PitchDeck; from pitchdeck.parsers import extract_document; from pitchdeck.profiles import load_vc_profile; from pitchdeck.engine.narrative import generate_deck; from pitchdeck.output import render_markdown; print('All imports OK')"
```

**EXPECT**: Prints "All imports OK"

### Level 3: UNIT_TESTS

```bash
python -m pytest tests/ -v --tb=short
```

**EXPECT**: All tests pass

### Level 4: CLI_SMOKE_TEST

```bash
python -m pitchdeck --help && python -m pitchdeck profiles
```

**EXPECT**: Help text displays correctly, profiles command lists "earlybird"

### Level 5: INSTALL_TEST

```bash
pip install -e ".[dev]" && pitchdeck --help
```

**EXPECT**: Package installs, entry point works

### Level 6: INTEGRATION_TEST (requires ANTHROPIC_API_KEY)

```bash
# Create a minimal test PDF first, then:
pitchdeck generate test_doc.pdf --vc earlybird --output test_deck.md
cat test_deck.md | head -50
```

**EXPECT**: Generates Markdown deck with 15 slides, speaker notes, VC alignment

---

## Acceptance Criteria

- [ ] `pip install -e ".[dev]"` installs without errors
- [ ] `pitchdeck --help` shows generate and profiles commands
- [ ] `pitchdeck profiles` lists "earlybird"
- [ ] PDF and DOCX documents can be parsed to text
- [ ] Earlybird YAML profile loads and validates
- [ ] Gap detection identifies missing CompanyProfile fields
- [ ] Interactive gap filling works via questionary prompts
- [ ] Claude API generates structured slide content (15 slides)
- [ ] Markdown output contains all slides with speaker notes
- [ ] All unit tests pass with mocked API
- [ ] No hardcoded API keys or secrets in source

---

## Completion Checklist

- [ ] All 14 tasks completed in dependency order
- [ ] Each task validated immediately after completion
- [ ] Level 1: Static analysis passes
- [ ] Level 2: All imports succeed
- [ ] Level 3: Unit tests pass
- [ ] Level 4: CLI smoke test passes
- [ ] Level 5: Package installation works
- [ ] All acceptance criteria met

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Claude generates generic/fluffy content | MEDIUM | HIGH | Constrain with specific company data, VC thesis, and slide-level requirements; validate each slide has metrics |
| Structured output parsing fails for 15 slides | MEDIUM | MEDIUM | Fallback to XML-tagged Markdown generation with manual parsing; test with increasing slide counts |
| pymupdf4llm AGPL license concern | LOW | MEDIUM | For Phase 1 (internal use) AGPL is fine; evaluate pypdf (MIT) if distributing commercially |
| 8096 max_tokens truncates 15-slide output | MEDIUM | HIGH | Increase to 16384; if still insufficient, generate in two batches (slides 1-8, 9-15) with shared context |
| Company docs too large for context window | LOW | MEDIUM | pymupdf4llm output is compact; 200K context fits ~500 pages; if exceeded, summarize with Claude first |
| Interactive prompts break in non-TTY environments | LOW | LOW | Add `--skip-gaps` flag and `--company-json` flag for non-interactive use |
| YAML profile values parsed incorrectly | LOW | LOW | ruamel.yaml (YAML 1.2) avoids boolean coercion; Pydantic validates types on load |

---

## Notes

### Architecture Decisions

1. **Single generation call vs per-slide**: Generating all slides in one API call ensures narrative coherence and transitions. Per-slide generation would allow streaming progress but risks disjointed narrative.

2. **src-layout**: Using `src/pitchdeck/` layout (PEP 517) instead of flat `pitchdeck/` — prevents accidental imports from the development directory and follows modern Python packaging best practices.

3. **Pydantic for everything**: Using Pydantic models for company data, VC profiles, slide content, and API responses. This gives us validation, serialization, and type safety throughout.

4. **Claude Sonnet 4.6 over Opus**: Sonnet is 60% cheaper with comparable quality for structured generation tasks. Opus reserved for future validation/scoring phase where qualitative judgment matters more.

5. **YAML over JSON for profiles**: YAML supports comments (documenting thesis points), is more human-readable, and round-trips with ruamel.yaml preserving formatting.

### Future Phase Considerations

- **Phase 2 (Validation)**: Will consume `PitchDeck` model and score each `SlideContent` against rubric dimensions. The `vc_alignment_notes` field on SlideContent is prep for this.
- **Phase 3 (Export)**: Will add `output/json_export.py` and `output/qa_document.py`. The `PitchDeck` model already serializes to JSON via Pydantic.
- **Phase 4 (Visual)**: The Markdown output with structured sections is already parseable for Imagen3 XML prompt generation.

### Key Library Versions (pinned from research)

| Library | Version | License |
|---------|---------|---------|
| anthropic | >=0.82.0 | MIT |
| pymupdf | >=1.27 | AGPL 3.0 |
| pymupdf4llm | >=0.0.17 | AGPL 3.0 |
| python-docx | >=1.2.0 | MIT |
| typer | >=0.24.0 | MIT |
| ruamel.yaml | >=0.19 | MIT |
| pydantic | >=2.0 | MIT |
| questionary | >=2.0 | MIT |
