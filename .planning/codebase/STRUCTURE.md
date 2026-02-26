# Codebase Structure

**Analysis Date:** 2026-02-26

## Directory Layout

```
/root/projects/capital/
├── src/pitchdeck/               # Main application package
│   ├── __init__.py              # Package init; __version__
│   ├── __main__.py              # Module entry point; imports and runs CLI
│   ├── cli.py                   # Typer CLI application; three commands (generate, validate, profiles)
│   ├── models.py                # All Pydantic data models (20+ classes); source of truth for data shapes
│   ├── engine/                  # Generation and validation engines
│   │   ├── __init__.py
│   │   ├── narrative.py         # Claude API call for deck generation; ephemeral caching
│   │   ├── validator.py         # Validation engine; rule-based and LLM scoring
│   │   ├── gaps.py              # Gap detection and interactive CLI prompting
│   │   └── slides.py            # SLIDE_TEMPLATES (15-slide structure); narrative arc definition
│   ├── output/                  # Output formatters
│   │   ├── __init__.py
│   │   ├── markdown.py          # Render PitchDeck to formatted Markdown
│   │   └── validation_report.py # Render DeckValidationResult to Markdown report
│   ├── parsers/                 # Document extraction plugins
│   │   ├── __init__.py          # Format dispatch; extract_document() function
│   │   ├── pdf.py               # PyMuPDF-based PDF extraction
│   │   └── docx_parser.py       # python-docx-based DOCX extraction
│   └── profiles/                # VC profile loading
│       ├── __init__.py
│       └── loader.py            # YAML loader with Pydantic validation; list_profiles()
├── profiles/                    # VC profile YAML files (configuration, not code)
│   └── earlybird.yaml           # Sample VC profile with thesis points and deck preferences
├── tests/                       # pytest test suite
│   ├── __init__.py
│   ├── conftest.py              # pytest fixtures; sample_company_profile, sample_vc_profile, sample_deck
│   ├── test_models.py           # Tests for Pydantic models; validation, computed fields
│   ├── test_engine.py           # Tests for slides, gaps, narrative generation logic
│   ├── test_validator.py        # Tests for validation engine; rule scoring, LLM mocking
│   ├── test_parsers.py          # Tests for PDF/DOCX extraction
│   ├── test_output.py           # Tests for Markdown rendering
│   ├── test_profiles.py         # Tests for VC profile loading
│   ├── test_cli_validate.py     # Integration tests for validate command
│   └── test_validation_report.py # Tests for validation report rendering
├── output/                      # Runtime output directory (generated decks, reports)
│   └── neuraplox/               # Sample company outputs
│       ├── current/             # Latest generated outputs
│       └── archive/             # Previous versions
├── pyproject.toml              # Package metadata; dependencies; pytest config
├── CLAUDE.md                   # AI assistant instructions; conventions and architecture reference
├── README.md                   # User guide; command documentation; typical workflow
└── .env                        # Environment configuration (not committed; contains ANTHROPIC_API_KEY)
```

## Directory Purposes

**src/pitchdeck/:**
- Purpose: Main application code; entry point is cli.py
- Contains: CLI commands, data models, generation/validation engines, formatters, document parsers, profile loader
- Key files: `cli.py` (entry), `models.py` (schema), `engine/` (business logic), `output/` (rendering)

**src/pitchdeck/engine/:**
- Purpose: Core generation and validation logic
- Contains: Narrative generation via Claude, gap detection, slide template definitions, validation scoring
- Key files:
  - `narrative.py`: Claude API call for full deck generation with cached context
  - `validator.py`: Five-dimension scoring (completeness, metrics_density, narrative_coherence, thesis_alignment, common_mistakes)
  - `slides.py`: SLIDE_TEMPLATES constant (cover, problem, solution, ..., ai-architecture); get_narrative_arc()
  - `gaps.py`: GAP_DEFINITIONS list; detect_gaps(), fill_gaps_interactive()

**src/pitchdeck/output/:**
- Purpose: Transform generated/validated data into human-readable formats
- Contains: Markdown deck renderer and validation report renderer
- Key files: `markdown.py` (slides → Markdown), `validation_report.py` (DeckValidationResult → report)

**src/pitchdeck/parsers/:**
- Purpose: Extract text from user-provided documents
- Contains: PDF and DOCX extraction implementations; format dispatch logic
- Key files: `pdf.py` (PyMuPDF), `docx_parser.py` (python-docx), `__init__.py` (dispatch)

**src/pitchdeck/profiles/:**
- Purpose: Load and validate VC profile configurations from YAML files
- Contains: Profile loader with Pydantic validation; list available profiles
- Key files: `loader.py` (load_vc_profile(), list_profiles())

**profiles/:**
- Purpose: VC profile configurations (data, not code)
- Contains: YAML files defining fund focus, thesis points, custom validation checks, deck preferences
- Key files: `earlybird.yaml` (sample profile)

**tests/:**
- Purpose: pytest test suite covering all modules
- Contains: Unit tests, integration tests, fixtures, mocks
- Key files:
  - `conftest.py`: pytest fixtures shared across tests (sample_company_profile, sample_vc_profile, sample_deck, mock Claude responses)
  - `test_engine.py`: Tests for slide templates, gap detection, narrative generation
  - `test_validator.py`: Tests for rule-based and LLM scoring
  - `test_cli_validate.py`: Integration tests for validate command with mocked API
  - Others: test_models.py, test_parsers.py, test_output.py, test_profiles.py, test_validation_report.py

**output/:**
- Purpose: Runtime output directory for generated decks and validation reports
- Contains: Generated Markdown files, JSON files, validation reports
- Note: Created at runtime; not committed to git

## Key File Locations

**Entry Points:**
- `src/pitchdeck/__main__.py`: Module entry point; `python -m pitchdeck` invokes this
- `src/pitchdeck/cli.py`: Typer CLI app; contains all three user commands (generate, validate, profiles)
- Command entry: `pyproject.toml` [project.scripts] defines `pitchdeck` command → `pitchdeck.cli:app`

**Configuration:**
- `pyproject.toml`: Package metadata, dependencies, pytest config, CLI entry point
- `CLAUDE.md`: AI assistant instructions; conventions reference
- `.env`: Environment variables (ANTHROPIC_API_KEY); not committed
- `profiles/earlybird.yaml`: VC profile example; loaded via `load_vc_profile("earlybird")`

**Core Logic:**
- `src/pitchdeck/models.py`: All 20+ Pydantic models; schema source of truth
- `src/pitchdeck/engine/narrative.py`: Claude API call for deck generation
- `src/pitchdeck/engine/validator.py`: Validation scoring engine
- `src/pitchdeck/engine/slides.py`: SLIDE_TEMPLATES constant (15 templates); narrative arc
- `src/pitchdeck/engine/gaps.py`: GAP_DEFINITIONS list; interactive prompting

**Output Rendering:**
- `src/pitchdeck/output/markdown.py`: PitchDeck → Markdown
- `src/pitchdeck/output/validation_report.py`: DeckValidationResult → report Markdown

**Document Input:**
- `src/pitchdeck/parsers/__init__.py`: Format dispatch
- `src/pitchdeck/parsers/pdf.py`: PDF text extraction
- `src/pitchdeck/parsers/docx_parser.py`: DOCX text extraction

**VC Profile Loading:**
- `src/pitchdeck/profiles/loader.py`: YAML loader; profile validation

**Testing:**
- `tests/conftest.py`: pytest fixtures
- `tests/test_engine.py`: Engine component tests
- `tests/test_validator.py`: Validation scoring tests
- `tests/test_cli_validate.py`: Integration tests for validate command

## Naming Conventions

**Files:**
- Module files: lowercase with underscores (e.g., `narrative.py`, `docx_parser.py`)
- Package init files: `__init__.py` with public exports
- Test files: `test_*.py` matching module name (e.g., `test_validator.py` for `validator.py`)
- Profile files: lowercase name + `.yaml` (e.g., `earlybird.yaml`)

**Directories:**
- Package directories: lowercase (e.g., `engine`, `output`, `parsers`, `profiles`)
- Feature grouping: logical cohesion (e.g., all Claude calls in `engine/`, all output in `output/`)

**Classes:**
- Pydantic models: PascalCase (e.g., `CompanyProfile`, `PitchDeck`, `DeckValidationResult`, `VCProfile`)
- Exception classes: PascalCase ending with Error (e.g., `PitchDeckError`, `DocumentParseError`, `ProfileNotFoundError`)

**Functions:**
- Snake_case (e.g., `detect_gaps()`, `generate_deck()`, `validate_deck()`, `extract_document()`, `load_vc_profile()`)
- Private functions: prefixed with underscore (e.g., `_score_slide_rules()`, `_build_slide_instructions()`)

**Constants:**
- UPPERCASE_WITH_UNDERSCORES (e.g., `SLIDE_TEMPLATES`, `COMMON_MISTAKES`, `GAP_DEFINITIONS`, `SCORING_DIMENSIONS`)
- Defined at module level for broad sharing; immutable

**Variables:**
- snake_case for local variables
- Type hints used throughout for clarity (e.g., `company: CompanyProfile`, `gaps: list[GapQuestion]`)

## Where to Add New Code

**New Feature (e.g., new command):**
- Primary code: `src/pitchdeck/cli.py` — add new @app.command() function
- New engine logic: `src/pitchdeck/engine/` — create new module or extend existing
- New models: `src/pitchdeck/models.py` — add Pydantic class for feature data
- Tests: `tests/test_cli_<feature>.py` — integration test for CLI command
- Unit tests: `tests/test_<module>.py` — tests for new engine functions

**New Slide Type (e.g., new template):**
- Add to `SLIDE_TEMPLATES` in `src/pitchdeck/engine/slides.py`
- Update `COMMON_MISTAKES` in `src/pitchdeck/engine/validator.py` if new patterns to check
- Add test to `tests/test_engine.py` for template structure
- No model changes needed (SlideTemplate already generic)

**New Document Format (e.g., PPTX support):**
- Create `src/pitchdeck/parsers/<format>.py` with `extract_<format>()` function
- Update dispatch in `src/pitchdeck/parsers/__init__.py` to handle new extension
- Add DocumentParseError for unsupported formats
- Add test to `tests/test_parsers.py`

**New VC Profile:**
- Create `profiles/<name>.yaml` following VCProfile schema
- Run `pitchdeck profiles` to verify it appears
- No code changes needed; profiles are data-driven
- Optional: add test to `tests/test_profiles.py` if profile-specific behavior

**New Validation Dimension:**
- Add dimension dict to `SCORING_DIMENSIONS` in `src/pitchdeck/engine/validator.py`
- Ensure weights sum to 1.0 across all dimensions
- Add DimensionName to `Literal` in `src/pitchdeck/models.py`
- Implement rule-based or LLM scorer in `validate_deck()` function
- Add test to `tests/test_validator.py`

**New Gap Question:**
- Add `GapQuestion` entry to `GAP_DEFINITIONS` in `src/pitchdeck/engine/gaps.py`
- Match field name to `CompanyProfile` attribute
- Tests auto-covered by existing gap detection tests

**Shared Utility/Helper:**
- Location: `src/pitchdeck/` directory; new module if widely used
- Import pattern: `from pitchdeck.<module> import <function>`
- Example: If creating a JSON extraction helper, create `src/pitchdeck/utils.py` and export from `__init__.py`

## Special Directories

**src/pitchdeck/__pycache__/:**
- Purpose: Python compiled bytecode cache
- Generated: Yes (created by Python interpreter)
- Committed: No (in .gitignore)

**tests/__pycache__/:**
- Purpose: Test compiled bytecode cache
- Generated: Yes
- Committed: No

**output/:**
- Purpose: Runtime-generated deck files (Markdown, JSON, reports)
- Generated: Yes (created by CLI commands)
- Committed: No (by policy; sample outputs exist for reference)

**profiles/:**
- Purpose: VC profile configuration files
- Generated: No (hand-authored YAML)
- Committed: Yes (part of product configuration)

**.pytest_cache/:**
- Purpose: pytest caching directory
- Generated: Yes
- Committed: No (in .gitignore)

**.coverage:**
- Purpose: Coverage report data
- Generated: Yes (by pytest-cov)
- Committed: Yes (artifact; aids in CI/metrics)

**.env:**
- Purpose: Environment variable file (ANTHROPIC_API_KEY)
- Generated: No (user-created)
- Committed: No (in .gitignore; sensitive data)

---

*Structure analysis: 2026-02-26*
