# Coding Conventions

**Analysis Date:** 2026-02-26

## Naming Patterns

**Files:**
- Module files use snake_case: `cli.py`, `models.py`, `narrative.py`, `validator.py`
- Package directories use snake_case: `engine/`, `output/`, `parsers/`, `profiles/`
- Test files: `test_<module>.py` (e.g., `test_models.py`, `test_engine.py`, `test_validator.py`)

**Functions:**
- Use snake_case: `generate_deck()`, `detect_gaps()`, `fill_gaps_interactive()`, `_parse_deck_response()`
- Private/internal functions prefixed with underscore: `_build_slide_instructions()`, `_score_slide_rules()`, `_parse_validation_response()`
- Command functions use present tense verbs: `generate()`, `validate()`, `profiles()`

**Variables:**
- Local variables use snake_case: `combined_text`, `vc_profile`, `slide_templates`, `dimension_scores`
- Constants use UPPER_CASE: `SYSTEM_PROMPT`, `SLIDE_TEMPLATES`, `SCORING_DIMENSIONS`, `GAP_DEFINITIONS`
- Loop variables use descriptive names: `slide` (not `s`), `gap_def` (not `g`), `template` (not `t`)

**Types and Classes:**
- Classes use PascalCase: `CompanyProfile`, `VCProfile`, `PitchDeck`, `SlideContent`, `DeckValidationResult`
- Exception classes also use PascalCase and end with "Error": `PitchDeckError`, `DocumentParseError`, `ProfileNotFoundError`
- Type aliases use PascalCase: `DimensionName` (Literal type alias)

## Code Style

**Formatting:**
- No explicit formatter configured (no .black, .ruff, or .eslintrc file)
- Imports follow Python style: standard library → third-party → local
- 4-space indentation (Python standard)
- Line length appears to be ~100 chars (observed in code samples like `cli.py`)
- String literals use double quotes for consistency

**Linting:**
- No linting tool configured in pyproject.toml or root directory
- Type hints are used throughout: function signatures include parameter and return types
- All functions have type hints: `def generate_deck(company: CompanyProfile, vc_profile: VCProfile, slide_templates: list[SlideTemplate]) -> PitchDeck:`

## Import Organization

**Order:**
1. Standard library: `import json`, `import os`, `import re`, `from datetime import datetime`
2. Third-party: `from pydantic import BaseModel, Field`, `from typer import Typer`, `from anthropic import Anthropic`
3. Local imports: `from pitchdeck.models import ...`, `from pitchdeck.engine.slides import ...`

**Path Aliases:**
- Imports use absolute paths from package root: `from pitchdeck.models import CompanyProfile` (not relative imports)
- Monolithic imports grouped by module: `from pitchdeck.models import (CompanyProfile, PitchDeckError, PitchDeck, ...)`

**Avoid:**
- Star imports (`from module import *`) — always use explicit imports

## Error Handling

**Patterns:**
- Raise custom exceptions for known error states: `raise PitchDeckError("message")` for user-facing errors
- Specific exception types for external API errors: `AuthenticationError`, `RateLimitError`, `APITimeoutError`, `APIStatusError` from Anthropic SDK
- Catch specific exceptions, not generic `Exception` (unless re-raising with context)
- All error messages are descriptive and actionable; include URLs or recovery suggestions where applicable

**Example from `cli.py`:**
```python
try:
    response = client.messages.create(...)
except AuthenticationError:
    raise PitchDeckError(
        "Invalid API key. Check ANTHROPIC_API_KEY at https://console.anthropic.com/"
    )
except RateLimitError:
    raise PitchDeckError(
        "Anthropic API rate limit hit. Wait a moment and try again."
    )
except APITimeoutError:
    raise PitchDeckError(
        "Anthropic API timed out. The document may be too large — "
        "try reducing input size."
    )
except APIStatusError as e:
    raise PitchDeckError(
        f"Anthropic API error (HTTP {e.status_code}): {e.message}"
    ) from e
```

**CLI Error Exit Pattern:**
- Use `typer.Exit(1)` to exit with error code 1
- Print user-friendly error message to console using Rich `console.print()` before exiting
- Color codes: `[red]` for failures, `[green]` for success, `[yellow]` for warnings, `[dim]` for verbose/secondary

## Logging

**Framework:** `Rich` console output (not a logging library)

**Patterns:**
- Use `console = Console()` instance from rich
- Log important milestones: `console.print("[bold]Parsing documents...[/bold]")`
- Use Rich markup for visual feedback: colors, bold, dim, progress bars
- No debug logging to files — only CLI output to user
- Example from `cli.py`:
  ```python
  console.print(f"[bold]Parsing {len(input_files)} document(s)...[/bold]")
  console.print(f"  [green]OK[/green] {path} ({len(text)} chars)")
  console.print(f"  [red]FAIL[/red] {path}: {e}")
  ```

## Comments

**When to Comment:**
- Module-level docstrings for all files: """Purpose of this module."""
- Function docstrings for public functions (single line is sufficient if clear)
- Inline comments only for non-obvious logic (e.g., regex patterns, heuristics)
- Avoid stating the obvious: `x = x + 1  # increment x` is not needed

**JSDoc/TSDoc:**
- Not applicable (Python project)
- Use Python docstrings instead (triple-quoted strings)
- Example from `models.py`:
  ```python
  class PitchDeckError(Exception):
      """Base exception for pitch deck generator."""
      pass
  ```

**Example of Good Inline Comment:**
```python
# Try to extract JSON from the response (Claude sometimes wraps in markdown)
json_match = re.search(r"\{[\s\S]*\}", raw_text)
```

## Function Design

**Size:**
- Functions are single-responsibility and typically 20-80 lines
- Long functions (>100 lines) are broken into helper functions (e.g., `_parse_deck_response()` is 68 lines but only handles one concern: JSON parsing)

**Parameters:**
- Use typed parameters with type hints
- Group related parameters (e.g., `company: CompanyProfile, vc_profile: VCProfile`)
- Avoid boolean flags when possible; use Enum or separate functions
- Cli functions use `Annotated` with Typer metadata:
  ```python
  def generate(
      input_files: Annotated[
          list[str],
          typer.Argument(help="Paths to company PDFs or DOCXs"),
      ],
      vc: Annotated[
          str,
          typer.Option("--vc", "-v", help="VC profile name (without .yaml)"),
      ] = "earlybird",
  ):
  ```

**Return Values:**
- Functions return typed objects (Pydantic models, lists, or None)
- Never return raw dicts or lists when a model exists
- Example: `generate_deck()` returns `PitchDeck` (model), not `dict`

## Module Design

**Exports:**
- No `__all__` declarations observed
- All public functions/classes are importable by name: `from pitchdeck.cli import app`, `from pitchdeck.models import PitchDeck`

**Barrel Files:**
- `__init__.py` files use barrel imports to expose public API
- Example from `src/pitchdeck/profiles/__init__.py`:
  ```python
  from pitchdeck.profiles.loader import load_vc_profile, list_profiles
  ```

## Pydantic Model Conventions

**Fields:**
- Use `List[X]` from typing for list fields: `List[str]`, `List[SlideContent]`
- Use `Field(default_factory=list)` for mutable defaults, not `default=[]`
- Use `Optional[X]` for nullable fields, with explicit `= None` default
- Score fields use validators: `score: int = Field(ge=0, le=100)` (0-100 range)
- Weight fields use float validators: `weight: float = Field(ge=0.0, le=1.0)`

**Computed Fields:**
- Use `@computed_field` decorator for derived properties
- Example from `models.py`:
  ```python
  @computed_field
  @property
  def overall_score(self) -> int:
      if not self.dimension_scores:
          return 0
      raw = sum(d.score * d.weight for d in self.dimension_scores)
      return max(0, min(100, int(round(raw))))
  ```

**Cross-Field Validation:**
- Use `@model_validator(mode="after")` for invariants that involve multiple fields
- Example from `models.py`:
  ```python
  @model_validator(mode="after")
  def _check_weight_sum(self) -> "DeckValidationResult":
      weight_sum = sum(d.weight for d in self.dimension_scores)
      if self.dimension_scores and abs(weight_sum - 1.0) > 0.01:
          raise ValueError(f"Dimension weights must sum to ~1.0, got {weight_sum:.3f}")
      return self
  ```

## JSON Extraction Pattern

**From Claude API Responses:**
- Use regex `r"\{[\s\S]*\}"` to extract JSON (handles markdown wrapping, multiple line breaks)
- Always catch `json.JSONDecodeError` with full context
- Example from `narrative.py`:
  ```python
  json_match = re.search(r"\{[\s\S]*\}", raw_text)
  if not json_match:
      raise PitchDeckError("Failed to parse deck response — no JSON found in Claude output")
  try:
      data = json.loads(json_match.group())
  except json.JSONDecodeError as e:
      extracted = json_match.group()
      snippet = extracted[:200] + ("..." if len(extracted) > 200 else "")
      raise PitchDeckError(
          f"Failed to parse deck JSON: {e}. Extracted text starts with: {snippet}"
      ) from e
  ```

## Temperature Settings

**LLM Calls:**
- Use `temperature=0.0` for deterministic tasks: validation scoring, rule extraction
- Use default temperature (0.7) or specified temperature for creative tasks: deck generation
- Explicitly set in API calls: `model="claude-sonnet-4-6", ... temperature=0.0 ...`

## Prompt Caching

**Pattern:**
- Use ephemeral prompt caching for large context that repeats across calls
- Apply `"cache_control": {"type": "ephemeral"}` to system messages with large static context
- Example from `narrative.py`:
  ```python
  system_messages = [
      {"type": "text", "text": SYSTEM_PROMPT},
      {
          "type": "text",
          "text": (
              f"<company_document>\n{company.raw_document_text}\n</company_document>\n\n"
              f"<company_profile>\n{company.model_dump_json(indent=2)}\n</company_profile>\n\n"
              f"<vc_profile>\n{vc_context}\n</vc_profile>"
          ),
          "cache_control": {"type": "ephemeral"},
      },
  ]
  ```

---

*Convention analysis: 2026-02-26*
