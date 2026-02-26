# External Integrations

**Analysis Date:** 2026-02-26

## APIs & External Services

**Anthropic Claude API:**
- Claude 3.5 Sonnet (`claude-sonnet-4-6`) - LLM for pitch deck generation and validation scoring
  - SDK: `anthropic` (0.82.0+)
  - Auth: `ANTHROPIC_API_KEY` environment variable
  - Endpoints:
    - Deck generation: `messages.create()` with prompt caching (see `src/pitchdeck/engine/narrative.py` line 108)
    - Validation scoring: `messages.create()` with `temperature=0.0` (see `src/pitchdeck/engine/validator.py`)
  - Cache Control: Ephemeral prompt caching enabled for VC context (repeated across generation calls)
  - Error handling: Maps AuthenticationError, RateLimitError, APITimeoutError, APIStatusError to user-facing PitchDeckError messages

## Data Storage

**Databases:**
- Not applicable - no persistent database used

**File Storage:**
- **Local filesystem only** (no cloud storage integration)
  - Input: PDF/DOCX documents parsed from local paths
  - Output: Generated `.md` (Markdown) and `.json` (PitchDeck) files written to local filesystem
  - Profiles: YAML files in `profiles/` directory (loaded at startup via `src/pitchdeck/profiles/loader.py`)

**Caching:**
- **Anthropic Ephemeral Prompt Cache** - Not persistent, used within single generation session
  - Applied to system context messages in `src/pitchdeck/engine/narrative.py` line 72
  - Reduces token usage for repeated VC profile context

## Authentication & Identity

**Auth Provider:**
- None (no user authentication system)

**API Authentication:**
- Anthropic API: ANTHROPIC_API_KEY
  - Validated at CLI startup (line 56 in `cli.py`)
  - Validated before validation runs (line 289 in `cli.py`)
  - Missing key blocks: `pitchdeck generate` (always) and `pitchdeck validate` (unless --skip-llm used)

## Monitoring & Observability

**Error Tracking:**
- None (no external error tracking service)

**Logs:**
- Console output via Rich library
  - Success/failure messages prefixed with [green], [red], [yellow] color codes
  - Progress indicators with spinner columns during Claude API calls
  - Validation errors include per-field JSON validation errors (line 251-253 in `cli.py`)
  - All errors raise `typer.Exit(1)` to signal failure to shell

**Structured Logging:**
- None - uses console print statements only

## CI/CD & Deployment

**Hosting:**
- CLI application (runs locally via `pitchdeck` command)
- No web server, no cloud deployment required
- Installed via: `pip install -e ".[dev]"`

**CI Pipeline:**
- Not detected - no `.github/workflows/` or similar CI config found

**Testing Infrastructure:**
- pytest runs tests in `tests/` directory
- All Claude API calls are mocked (see CLAUDE.md: "No integration tests hit the real Claude API")
- No integration tests against real Anthropic API

## Environment Configuration

**Required env vars:**
- `ANTHROPIC_API_KEY` - Anthropic API authentication key
  - Format: typically `sk-ant-...`
  - Must be set before running `generate` or `validate` (unless --skip-llm)

**Optional env vars:**
- None detected - all CLI options use flags/arguments instead

**Secrets location:**
- `.env` file (auto-loaded via `python-dotenv` in `cli.py` line 9)
- `.env` not committed to git (standard best practice)
- Example: `ANTHROPIC_API_KEY=sk-ant-...`

**Configuration files:**
- `pyproject.toml` - Project and build metadata (not a secret file)
- `profiles/<name>.yaml` - VC profile definitions (committed, no secrets)

## Webhooks & Callbacks

**Incoming:**
- None - CLI application, no HTTP endpoints

**Outgoing:**
- None detected

## Document Parsing

**PDF Extraction:**
- Library: `pymupdf4llm` 0.0.17+
- Approach: Converts PDFs to Markdown using `pymupdf4llm.to_markdown(path)`
- Format: Structure-preserving Markdown (headings, tables, lists preserved)
- Entry point: `src/pitchdeck/parsers/pdf.py::extract_pdf()`

**DOCX Extraction:**
- Library: `python-docx` 1.2.0+
- Approach: Parses paragraphs, extracts heading hierarchy (Heading 1-6), preserves structure
- Format: Markdown-formatted output with `#` headings
- Entry point: `src/pitchdeck/parsers/docx_parser.py::extract_docx()`

**Router:**
- Dispatch in `src/pitchdeck/parsers/__init__.py::extract_document()`
  - `.pdf` files → `extract_pdf()`
  - `.docx` / `.doc` files → `extract_docx()`
  - Other formats raise `DocumentParseError`

## Data Flow: Generate Command

1. User runs: `pitchdeck generate company.pdf --vc earlybird`
2. CLI checks `ANTHROPIC_API_KEY` environment variable (line 56)
3. Document is parsed to text (PDF/DOCX → Markdown via pymupdf4llm/python-docx)
4. VC profile `earlybird.yaml` is loaded and validated (line 88)
5. Gap detection runs against CompanyProfile template (optional: --skip-gaps)
6. Interactive gap-filling prompts user for missing fields (line 121)
7. Claude API call in `generate_deck()`:
   - Sends document text + company profile + VC context via ephemeral cache
   - Model: `claude-sonnet-4-6`, max_tokens: 16384
   - Returns JSON with slides, narrative arc, gaps identified
8. JSON response is parsed and validated into `PitchDeck` model
9. Outputs saved:
   - `deck.md` - Markdown rendering of deck (via `src/pitchdeck/output/markdown.py`)
   - `deck.json` - Structured PitchDeck model (Pydantic `model_dump_json()`)

## Data Flow: Validate Command

1. User runs: `pitchdeck validate deck.json --vc earlybird --threshold 60`
2. `deck.json` is loaded and validated into `PitchDeck` model (line 244)
3. VC profile is loaded (line 266)
4. Rule-based validation runs (deterministic, no API key needed):
   - Completeness checks (title, headline, bullets, metrics)
   - Metrics density checks
   - Custom checks from VC profile
5. LLM validation runs (if --skip-llm not set):
   - Checks `ANTHROPIC_API_KEY` (line 289)
   - Claude API call to score:
     - Narrative coherence
     - Thesis alignment
     - Common mistakes
   - Model: `claude-sonnet-4-6`, temperature: 0.0
6. Weighted scores calculated (see `SCORING_DIMENSIONS` in `src/pitchdeck/engine/validator.py` line 33-39):
   - Completeness: 25% (rule-based)
   - Metrics density: 20% (rule-based)
   - Narrative coherence: 20% (LLM)
   - Thesis alignment: 20% (LLM)
   - Common mistakes: 15% (LLM)
7. Overall score computed and compared to threshold
8. Report generated and saved (via `src/pitchdeck/output/validation_report.py`)

## VC Profile Integration

**Profile Source:**
- YAML files in `profiles/` directory
- Schema validated by `VCProfile` Pydantic model (`src/pitchdeck/models.py`)

**Profile Usage:**

- **Generation:** VC context passed to Claude via system message (line 68-70 in `src/pitchdeck/engine/narrative.py`)
  - Includes: name, fund name, stage/sector/geo focus, thesis points, portfolio companies, deck preferences, custom checks

- **Validation:** Custom checks extracted as strings (line 167-170 in `src/pitchdeck/engine/narrative.py`)
  - Custom checks matched against deck content
  - Example from `earlybird.yaml`: "European sovereignty angle must be present", "Bottom-up market sizing required"

**Profile Loading:**
- Loader: `src/pitchdeck/profiles/loader.py::load_vc_profile(name)`
- Default search path: `profiles/` (relative to project root)
- Profiles discoverable via: `pitchdeck profiles` command (line 184 in `cli.py`)

**Example Profile:**
- `profiles/earlybird.yaml` - Earlybird Capital Fund VII profile
  - 7 thesis points (European sovereignty, category creation, capital efficiency, etc.)
  - 15-slide preferred deck structure
  - 8 metrics emphasis areas (ARR, NDR, burn multiple, etc.)
  - 6 custom checks for validation

---

*Integration audit: 2026-02-26*
