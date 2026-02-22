# CLAUDE.md

AI assistant instructions for the Capital pitchdeck project.

## Project overview

`pitchdeck` is a CLI tool that generates and validates investor pitch decks for B2B AI/SaaS companies. It uses Claude (via the Anthropic API) for deck generation and LLM-powered scoring.

Three user-facing commands: `generate`, `validate`, and `profiles`. See `README.md` for usage.

## Architecture

```
src/pitchdeck/
  cli.py                        — Typer app: generate, validate, profiles commands
  models.py                     — All Pydantic models (source of truth for data shapes)
  engine/
    gaps.py                     — Gap detection and interactive filling
    narrative.py                — Claude API call for deck generation
    slides.py                   — SLIDE_TEMPLATES constant
    validator.py                — Validation engine (rule-based + LLM scoring)
  output/
    markdown.py                 — Deck Markdown renderer
    validation_report.py        — Validation report Markdown renderer
  parsers/                      — PDF/DOCX document extraction
  profiles/                     — VC profile YAML loader
profiles/                       — VC profile YAML files (e.g. earlybird.yaml)
tests/                          — pytest tests
```

## Key conventions

**Models**: All Pydantic models live in `src/pitchdeck/models.py`. Use `List[X]` (from `typing`) for list fields, `Field(default_factory=list)` for mutable defaults. Score fields use `Field(ge=0, le=100)`. Use `@computed_field` for derived properties (see `DeckValidationResult.overall_score` and `pass_fail` for the pattern). Use `@model_validator(mode="after")` for cross-field invariants (see `DeckValidationResult._check_weight_sum`).

**CLI**: Typer commands use `Annotated` for all options and arguments. Follow the pattern in `cli.py`. Use Rich console for output — green for success, red for failure, yellow for warnings.

**Engine modules**: Each engine function takes typed model arguments and returns typed models. API key is checked at call time; raise `PitchDeckError` with a clear message if missing.

**Claude API calls**: Use `temperature=0.0` for scoring/validation. Use ephemeral prompt caching for context that repeats across calls. See `src/pitchdeck/engine/narrative.py` for the pattern.

**JSON extraction**: Extract JSON from Claude responses with a regex `\{[\s\S]*\}` before parsing. See `narrative.py` for the error-handling pattern.

**Tests**: Class-based pytest. Mock all Claude API calls — no real API calls in tests. See `tests/test_engine.py` and `tests/test_validator.py` for patterns.

**Profiles**: VC profiles are YAML files in `profiles/`. The `VCProfile` model (in `models.py`) is the schema. `custom_checks` is a list of keyword strings used by the validator.

## Adding a new VC profile

Create `profiles/<name>.yaml` following the `VCProfile` schema. Run `pitchdeck profiles` to confirm it appears.

## Running tests

```bash
pytest
```

No integration tests hit the real Claude API. All LLM calls are mocked.

## Dependencies

Managed in `pyproject.toml`. No new runtime dependencies without discussion — the current set covers all Phase 1 and Phase 2 functionality.
