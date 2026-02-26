# Architecture

**Analysis Date:** 2026-02-26

## Pattern Overview

**Overall:** Layered application with three primary pipelines: document parsing → deck generation → validation. Each pipeline transforms data through typed models with clear boundaries between concerns.

**Key Characteristics:**
- **Model-driven design**: All data shapes defined in `src/pitchdeck/models.py` using Pydantic BaseModel; single source of truth for schema
- **Plugin-based generation**: Slide templates, VC profiles, and document parsers pluggable; new formats/profiles don't require code changes
- **Claude API-centric**: Both generation and validation pipeline rely on Claude for content creation and LLM-powered scoring
- **Explicit error hierarchy**: Custom exception types (`PitchDeckError`, `DocumentParseError`, `ProfileNotFoundError`) for specific failure modes
- **Deterministic + LLM hybrid validation**: Rule-based checks run without API; LLM scoring optional for deeper analysis

## Layers

**Data Layer (Models):**
- Purpose: Define all data structures and validation rules for company profiles, VC preferences, decks, and validation results
- Location: `src/pitchdeck/models.py`
- Contains: 20+ Pydantic models including `CompanyProfile`, `PitchDeck`, `DeckValidationResult`, `VCProfile`, error classes
- Depends on: Pydantic, typing stdlib
- Used by: All other layers

**Input/Parsing Layer:**
- Purpose: Extract raw text from user documents (PDF, DOCX) and load VC profile YAML configurations
- Location: `src/pitchdeck/parsers/`, `src/pitchdeck/profiles/loader.py`
- Contains: Document extraction (PDF via PyMuPDF, DOCX via python-docx), YAML profile loader with Pydantic validation
- Depends on: Models, PyMuPDF, python-docx, ruamel.yaml
- Used by: CLI generate command

**Generation Engine:**
- Purpose: Create investor pitch deck content using Claude API with contextual awareness of VC thesis
- Location: `src/pitchdeck/engine/`
  - `narrative.py`: Claude API call for full deck generation with ephemeral prompt caching
  - `gaps.py`: Gap detection and interactive CLI prompting to fill missing company data
  - `slides.py`: SLIDE_TEMPLATES constant (15-slide structure) and narrative arc definition
- Depends on: Models, anthropic SDK, questionary (for interactive prompts)
- Used by: CLI generate command

**Validation Engine:**
- Purpose: Score decks against VC-specific rubrics using both deterministic rules and Claude LLM
- Location: `src/pitchdeck/engine/validator.py`
- Contains: Five scoring dimensions (completeness, metrics_density, narrative_coherence, thesis_alignment, common_mistakes); rule-based checkers; LLM evaluator
- Depends on: Models, anthropic SDK, SLIDE_TEMPLATES
- Used by: CLI validate command

**Output Layer:**
- Purpose: Render scored/generated decks into human-readable formats
- Location: `src/pitchdeck/output/`
  - `markdown.py`: Render PitchDeck to formatted Markdown with speaker notes, metrics, transitions
  - `validation_report.py`: Render DeckValidationResult to scored report with per-slide breakdowns and prioritized improvements
- Depends on: Models
- Used by: CLI generate and validate commands

**CLI Layer:**
- Purpose: User-facing command interface with error handling, progress indicators, and formatted output
- Location: `src/pitchdeck/cli.py`
- Contains: Three Typer commands (`generate`, `validate`, `profiles`) with Rich console output
- Depends on: All layers, typer, rich, os/path
- Used by: End users via `pitchdeck` CLI command

## Data Flow

**Generate Pipeline:**

1. **CLI input**: User provides document paths, VC profile name, output destinations
2. **Parse documents**: `extract_document()` → combined raw text
3. **Load VC profile**: `load_vc_profile()` → VCProfile model with thesis points and deck preferences
4. **Build company skeleton**: CLI creates empty CompanyProfile with raw document text
5. **Gap detection**: `detect_gaps()` compares profile against slide template requirements
6. **Interactive filling**: If gaps found and not --skip-gaps, `fill_gaps_interactive()` prompts user for critical/important fields
7. **Get slide structure**: `get_slide_templates()` returns filtered 15-slide template list (may be subset per VC preferences)
8. **Claude generation**: `generate_deck()` calls Claude with system prompt + cached context (company doc + profiles) + user request for structured JSON
9. **JSON extraction**: Regex extracts JSON from Claude response before Pydantic parsing
10. **Save outputs**: Markdown rendered and JSON serialized to disk
11. **Return to CLI**: User sees deck location and any remaining gaps

**Validate Pipeline:**

1. **CLI input**: User provides deck JSON file path, VC profile, threshold (default 60), optional --skip-llm
2. **Load deck JSON**: `PitchDeck.model_validate_json()` deserializes and validates structure
3. **Load VC profile**: `load_vc_profile()` loads target VC thesis and custom checks
4. **Rule-based scoring** (always):
   - Per-slide checks: title/headline presence, bullet count, metrics presence against template
   - Completeness: slides have required narrative elements
   - Metrics density: count metrics per slide vs template needs
5. **LLM scoring** (if not --skip-llm):
   - Call Claude with cached VC context + full deck content
   - Evaluate narrative_coherence, thesis_alignment, common_mistakes dimensions
6. **Custom checks**: Iterate VC custom_checks strings against deck content with LLM assessment
7. **Aggregate scores**: Weighted sum of dimension scores (dimension.score * dimension.weight) → overall_score
8. **Determine pass/fail**: overall_score >= threshold → pass_fail boolean
9. **Render report**: Markdown report with summary, per-dimension breakdown, per-slide issues, prioritized improvements
10. **Save and display**: Write report to disk, print summary to CLI

**State Management:**

- **CompanyProfile**: Mutable during generation (gaps filled interactively); frozen once passed to Claude
- **PitchDeck**: Immutable output from Claude; never modified after generation
- **DeckValidationResult**: Immutable output from validation engine; computed properties (overall_score, pass_fail) derived from dimension_scores
- **VCProfile**: Loaded from YAML, immutable during execution; used as context/rules, never modified

## Key Abstractions

**SlideTemplate:**
- Purpose: Defines structural and content expectations for a single slide type (e.g., "traction", "team")
- Examples: `src/pitchdeck/engine/slides.py` SLIDE_TEMPLATES constant (cover, problem, solution, market-sizing, traction, etc.)
- Pattern: 15 fixed templates matching investor expectations for SaaS pitch decks; each specifies required_elements, optional_elements, metrics_needed, max_bullets, word_limit

**SlideContent:**
- Purpose: Concrete slide instance with generated content for a specific deck
- Examples: Generated by `generate_deck()` as list in PitchDeck.slides
- Pattern: slide_number, slide_type (ref to template), title, headline, bullets, metrics, speaker_notes, transition_to_next, vc_alignment_notes

**DimensionScore:**
- Purpose: Rubric dimension score with weight for weighted aggregation
- Examples: completeness (0.25), metrics_density (0.20), narrative_coherence (0.20), thesis_alignment (0.20), common_mistakes (0.15)
- Pattern: dimension name (Literal), score (0-100), weight (0.0-1.0), rationale string, evidence_found/evidence_missing lists

**GapQuestion:**
- Purpose: Prompt definition for missing company data
- Examples: `src/pitchdeck/engine/gaps.py` GAP_DEFINITIONS list (company name, product name, growth_rate, ndr_percent, etc.)
- Pattern: field name, question text, importance level (critical/important/nice-to-have), optional default or choices

**VCProfile:**
- Purpose: Configuration object for VC-specific generation and validation behavior
- Examples: `profiles/earlybird.yaml` loaded via `load_vc_profile()`
- Pattern: fund name, stage/sector/geo focus, thesis_points, deck_preferences (must_include_slides, narrative_style), custom_checks (list of check strings)

**DocumentParser (Plugin):**
- Purpose: Extract text from various document formats
- Examples: `parsers/pdf.py` (PyMuPDF-based), `parsers/docx_parser.py` (python-docx-based)
- Pattern: Format dispatch in `parsers/__init__.py` extract_document() function; each parser returns str; errors wrapped as DocumentParseError

## Entry Points

**CLI Application:**
- Location: `src/pitchdeck/cli.py`
- Triggers: `pitchdeck generate`, `pitchdeck validate`, `pitchdeck profiles` commands invoked by user
- Responsibilities: Parse CLI arguments, orchestrate layer calls, handle errors, format output for user

**Module Entry:**
- Location: `src/pitchdeck/__main__.py`
- Triggers: `python -m pitchdeck` or installed `pitchdeck` command
- Responsibilities: Import and run Typer app from cli.py

**API Integration:**
- Location: `src/pitchdeck/engine/narrative.py` generate_deck(), `src/pitchdeck/engine/validator.py` validate_deck()
- Triggers: Called by CLI commands after input preparation
- Responsibilities: Orchestrate Claude API calls and data transformations

## Error Handling

**Strategy:** Typed exception hierarchy with contextual information. CLI catches exceptions and provides user-friendly error messages with actionable hints.

**Patterns:**

- **PitchDeckError** (base): Used for application-level failures requiring user intervention (missing API key, invalid profile name)
  - `DocumentParseError(path, reason)`: File extraction failed with why
  - `ProfileNotFoundError(message)`: VC profile YAML not found; includes available options
  - Raised in engine functions; caught in CLI with typer.Exit(1)

- **Pydantic ValidationError**: Caught when model validation fails (e.g., invalid deck JSON schema); CLI shows first 5 field errors
  - Example: `DeckValidationResult.model_validator` ensures dimension weights sum to ~1.0

- **Anthropic SDK errors**: Caught for API failures:
  - `AuthenticationError`: ANTHROPIC_API_KEY missing or invalid
  - `RateLimitError`, `APITimeoutError`: Transient failures (user should retry)
  - `APIStatusError`: Server error (user should retry or report)
  - Wrapped in PitchDeckError with clear message

- **File I/O errors** (OSError): Caught for document parsing, profile loading, output writing; CLI shows permission/disk space hints

- **JSON parsing errors**: Regex extraction of JSON from Claude response fails → PitchDeckError with suggestion to check API key

## Cross-Cutting Concerns

**Logging:** Console output via Rich library. No persistent logs. Progress spinners for long-running operations (Claude API calls). Success/failure indicated by color: green (OK), red (FAIL), yellow (warning).

**Validation:** Enforced at model boundaries:
  - Input: Pydantic models validate on parse (document paths, API responses, profile YAML)
  - Output: Models serialize to JSON/Markdown; schema enforced on validate command (load previous deck for re-validation)
  - Rules: Template enforcement (slide types, required elements) in validation engine

**Authentication:** ANTHROPIC_API_KEY environment variable checked at two points:
  - `generate_deck()`: Raises PitchDeckError if missing
  - `validate_deck()`: Raises PitchDeckError if LLM scoring requested but key missing; rule-based OK without key
  - CLI prints hint to user when key missing

**Context management:** Claude API ephemeral prompt caching used for repeated context:
  - Company document text + profile JSON cached once, reused for multi-slide generation
  - Reduces latency and token cost for repeated API calls within single generation

**Rate limiting:** No built-in retry logic. Anthropic SDK raises RateLimitError; CLI advises user to retry command.

---

*Architecture analysis: 2026-02-26*
