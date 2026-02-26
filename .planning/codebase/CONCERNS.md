# Codebase Concerns

**Analysis Date:** 2026-02-26

## Tech Debt

**Hardcoded Custom Check Keywords:**
- Issue: `_check_custom_checks()` in `src/pitchdeck/engine/validator.py` (lines 297-305) uses a hardcoded `keyword_map` dictionary for pattern matching against VC custom checks. Adding new check patterns requires code changes and test updates.
- Files: `src/pitchdeck/engine/validator.py`
- Impact: New VC profiles with custom checks that don't match the hardcoded patterns fall back to weak heuristic (word overlap). This produces false positives and false negatives. VC-specific validation can be unreliable.
- Fix approach: Extract `keyword_map` to a data-driven configuration file or loader. Allow dynamic pattern registration. Add integration tests for new check types before hardcoding patterns.

**Large Module: validator.py:**
- Issue: `src/pitchdeck/engine/validator.py` is 748 lines — multiple concerns mixed: per-slide rule scoring, dimension scoring, custom check evaluation, LLM integration, and response parsing.
- Files: `src/pitchdeck/engine/validator.py`
- Impact: Difficult to test in isolation. Changes to one scoring dimension risk breaking others. Dimension weight rescaling logic (lines 688-696) is fragile.
- Fix approach: Split into smaller modules: `slide_scoring.py`, `dimension_scoring.py`, `custom_checks.py`, `llm_scoring.py`. Each with focused responsibility.

**JSON Extraction Regex Fragility:**
- Issue: Both `narrative.py` (line 211) and `validator.py` (line 506) extract JSON from Claude responses using regex `\{[\s\S]*\}`. If Claude emits preface text outside braces or nested objects, extraction may grab wrong boundaries.
- Files: `src/pitchdeck/engine/narrative.py`, `src/pitchdeck/engine/validator.py`
- Impact: JSON parsing errors on edge cases. Users see "Failed to parse deck response" with no hint of what Claude sent. Difficult to debug API response issues.
- Fix approach: Use `json.JSONDecodeError` to identify where parsing failed. Try multiple extraction strategies: look for top-level `{`, validate after each `}`, or request JSON with markers. Add response logging for debugging.

## Known Bugs

**Dimension Weight Rescaling When Skipping LLM:**
- Symptoms: When `--skip-llm` flag is used, `validate_deck()` (lines 688-696) rescales `completeness` and `metrics_density` weights to sum to 1.0, zeroing out LLM dimension weights. If a future PR adds another rule-based dimension without updating the rescale logic, weights won't sum to 1.0 and will trigger the validator on line 726-729.
- Files: `src/pitchdeck/engine/validator.py`
- Trigger: Run validation with `--skip-llm`, then add a new rule-based dimension to `SCORING_DIMENSIONS` without updating rescale logic.
- Workaround: Verify weight sums with `--skip-llm` in CI.
- Fix: Calculate rule-based weights dynamically instead of hardcoding `0.45` sum.

**Model Name Hardcoded to claude-sonnet-4-6:**
- Symptoms: Both `narrative.py` (line 109) and `validator.py` (line 460) hardcode `model="claude-sonnet-4-6"`. If Anthropic deprecates this model or pricing changes, all deck generation and validation breaks.
- Files: `src/pitchdeck/engine/narrative.py` (line 109), `src/pitchdeck/engine/validator.py` (line 460)
- Trigger: Anthropic deprecates model or renames it.
- Workaround: Would require code change and redeploy.
- Fix: Make model name configurable via environment variable with sensible default.

## Security Considerations

**API Key Exposure in Error Messages:**
- Risk: If Anthropic API call fails with `APIStatusError`, the exception message may include request/response details. If logs are shared, API behavior could be exposed (not the key itself, but usage patterns).
- Files: `src/pitchdeck/engine/narrative.py` (lines 114-134), `src/pitchdeck/engine/validator.py` (lines 466-486)
- Current mitigation: Generic error messages are provided to users via `PitchDeckError`. Raw API errors are caught and abstracted.
- Recommendations: Ensure logs are not world-readable. Add redaction of sensitive context (company names, thesis points) from exception messages. Test error paths with sensitive data.

**Input Document Size Not Bounded:**
- Risk: Large PDF/DOCX files could exhaust memory during parsing or cause API timeouts. No file size check before parsing.
- Files: `src/pitchdeck/cli.py` (lines 65-71 in `generate` command), `src/pitchdeck/parsers/pdf.py`, `src/pitchdeck/parsers/docx_parser.py`
- Current mitigation: API timeouts are caught with helpful message (lines 122-126 in `narrative.py`).
- Recommendations: Add file size limit checks before parsing (e.g., max 50MB per file). Warn user if combined text exceeds 100KB. Consider streaming/chunking for large documents.

## Performance Bottlenecks

**Inefficient Custom Check Word Overlap:**
- Problem: `_check_custom_checks()` (lines 326-339) performs word splitting on entire deck content, then checks overlap for EVERY custom check. For decks with many slides and many custom checks, this becomes O(slides * checks).
- Files: `src/pitchdeck/engine/validator.py`
- Cause: No caching of content words. Regex and string operations repeated for each check.
- Improvement path: Pre-compute content word set once (line 330). Lookup is then O(checks) with set intersection. Cache deck text analysis.

**LLM Scoring Makes Two Separate API Calls:**
- Problem: Validation flow calls `_score_qualitative()` (line 620) which makes ONE API call, but for narrative + thesis + mistakes scoring. With caching, this is efficient, but the system makes: (1) deck generation call, (2) validation scoring call. No batching.
- Files: `src/pitchdeck/engine/validator.py` (line 620), `src/pitchdeck/engine/narrative.py` (line 108)
- Cause: Separation of concerns — generator and validator are independent.
- Improvement path: If both are called in same process (e.g., batch mode), combine into single prompt to reuse cache. Non-trivial refactor; current setup is acceptable for single-use CLI.

**Metrics Emphasis Keyword Matching O(deck_content * emphasis_metrics):**
- Problem: `_score_metrics_density()` (lines 233-238) tokenizes entire deck once, but then checks `any(kw in all_content for kw in keywords)` for each emphasis metric. Large decks × many metrics = repeated string searches.
- Files: `src/pitchdeck/engine/validator.py`
- Cause: Inefficient keyword lookup; string `in` operator scans all text.
- Improvement path: Pre-compile regex or build keyword set once. Use set intersection instead of substring checks.

## Fragile Areas

**Dimension Weight Calibration:**
- Files: `src/pitchdeck/engine/validator.py` (lines 33-39)
- Why fragile: `SCORING_DIMENSIONS` list defines weights that must sum to 1.0. If someone adds or removes a dimension without updating weights, tests should catch it (line 725-729), but it's easy to miss during refactoring. Weight semantics are implicit.
- Safe modification: Always verify weight sum in tests. Document why each weight is chosen. Use `Decimal` for weight arithmetic to avoid floating-point rounding errors (current `abs(weight_sum - 1.0) > 0.01` tolerance is loose).
- Test coverage: `test_validator.py` should have `test_dimension_weights_sum_to_one`. Check if it exists.

**Custom Check Keyword Map Hard to Maintain:**
- Files: `src/pitchdeck/engine/validator.py` (lines 297-305)
- Why fragile: Keyword list is domain knowledge (what keywords signal "european sovereignty"?). As VC language evolves or new profiles are added, map becomes incomplete. No mechanism to alert maintainers.
- Safe modification: Add `pytest` fixture that loads all profile custom_checks and validates that each matches at least one pattern or has clear fallback documented. Periodically audit VC profiles against keyword_map.
- Test coverage: No test currently validates that realistic custom checks produce expected results.

**JSON Response Parsing Assumes Structure:**
- Files: `src/pitchdeck/engine/narrative.py` (lines 227-232), `src/pitchdeck/engine/validator.py` (lines 491-522)
- Why fragile: Assume Claude returns "slides" key with list of slide dicts. If Claude changes response structure (e.g., wraps in extra object), parsing silently fails or throws unhelpful error.
- Safe modification: Add detailed logging of Claude's raw response before parsing. Add schema validation (Pydantic or JSONSchema). Use Claude's structured output mode if available.
- Test coverage: Mocking in `test_engine.py` uses synthetic responses that match expectations perfectly. Need tests for malformed responses.

**VC Profile YAML Validation:**
- Files: `src/pitchdeck/profiles/loader.py` (lines 27-30)
- Why fragile: `VCProfile(**raw)` from YAML will raise `ValidationError` if YAML is missing required fields. Error is not caught; users see cryptic Pydantic message.
- Safe modification: Wrap in try/except, catch `ValidationError`, and provide better message with guidance on required fields.
- Test coverage: `test_profiles.py` likely doesn't test malformed profiles.

## Scaling Limits

**Max Tokens Fixed at 16384 (narrative) and 8192 (validator):**
- Current capacity: Decks with ~15 slides and full VC context fit comfortably.
- Limit: If deck grows to 30+ slides or input documents are extremely large, `max_tokens` may be insufficient. Claude will truncate output or error.
- Scaling path: Make `max_tokens` configurable per environment or profile. Monitor token usage via `response.usage`. Implement streaming if responses grow beyond 8KB.

**No Rate Limiting or Retry Logic:**
- Current capacity: Single sequential deck generation/validation works. No exponential backoff or retry.
- Limit: If running batch operations (e.g., 100 decks), hitting rate limits will crash after first limited request.
- Scaling path: Add `tenacity` or `backoff` library with exponential backoff. Respect Anthropic's `Retry-After` header. Queue batch jobs.

**Deck Validation O(slides * LLM calls):**
- Current capacity: Single deck with 15 slides validates in ~10-30 seconds (one LLM call).
- Limit: Validating 1000 decks would require 1000 API calls, each taking 10+ seconds. Not feasible.
- Scaling path: Batch validation by combining multiple decks into single LLM prompt (if validation logic allows). Or offload to async job queue.

## Dependencies at Risk

**pymupdf4llm (0.0.17):**
- Risk: Early version number (0.0.17) suggests API may not be stable. If upstream pymupdf changes, this wrapper may break.
- Impact: PDF parsing fails for all users.
- Migration plan: Monitor releases. Have fallback extraction using raw pymupdf or pdfplumber. Add integration tests for PDF extraction.

**questionary (2.0+):**
- Risk: Interactive prompt library. If terminal environment doesn't support, interactive mode fails (e.g., CI/CD, headless).
- Impact: `fill_gaps_interactive()` crashes in non-interactive environments.
- Migration plan: Already handled via `--skip-gaps` flag in CLI. Ensure flag is documented and tests verify non-interactive mode works.

**Anthropic SDK Version Pinning:**
- Risk: `anthropic>=0.82.0` allows drift. If new major version changes exception types or API contracts, code may break unexpectedly.
- Impact: Unknown — depends on Anthropic's versioning discipline.
- Migration plan: Consider tighter pin (e.g., `>=0.82.0,<1.0.0`). Test against latest version in CI.

## Missing Critical Features

**No Batch Deck Generation:**
- Problem: CLI only generates one deck at a time. No way to specify "generate decks for 10 companies targeting 3 different VCs".
- Blocks: Large-scale pitch deck production.
- Priority: Medium. Workaround is shell loop.

**No Deck Editing Interface:**
- Problem: Generated deck is immutable JSON. To edit, user must manually modify JSON or regenerate. No incremental update API.
- Blocks: Iterative refinement workflow.
- Priority: Low. Most users prefer full regeneration for consistency.

**No Persistent Deck History:**
- Problem: Each generation overwrites previous output. No versioning or audit trail.
- Blocks: Tracking what changed between versions.
- Priority: Low. User can use git to track JSON versions.

**No Export to PowerPoint/Keynote:**
- Problem: Output is Markdown only. No way to get a presentation file.
- Blocks: Immediate use in pitch meetings.
- Priority: High. Markdown is not investor-ready without manual conversion.
- Fix: Add Markdown-to-PPTX renderer using `python-pptx` or similar.

## Test Coverage Gaps

**CLI Integration Tests:**
- What's not tested: The `generate` command end-to-end with mocked Claude. Current tests mock at module level, not CLI level.
- Files: `src/pitchdeck/cli.py`, tests in `tests/test_cli_validate.py` (only `validate` command is tested)
- Risk: CLI argument parsing, file I/O flow, error handling in shell could fail unnoticed.
- Priority: High. Add `test_cli_generate.py` with end-to-end flow tests.

**PDF/DOCX Parser Edge Cases:**
- What's not tested: Large files (>10MB), corrupted headers, unsupported formats, empty documents, documents with binary data.
- Files: `src/pitchdeck/parsers/pdf.py`, `src/pitchdeck/parsers/docx_parser.py`
- Risk: Parser crashes on real-world documents.
- Priority: Medium. Add parametrized tests with realistic edge cases.

**Custom Check Validation:**
- What's not tested: Do custom checks from real VC profiles pass/fail as expected? Only synthetic test data is used.
- Files: `src/pitchdeck/engine/validator.py` (lines 276-348)
- Risk: Custom check logic is untested against real profiles. VC-specific validation is unreliable.
- Priority: High. Load actual profile custom_checks and validate behavior.

**LLM Response Malformation:**
- What's not tested: Claude response missing "slides" key, "slides" is not a list, slide fields are wrong type, invalid JSON.
- Files: `src/pitchdeck/engine/narrative.py` (lines 191-258), `src/pitchdeck/engine/validator.py` (lines 491-522)
- Risk: Unhelpful error messages if Claude output is malformed.
- Priority: Medium. Mock Claude to return malformed responses and verify graceful errors.

**Weight Sum Validation:**
- What's not tested: Adding new dimension breaks weight sum validation. Test should fail if dimensions don't sum to 1.0.
- Files: `src/pitchdeck/engine/validator.py` (lines 725-729)
- Risk: Dimension changes silently break scoring.
- Priority: High. Add explicit test: `test_dimension_weights_sum_to_one`.

**Gap Filling Type Coercion:**
- What's not tested: User input that's truly invalid (non-numeric string to float field, malformed dates, etc.). Coercion fallback to string is not tested.
- Files: `src/pitchdeck/engine/gaps.py` (lines 105-126)
- Risk: Type coercion silently accepts bad data, leading to downstream validation errors.
- Priority: Low. Add tests for invalid coercion paths.

---

*Concerns audit: 2026-02-26*
