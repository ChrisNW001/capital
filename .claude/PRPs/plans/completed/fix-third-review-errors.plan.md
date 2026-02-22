# Feature: Fix All Errors from Third PR Review

## Summary

Fix all 4 critical issues, 8 important issues, and 7 suggestions identified in the third round of PR #2 review. Changes span the validator scoring engine, CLI error handling, Pydantic model design, and test coverage. No new dependencies — all fixes use existing patterns.

## User Story

As a developer reviewing PR #2
I want all review-identified issues fixed
So that the validation engine is correct, robust, and follows project conventions

## Problem Statement

PR #2 (validation engine) has passed two fix rounds but the third review still found: a scoring formula bug that conflates three independent axes, missing error handlers on file I/O, private cross-module imports, convention violations, and test gaps.

## Solution Statement

Apply targeted fixes across 4 files (validator.py, cli.py, models.py, narrative.py) and extend test coverage in 2 test files (test_validator.py, test_cli_validate.py). Every fix mirrors an existing codebase pattern.

## Metadata

| Field            | Value                                                |
| ---------------- | ---------------------------------------------------- |
| Type             | BUG_FIX                                              |
| Complexity       | MEDIUM                                               |
| Systems Affected | validator, cli, models, narrative, tests             |
| Dependencies     | None (existing deps only)                            |
| Estimated Tasks  | 12                                                   |

---

## Mandatory Reading

**CRITICAL: Implementation agent MUST read these files before starting any task:**

| Priority | File | Lines | Why Read This |
|----------|------|-------|---------------|
| P0 | `src/pitchdeck/engine/validator.py` | all | Primary fix target — scoring, parsing, mutation |
| P0 | `src/pitchdeck/cli.py` | all | Error handling fixes in generate/validate |
| P0 | `src/pitchdeck/models.py` | 130-170 | Model field fixes |
| P1 | `src/pitchdeck/engine/narrative.py` | 111-144 | `_build_vc_context` to make public |
| P1 | `tests/test_validator.py` | all | Existing test patterns to mirror |
| P1 | `tests/test_cli_validate.py` | all | CLI test patterns to extend |
| P2 | `tests/conftest.py` | all | Fixture patterns |

---

## Patterns to Mirror

**ERROR_HANDLING (CLI):**
```python
# SOURCE: src/pitchdeck/cli.py:139-151
# COPY THIS PATTERN for save_markdown error handling:
try:
    with open(json_path, "w") as f:
        f.write(deck.model_dump_json(indent=2))
    console.print(f"  JSON: {json_path}")
except OSError as e:
    console.print(
        f"\n[bold red]Error: Failed to save JSON to {json_path}: {e}[/bold red]"
    )
    console.print(
        "[red]The deck was saved as Markdown but cannot be validated. "
        "Check file permissions and disk space.[/red]"
    )
    raise typer.Exit(1)
```

**COMPUTED_FIELD:**
```python
# SOURCE: src/pitchdeck/models.py:167-170
# COPY THIS PATTERN for overall_score:
@computed_field
@property
def pass_fail(self) -> bool:
    return self.overall_score >= self.pass_threshold
```

**MODEL_COPY (immutable update):**
```python
# SOURCE: src/pitchdeck/engine/validator.py:655-659
# COPY THIS PATTERN instead of .append() mutation:
completeness = completeness.model_copy(
    update={"weight": completeness.weight / rule_weight_sum}
)
```

**FIELD_DEFAULT_FACTORY:**
```python
# SOURCE: src/pitchdeck/models.py:135-136
# COPY THIS PATTERN for list fields:
evidence_found: List[str] = Field(default_factory=list)
```

**TEST_CLASS_STRUCTURE:**
```python
# SOURCE: tests/test_cli_validate.py:13-19
# COPY THIS PATTERN:
class TestValidateCLIFileHandling:
    def test_file_not_found_exits_1(self):
        result = runner.invoke(
            app, ["validate", "nonexistent.json", "--skip-llm"]
        )
        assert result.exit_code == 1
        assert "File not found" in result.output
```

---

## Files to Change

| File | Action | Justification |
|------|--------|---------------|
| `src/pitchdeck/engine/validator.py` | UPDATE | Fix scoring formula, regex, mutation, import, catch-all, docstring |
| `src/pitchdeck/cli.py` | UPDATE | Add save_markdown error handler, exit non-zero on report save fail |
| `src/pitchdeck/models.py` | UPDATE | Add default_factory to list fields, Literal dimension type |
| `src/pitchdeck/engine/narrative.py` | UPDATE | Rename _build_vc_context → build_vc_context (make public) |
| `tests/test_validator.py` | UPDATE | Fix weak assertions, add missing test paths |
| `tests/test_cli_validate.py` | UPDATE | Add save error tests, generate command tests |

---

## NOT Building (Scope Limits)

- `overall_score` as `@computed_field` — would require `dimension_scores` to be stored before `overall_score` is computed; currently `validate_deck` constructs all at once. The tight coupling with the weight-rescaling logic makes this a refactor, not a bug fix. Keeping as a passed-in field with `ge=0, le=100` enforcement.
- `DimensionScore.dimension` as `Literal` type — while a good suggestion, this is a type-tightening improvement not a bug fix. The five dimension names are validated implicitly by the code structure (each scoring function sets its own string). Out of scope for this fix round.

---

## Step-by-Step Tasks

### Task 1: FIX `_score_completeness` formula — separate the three axes

**CRITICAL BUG**: The denominator conflates slide count, type coverage, and speaker notes into one sum, making individual axis scores meaningless when axes have very different magnitudes.

- **FILE**: `src/pitchdeck/engine/validator.py:145-210`
- **ACTION**: Rewrite the score formula to score each axis independently (0-100) and average them
- **IMPLEMENT**:
  ```python
  # Score each axis independently on 0-100 scale, then average
  # Axis 1: Slide count
  expected = vc_profile.deck_preferences.preferred_slide_count
  actual = len(deck.slides)
  slide_count_score = min(100, int((actual / max(expected, 1)) * 100))

  # Axis 2: Required slide types coverage
  if must_include:
      type_score = int((len(present) / len(must_include)) * 100)
  else:
      type_score = 100  # no requirements = full marks

  # Axis 3: Speaker notes coverage
  notes_score = int((notes_count / max(len(deck.slides), 1)) * 100)

  # Average the three axes
  score = (slide_count_score + type_score + notes_score) // 3
  ```
- **ALSO FIXES**: Important issue — `preferred_slide_count` now consulted instead of hardcoded `or 15`
- **MIRROR**: Keep same `DimensionScore` return shape, same evidence lists, same `max(0, min(100, score))` clamping
- **VALIDATE**: `pytest tests/test_validator.py -q`

### Task 2: MAKE `_build_vc_context` public

**CRITICAL**: Importing a private function across modules breaks encapsulation.

- **FILE**: `src/pitchdeck/engine/narrative.py:111`
- **ACTION**: Rename `_build_vc_context` → `build_vc_context` (remove leading underscore)
- **ALSO UPDATE**:
  - `src/pitchdeck/engine/narrative.py:53` — call site in `generate_deck()`
  - `src/pitchdeck/engine/validator.py:17` — import statement
  - `src/pitchdeck/engine/validator.py:370` — call site in `_score_qualitative()`
  - `tests/test_engine.py` — any import of `_build_vc_context`
- **VALIDATE**: `pytest -q`

### Task 3: ADD error handler for `save_markdown` in `generate` command

**CRITICAL**: `save_markdown` at cli.py:130 has no try/except — disk errors crash with raw traceback after API credits consumed.

- **FILE**: `src/pitchdeck/cli.py:129-131`
- **ACTION**: Wrap `save_markdown(deck, output)` in try/except OSError
- **IMPLEMENT**:
  ```python
  try:
      save_markdown(deck, output)
      console.print(f"\n[bold green]Deck saved to {output}[/bold green]")
  except OSError as e:
      console.print(
          f"\n[bold red]Error: Failed to save deck to {output}: {e}[/bold red]"
      )
      console.print("[red]Check file permissions and disk space.[/red]")
      raise typer.Exit(1)
  ```
- **MIRROR**: `cli.py:139-151` — JSON save error pattern (same structure, same exit code)
- **VALIDATE**: `pytest tests/test_cli_validate.py -q`

### Task 4: EXIT non-zero on report save failure in `validate` command

**CRITICAL**: Report save catches `OSError` but exits with code 0 — automated pipelines see success when report wasn't written.

- **FILE**: `src/pitchdeck/cli.py:291-325`
- **ACTION**: After printing the summary, exit with code 1 if `report_saved` is False
- **IMPLEMENT**: Add after line 325:
  ```python
  if not report_saved:
      raise typer.Exit(1)
  ```
- **RATIONALE**: Print the summary first so the user gets the scores even if save failed, then signal failure to the process
- **VALIDATE**: `pytest tests/test_cli_validate.py -q`

### Task 5: FIX `_score_qualitative` catch-all to not misattribute non-API errors

**IMPORTANT**: The `except Exception` at validator.py:463-464 wraps _all_ errors as "Unexpected error calling Claude API" — but errors could be from prompt construction, not the API call.

- **FILE**: `src/pitchdeck/engine/validator.py:438-464`
- **ACTION**: Narrow the try/except to cover only the `client.messages.create()` call, not the prompt construction code above it
- **IMPLEMENT**: Move the `try:` statement to just before `response = client.messages.create(...)` (line 438→line immediately before 439). The prompt construction code above (system_messages, user_prompt) should be outside the try block.
- **VALIDATE**: `pytest tests/test_validator.py -q`

### Task 6: ADD raw text to `_parse_validation_response` error messages

**IMPORTANT**: When JSON parsing fails, no raw Claude text is included — no debugging breadcrumb.

- **FILE**: `src/pitchdeck/engine/validator.py:484-496`
- **ACTION**: Include a truncated snippet of `raw_text` in error messages
- **IMPLEMENT**:
  ```python
  json_match = re.search(r"\{[\s\S]*\}", raw_text)
  if not json_match:
      snippet = raw_text[:200] + ("..." if len(raw_text) > 200 else "")
      raise PitchDeckError(
          "Failed to parse validation response — "
          f"no JSON found in Claude output. Response starts with: {snippet}"
      )

  try:
      return json.loads(json_match.group())
  except json.JSONDecodeError as e:
      snippet = json_match.group()[:200] + ("..." if len(json_match.group()) > 200 else "")
      raise PitchDeckError(
          f"Failed to parse validation JSON: {e}. Extracted text starts with: {snippet}"
      ) from e
  ```
- **VALIDATE**: `pytest tests/test_validator.py -q`

### Task 7: ELIMINATE post-construction mutation of `SlideValidationScore.suggestions`

**IMPORTANT**: `ss.suggestions.append(note)` at validator.py:646 mutates a Pydantic model after construction, bypassing validation.

- **FILE**: `src/pitchdeck/engine/validator.py:639-646`
- **ACTION**: Use `model_copy` to produce new instances instead of mutating in-place
- **IMPLEMENT**:
  ```python
  # Merge LLM per-slide quality notes into existing slide scores
  for sq in llm_data.get("slide_quality", []):
      num = sq.get("slide_number")
      note = sq.get("quality_note", "")
      if num and note:
          for i, ss in enumerate(slide_scores):
              if ss.slide_number == num:
                  slide_scores[i] = ss.model_copy(
                      update={"suggestions": ss.suggestions + [note]}
                  )
  ```
- **MIRROR**: `validator.py:655-659` — same `model_copy(update={...})` pattern
- **ALSO FIXES**: Removes the redundant `and note` check at line 645
- **VALIDATE**: `pytest tests/test_validator.py -q`

### Task 8: ADD `Field(default_factory=list)` to `DeckValidationResult` list fields

**IMPORTANT**: `top_strengths`, `critical_gaps`, `improvement_priorities` are required list fields with no defaults, violating CLAUDE.md convention.

- **FILE**: `src/pitchdeck/models.py:162-164`
- **ACTION**: Add `Field(default_factory=list)` to all three fields
- **IMPLEMENT**:
  ```python
  top_strengths: List[str] = Field(default_factory=list)
  critical_gaps: List[str] = Field(default_factory=list)
  improvement_priorities: List[str] = Field(default_factory=list)  # ordered by impact
  ```
- **MIRROR**: `models.py:135-136` — same pattern used elsewhere in the model
- **VALIDATE**: `pytest tests/test_validator.py tests/test_models.py -q`

### Task 9: FIX `_score_completeness` docstring accuracy

**IMPORTANT**: Docstring claims "required elements, data coverage" but function checks slide types, speaker notes, and gaps.

- **FILE**: `src/pitchdeck/engine/validator.py:146`
- **ACTION**: Update docstring to match actual behavior
- **IMPLEMENT**:
  ```python
  """Score deck completeness: slide count vs preferred, required slide type coverage, and speaker notes presence."""
  ```
- **VALIDATE**: N/A (docstring only)

### Task 10: ADD "Weak match" prefix to fallback evidence in `_check_custom_checks`

**SUGGESTION**: Curated keyword match and word-overlap fallback are indistinguishable in output.

- **FILE**: `src/pitchdeck/engine/validator.py:324-325`
- **ACTION**: Change evidence prefix from `"Content overlap"` to `"Weak match (word overlap)"`
- **IMPLEMENT**:
  ```python
  evidence = f"Weak match (word overlap): {', '.join(sorted(overlap)[:5])}"
  ```
- **VALIDATE**: `pytest tests/test_validator.py::TestCheckCustomChecks -q`

### Task 11: FIX `test_passes_when_keywords_present` weak assertion

**SUGGESTION**: Test at test_validator.py:244 asserts `isinstance(results, list)` without checking `results[0].passed is True`.

- **FILE**: `tests/test_validator.py:243-246`
- **ACTION**: Add assertion that the custom check actually passed
- **IMPLEMENT**:
  ```python
  results = _check_custom_checks(deck, sample_vc_profile)
  assert isinstance(results, list)
  assert len(results) == 1
  assert results[0].passed is True
  assert "Keywords found" in results[0].evidence
  ```
- **VALIDATE**: `pytest tests/test_validator.py::TestCheckCustomChecks -q`

### Task 12: ADD test coverage for critical untested paths

**SUGGESTION**: Multiple review-identified test gaps need coverage.

- **FILE**: `tests/test_validator.py` and `tests/test_cli_validate.py`
- **ACTION**: Add tests for:

**In `tests/test_validator.py`:**

1. **`_check_custom_checks` fallback word-overlap path** — test with a check string that matches no keyword_map pattern but has word overlap with content. Assert evidence starts with `"Weak match"`.
2. **`_build_improvement_priorities` ordering** — assert failed custom checks come before critical gaps, which come before slide issues.
3. **`_score_metrics_density` no-emphasis branch** — test with VC profile that has empty `metrics_emphasis`, verify score is based on template coverage only.

**In `tests/test_cli_validate.py`:**

4. **Report save failure exits non-zero** — mock `save_validation_report` to raise `OSError`, assert `exit_code == 1` and "Report not saved" not in output (since we exit before that).
5. **`save_markdown` failure in generate exits non-zero** — mock `save_markdown` to raise `OSError`, assert `exit_code == 1`.

- **MIRROR**: Existing class-based test patterns in both files
- **VALIDATE**: `pytest tests/test_validator.py tests/test_cli_validate.py -q`

---

## Testing Strategy

### Tests to Write

| Test File | Test Cases | Validates |
|-----------|-----------|-----------|
| `tests/test_validator.py` | fallback word-overlap, improvement priorities ordering, no-emphasis metrics density | Scoring logic, custom checks, prioritization |
| `tests/test_cli_validate.py` | report save failure, markdown save failure | CLI error handling |

### Edge Cases Checklist

- [ ] Empty `must_include_slides` with `preferred_slide_count=15` → slide count axis uses 15
- [ ] All speaker notes empty → notes axis scores 0
- [ ] Custom check matches no keyword_map pattern and has <2 word overlap → fails with empty evidence
- [ ] `save_markdown` raises `PermissionError` (subclass of `OSError`) → caught correctly
- [ ] LLM returns `slide_quality` with string `slide_number` instead of int → handled gracefully

---

## Validation Commands

### Level 1: STATIC_ANALYSIS

```bash
python3 -m py_compile src/pitchdeck/engine/validator.py && python3 -m py_compile src/pitchdeck/cli.py && python3 -m py_compile src/pitchdeck/models.py && python3 -m py_compile src/pitchdeck/engine/narrative.py
```

**EXPECT**: Exit 0, no errors

### Level 2: UNIT_TESTS

```bash
pytest tests/test_validator.py tests/test_cli_validate.py tests/test_models.py tests/test_engine.py -q
```

**EXPECT**: All tests pass, 0 failures

### Level 3: FULL_SUITE

```bash
pytest -q
```

**EXPECT**: All tests pass (131+ tests), 0 failures, 0 errors

---

## Acceptance Criteria

- [ ] `_score_completeness` scores three axes independently and uses `preferred_slide_count`
- [ ] `_build_vc_context` → `build_vc_context` (public) — no private cross-module imports
- [ ] `save_markdown` failure in `generate` exits with code 1
- [ ] Report save failure in `validate` exits with code 1 (after printing summary)
- [ ] `_score_qualitative` catch-all only covers the API call, not prompt construction
- [ ] `_parse_validation_response` error messages include raw text snippet
- [ ] `SlideValidationScore.suggestions` updated via `model_copy`, not `.append()`
- [ ] `DeckValidationResult` list fields have `Field(default_factory=list)`
- [ ] `_check_custom_checks` fallback evidence prefixed with "Weak match"
- [ ] All existing 131 tests still pass
- [ ] New tests cover: fallback word-overlap, priorities ordering, no-emphasis metrics, CLI save errors
- [ ] No regressions

---

## Completion Checklist

- [ ] All 12 tasks completed in order
- [ ] Each task validated immediately after completion
- [ ] Level 1: py_compile passes for all changed files
- [ ] Level 2: Targeted test files pass
- [ ] Level 3: Full `pytest` suite passes
- [ ] All acceptance criteria met

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `_score_completeness` formula change shifts scores for existing tests | HIGH | MED | Update test assertions to match new formula behavior |
| Renaming `_build_vc_context` breaks test imports | MED | LOW | Grep for all references before renaming; update all in one task |
| `model_copy` on `SlideValidationScore` changes list identity | LOW | LOW | `model_copy` creates new list — existing code already expects this |

---

## Notes

- The third review also suggested converting `overall_score` to `@computed_field` and using `Literal` for `dimension`. These are design improvements explicitly deferred (see "NOT Building" section) — they can be addressed in a future refactor.
- The `\{[\s\S]*\}` greedy regex was flagged as potentially capturing wrong spans with trailing braces. This is the same pattern used in `narrative.py:172` and documented in CLAUDE.md. Changing it could break the narrative parser. The risk is low since Claude responses typically have one JSON object. Deferred.
- Tasks 1-4 fix all 4 critical issues. Tasks 5-8 fix the most impactful important issues. Tasks 9-12 address suggestions and test gaps.
