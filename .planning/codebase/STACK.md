# Technology Stack

**Analysis Date:** 2026-02-26

## Languages

**Primary:**
- Python 3.10+ - All CLI and engine code; required minimum version

**Secondary:**
- YAML - VC profile configuration files (`profiles/*.yaml`)
- Markdown - Output format for generated decks and validation reports
- JSON - Structured deck output and Claude API communication

## Runtime

**Environment:**
- Python 3.10+ (as specified in `pyproject.toml`)
- System requirements: PDF/DOCX parsing requires libraries with binary dependencies (pymupdf, python-docx)

**Package Manager:**
- pip (via `pyproject.toml` with setuptools/hatchling build backend)
- Lockfile: No lock file checked in; standard requirements are in `pyproject.toml`

## Frameworks

**Core:**
- Typer 0.24+ - CLI framework with Rich integration; defines three commands (`generate`, `validate`, `profiles`)
  - See `src/pitchdeck/cli.py` for command definitions
  - Enables `--help`, argument parsing via `Annotated`, Rich console output

**Data Validation:**
- Pydantic 2.0+ - All data models and validation
  - Source of truth: `src/pitchdeck/models.py`
  - Uses `@computed_field` for derived properties
  - Uses `@model_validator(mode="after")` for cross-field invariants
  - Required format validation (0-100 for score fields)

**Testing:**
- pytest 8.0+ - Test runner
- pytest-cov 5.0+ - Coverage reporting
- Config: `pyproject.toml` points to `tests/` directory with `pythonpath = ["src"]`

**Build/Dev:**
- hatchling - Build backend for wheel packaging
- python-dotenv 1.0+ - Auto-loads `.env` file at CLI startup (see line 9 of `cli.py`)

## Key Dependencies

**Critical:**

- **anthropic 0.82.0+** - Anthropic Python SDK for Claude API calls
  - Used in `src/pitchdeck/engine/narrative.py` for deck generation
  - Used in `src/pitchdeck/engine/validator.py` for LLM-based validation scoring
  - Handles: Message creation, prompt caching (cache_control), error types (AuthenticationError, RateLimitError, APITimeoutError, APIStatusError)

**Document Parsing:**

- **pymupdf 1.27+ (fitz)** - PDF text extraction (as dependency of pymupdf4llm)
- **pymupdf4llm 0.0.17+** - Markdown-optimized PDF extraction preserving structure
  - Imported in `src/pitchdeck/parsers/pdf.py`
  - Converts PDFs to Markdown for LLM consumption
  - Called as `pymupdf4llm.to_markdown(path)`

- **python-docx 1.2.0+** - DOCX document parsing
  - Imported in `src/pitchdeck/parsers/docx_parser.py`
  - Parses document paragraphs, extracts heading hierarchy, preserves structure
  - Main entry: `Document(path)` class

**Configuration & Output:**

- **ruamel.yaml 0.19+ (YAML)** - YAML file parsing for VC profiles
  - Imported in `src/pitchdeck/profiles/loader.py`
  - Parses `profiles/<name>.yaml` files with full Pydantic validation

**UI/Console:**

- **Rich** - Part of Typer[all]; provides colored console output
  - Used in `src/pitchdeck/cli.py` for console output (green/red/yellow)
  - Used for progress bars and spinners during deck generation

## Configuration

**Environment:**

- **ANTHROPIC_API_KEY** - Required for deck generation and LLM validation
  - Auto-loaded from `.env` file via `python-dotenv` at startup
  - Checked at runtime in `cli.py` (line 56) and validator (line 288)
  - Should be set as environment variable or in `.env` file

**Build:**

- `pyproject.toml` - Single source of truth for:
  - Project metadata (name, version, description)
  - Dependencies and optional dev dependencies
  - Build system (hatchling backend)
  - CLI entry point: `pitchdeck = "pitchdeck.cli:app"`
  - Pytest configuration: `testpaths`, `pythonpath`

## Platform Requirements

**Development:**

- Python 3.10 or higher (strictly enforced in `pyproject.toml`: `requires-python = ">=3.10"`)
- pip for package installation
- Anthropic API key (ANTHROPIC_API_KEY) for testing generation/validation with Claude
- Read/write permissions for input document files and output directories

**Production:**

- Python 3.10 runtime
- System libraries for PDF parsing (libmupdf or equivalent) — typically auto-installed via pymupdf wheel
- Anthropic API key for any `generate` or `validate` command that uses Claude
- Network access to Anthropic API endpoints (`https://api.anthropic.com`)
- Deployment: CLI tool (no web server or special hosting needed); runs locally

## API Integration

**Claude API Details:**

- **Model:** `claude-sonnet-4-6` (hardcoded in `src/pitchdeck/engine/narrative.py` line 109)
- **Max Tokens:** 16384 for deck generation
- **Temperature:** 0.0 for deterministic validation scoring
- **Cache Control:** Ephemeral prompt caching enabled for repeated VC context (system message in narrative.py line 72)
- **Error Handling:** Catches AuthenticationError, RateLimitError, APITimeoutError, APIStatusError with user-friendly messages

---

*Stack analysis: 2026-02-26*
