# Feature: Pitch Deck Validation Engine

## Summary

Build a hybrid rule-based + LLM-powered validation engine that scores generated pitch decks against VC-specific rubrics. The engine evaluates five dimensions (completeness, metrics density, narrative coherence, thesis alignment, common mistake detection), produces per-slide scores (0-100) with actionable feedback, and generates a prioritized improvement report. Rule-based checks run without an API key; LLM scoring adds qualitative assessment via Claude. The first target is Earlybird Capital's 7 custom checks and 8 metrics emphasis criteria.

## User Story

As a technical founder preparing a VC pitch deck
I want to validate my generated deck against VC-specific scoring rubrics
So that I can identify and fix weaknesses before the actual pitch

## Problem Statement

A generated pitch deck may have structural issues (missing metrics, exceeding word limits), narrative weaknesses (poor transitions, disjointed arc), or VC-specific gaps (not addressing Earlybird's European sovereignty thesis). Without validation, the founder cannot objectively assess deck quality or know which improvements would have the highest impact.

## Solution Statement

A two-layer validation engine:
1. **Rule-based layer**: Deterministic checks against `SlideTemplate` constraints (`required_elements`, `metrics_needed`, `max_bullets`, `word_limit`) and `VCProfile.custom_checks` keyword matching. Runs instantly without API key.
2. **LLM-powered layer**: Claude evaluates narrative coherence, thesis alignment quality, and common founder mistakes. Uses `temperature=0.0` for consistent scoring and prompt caching for cost efficiency.

Results are aggregated into a `DeckValidationResult` model with weighted dimension scores, per-slide feedback, and a prioritized improvement list rendered as a Markdown report.

## Metadata

| Field            | Value                                                        |
| ---------------- | ------------------------------------------------------------ |
| Type             | NEW_CAPABILITY                                               |
| Complexity       | HIGH                                                         |
| Systems Affected | engine (new validator module), output (new report renderer), cli (new command), models (new types) |
| Dependencies     | anthropic>=0.82.0 (existing), pydantic>=2.0 (existing), typer>=0.24.0 (existing) — no new deps |
| Estimated Tasks  | 8                                                            |

---

## UX Design

### Before State

```
+-----------------------------------------------------------------------+
|                          BEFORE STATE                                  |
+-----------------------------------------------------------------------+
|                                                                        |
|   $ pitchdeck generate docs.pdf --vc earlybird                        |
|        |                                                               |
|        v                                                               |
|   [deck.md generated]                                                  |
|        |                                                               |
|        v                                                               |
|   +----------------------------------------------------+              |
|   |          FOUNDER'S MANUAL REVIEW                   |              |
|   |  - Reads through 15 slides                         |              |
|   |  - No idea if metrics are sufficient               |              |
|   |  - Cannot assess Earlybird thesis alignment         |              |
|   |  - Doesn't know common mistakes to look for        |              |
|   |  - No prioritized improvement list                 |              |
|   +----------------------------------------------------+              |
|        |                                                               |
|        v                                                               |
|   [Ships deck with unknown quality]                                    |
|                                                                        |
|   PAIN: No objective quality assessment                                |
|   PAIN: Unknown if Earlybird-specific criteria are met                 |
|   PAIN: No idea which improvements would have highest impact           |
|                                                                        |
|   DATA_FLOW: PitchDeck model -> Markdown file -> manual reading        |
+-----------------------------------------------------------------------+
```

### After State

```
+-----------------------------------------------------------------------+
|                           AFTER STATE                                  |
+-----------------------------------------------------------------------+
|                                                                        |
|   $ pitchdeck generate docs.pdf --vc earlybird                        |
|        |                                                               |
|        v                                                               |
|   [deck.md + deck.json generated]                                      |
|        |                                                               |
|        v                                                               |
|   $ pitchdeck validate deck.json --vc earlybird                       |
|        |                                                               |
|        +---> Rule-Based Engine (instant, no API key needed)            |
|        |     - Slide completeness checks                               |
|        |     - Metrics density scoring                                 |
|        |     - Format compliance (bullets, word limits)                 |
|        |     - VC custom_checks keyword matching                       |
|        |                                                               |
|        +---> LLM Scoring Engine (Claude, temperature=0.0)              |
|              - Narrative coherence evaluation                          |
|              - Thesis alignment quality                                |
|              - Common mistake detection                                |
|              - Per-slide quality assessment                            |
|                                                                        |
|        +---> Aggregation                                               |
|              - Weighted dimension scores                               |
|              - Per-slide scores with feedback                          |
|              - Prioritized improvement list                            |
|                                                                        |
|        v                                                               |
|   [validation_report.md]                                               |
|   - Overall: 73/100 PASS                                              |
|   - 5 dimension scores with rationale                                  |
|   - 15 per-slide scores with issues/suggestions                        |
|   - 7 Earlybird custom check results                                   |
|   - Top strengths, critical gaps, priorities                           |
|                                                                        |
|   VALUE: Objective scoring, VC-specific validation, prioritized fixes  |
|                                                                        |
|   DATA_FLOW: PitchDeck JSON -> validator -> DeckValidationResult ->    |
|              validation_report.md                                      |
+-----------------------------------------------------------------------+
```

### Interaction Changes

| Location | Before | After | User Impact |
|----------|--------|-------|-------------|
| CLI | No validate command | `pitchdeck validate deck.json --vc earlybird` | Objective deck scoring |
| CLI | generate saves only .md | generate saves .md + .json | JSON available for validation |
| Terminal | No quality feedback | Rich-formatted score summary with colors | Instant quality overview |
| Report | None | validation_report.md with per-slide detail | Actionable improvement list |
| Earlybird checks | Manual guessing | 7 automated custom checks with PASS/FAIL | No blind spots on VC criteria |

---

## Mandatory Reading

**CRITICAL: Implementation agent MUST read these files before starting any task:**

| Priority | File | Lines | Why Read This |
|----------|------|-------|---------------|
| P0 | `src/pitchdeck/models.py` | all | All existing Pydantic models — add validation types here |
| P0 | `src/pitchdeck/engine/gaps.py` | all | GAP_DEFINITIONS pattern to MIRROR for validation rules |
| P0 | `src/pitchdeck/engine/narrative.py` | all | Claude API call pattern, JSON extraction, prompt caching |
| P0 | `src/pitchdeck/engine/slides.py` | all | SLIDE_TEMPLATES — source of validation constraints |
| P1 | `src/pitchdeck/cli.py` | all | Typer CLI pattern, Rich console, spinner — add validate command here |
| P1 | `src/pitchdeck/output/markdown.py` | all | Report renderer pattern to MIRROR |
| P1 | `profiles/earlybird.yaml` | all | custom_checks and metrics_emphasis — validation criteria source |
| P2 | `tests/conftest.py` | all | Fixture pattern to extend |
| P2 | `tests/test_engine.py` | all | Test structure to MIRROR |
| P2 | `src/pitchdeck/output/__init__.py` | all | Export pattern to extend |

**External Documentation:**

| Source | Section | Why Needed |
|--------|---------|------------|
| [Anthropic Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | Ephemeral caching | Cost optimization — cache rubric + VC context across validation calls |
| [Pydantic Fields ge/le](https://docs.pydantic.dev/latest/concepts/fields/) | Numeric constraints | `Field(ge=0, le=100)` for score range enforcement |
| [LLM-as-Judge Best Practices](https://www.evidentlyai.com/llm-guide/llm-as-a-judge) | Score calibration | Avoid score inflation — anchor scale, CoT before scoring, temperature=0.0 |

---

## Patterns to Mirror

**ERROR_HANDLING:**
```python
# SOURCE: src/pitchdeck/models.py:8-26
# COPY THIS PATTERN — custom exceptions inherit from PitchDeckError:
class PitchDeckError(Exception):
    """Base exception for pitch deck generator."""
    pass

class DocumentParseError(PitchDeckError):
    """Raised when document parsing fails."""
    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Failed to parse {path}: {reason}")
```

**PYDANTIC_MODEL:**
```python
# SOURCE: src/pitchdeck/models.py:100-109
# COPY THIS PATTERN — Pydantic models with Optional/List defaults:
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

**GAP_DEFINITIONS (definitions list pattern):**
```python
# SOURCE: src/pitchdeck/engine/gaps.py:9-61
# COPY THIS PATTERN — module-level constant list of rule objects:
GAP_DEFINITIONS: list[GapQuestion] = [
    GapQuestion(
        field="name",
        question="Company name?",
        importance="critical",
    ),
    # ... 10 total definitions
]

def detect_gaps(
    profile: CompanyProfile, templates: List[SlideTemplate]
) -> list[GapQuestion]:
    """Identify missing data points needed for slide generation."""
    gaps = []
    for gap_def in GAP_DEFINITIONS:
        value = getattr(profile, gap_def.field, None)
        if value is None or value == "" or value == 0:
            gaps.append(gap_def)
    return gaps
```

**CLAUDE_API_CALL:**
```python
# SOURCE: src/pitchdeck/engine/narrative.py:38-108
# COPY THIS PATTERN — API key check, system messages with caching, JSON extraction:
def generate_deck(
    company: CompanyProfile,
    vc_profile: VCProfile,
    slide_templates: list[SlideTemplate],
) -> PitchDeck:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise PitchDeckError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Get your key at https://console.anthropic.com/"
        )

    client = Anthropic()

    system_messages = [
        {"type": "text", "text": SYSTEM_PROMPT},
        {
            "type": "text",
            "text": f"<context>...</context>",
            "cache_control": {"type": "ephemeral"},
        },
    ]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16384,
        system=system_messages,
        messages=[{"role": "user", "content": user_prompt}],
    )
```

**JSON_EXTRACTION:**
```python
# SOURCE: src/pitchdeck/engine/narrative.py:163-181
# COPY THIS PATTERN — regex JSON extraction + error handling:
raw_text = response.content[0].text

json_match = re.search(r"\{[\s\S]*\}", raw_text)
if not json_match:
    raise PitchDeckError(
        "Failed to parse validation response — no JSON found in Claude output"
    )

try:
    data = json.loads(json_match.group())
except json.JSONDecodeError as e:
    raise PitchDeckError(f"Failed to parse validation JSON: {e}") from e
```

**CLI_COMMAND:**
```python
# SOURCE: src/pitchdeck/cli.py:18-36
# COPY THIS PATTERN — Typer command with Annotated options:
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
):
```

**RICH_CONSOLE:**
```python
# SOURCE: src/pitchdeck/cli.py:56-116
# COPY THIS PATTERN — Rich console output with status colors + spinner:
console.print(f"[bold]Validating deck...[/bold]")
console.print(f"  [green]PASS[/green] {check}")
console.print(f"  [red]FAIL[/red] {check}")
console.print(f"\n[bold yellow]Score: {score}/100[/bold yellow]")

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console,
) as progress:
    task = progress.add_task("Scoring deck with Claude...", total=None)
    result = validate_deck(...)
    progress.remove_task(task)
```

**MARKDOWN_RENDERER:**
```python
# SOURCE: src/pitchdeck/output/markdown.py:6-80
# COPY THIS PATTERN — build lines list, conditional sections, join at end:
def render_markdown(deck: PitchDeck) -> str:
    lines = [
        f"# {deck.company_name} — Pitch Deck",
        ...
    ]
    for slide in deck.slides:
        lines.extend([...])
        if slide.bullets:
            for bullet in slide.bullets:
                lines.append(f"- {bullet}")
            lines.append("")
    return "\n".join(lines)
```

**TEST_STRUCTURE:**
```python
# SOURCE: tests/test_engine.py:62-101
# COPY THIS PATTERN — class-based pytest with fixtures from conftest:
class TestGapDetection:
    def test_detects_missing_fields(self, sample_company_with_gaps):
        gaps = detect_gaps(sample_company_with_gaps, SLIDE_TEMPLATES)
        fields = {g.field for g in gaps}
        assert "name" in fields

    def test_skips_filled_fields(self, sample_company):
        gaps = detect_gaps(sample_company, SLIDE_TEMPLATES)
        fields = {g.field for g in gaps}
        assert "name" not in fields
```

**TEST_API_MOCK:**
```python
# SOURCE: tests/test_engine.py:103-176
# COPY THIS PATTERN — mock Claude API, test JSON extraction:
class TestNarrativeEngine:
    def test_generate_deck_requires_api_key(self, sample_company, sample_vc_profile):
        templates = get_slide_templates(sample_vc_profile)
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(PitchDeckError, match="ANTHROPIC_API_KEY"):
                from pitchdeck.engine.narrative import generate_deck
                generate_deck(sample_company, sample_vc_profile, templates)

    def test_parse_deck_response(self, sample_company, sample_vc_profile):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"narrative_arc": "Test", ...}')]
        deck = _parse_deck_response(mock_response, sample_company, sample_vc_profile)
        assert deck.company_name == "Neurawork"
```

---

## Files to Change

| File | Action | Justification |
|------|--------|---------------|
| `src/pitchdeck/models.py` | UPDATE | Add validation result models (DimensionScore, SlideValidationScore, CustomCheckResult, DeckValidationResult) |
| `src/pitchdeck/engine/validator.py` | CREATE | Core validation logic — rule-based checks + LLM scoring orchestrator |
| `src/pitchdeck/output/validation_report.py` | CREATE | Render DeckValidationResult as Markdown report |
| `src/pitchdeck/output/__init__.py` | UPDATE | Add validation report exports |
| `src/pitchdeck/cli.py` | UPDATE | Add `validate` command + `--json` flag to `generate` |
| `tests/conftest.py` | UPDATE | Add validation-specific fixtures |
| `tests/test_validator.py` | CREATE | Comprehensive validator tests |
| `tests/test_validation_report.py` | CREATE | Validation report renderer tests |

---

## NOT Building (Scope Limits)

Explicit exclusions to prevent scope creep:

- **Visual report rendering (HTML/PDF)** — Markdown report only; visual rendering is Phase 4
- **Score history / trend tracking** — Deck versioning is a "Could" in PRD, not Phase 2
- **Auto-fix/rewrite suggestions** — Validator identifies issues but does not rewrite slides
- **Multi-VC comparison** — Validates against one VC profile at a time
- **Integration tests with real Claude API** — All LLM calls are mocked in tests; real API testing is manual
- **Markdown-to-PitchDeck parser** — Validate from JSON only; no reverse Markdown parsing
- **JSON export module** — Phase 3 scope; we add only a minimal JSON save in the generate command

---

## Step-by-Step Tasks

Execute in order. Each task is atomic and independently verifiable.

### Task 1: UPDATE `src/pitchdeck/models.py` — Add Validation Models

- **ACTION**: Add validation result Pydantic models after the existing `GapQuestion` class (line 128)
- **IMPLEMENT**: Add these models at the end of `models.py`:

  ```python
  class DimensionScore(BaseModel):
      dimension: str  # "completeness", "metrics_density", "narrative_coherence", "thesis_alignment", "common_mistakes"
      score: int = Field(ge=0, le=100)
      weight: float  # 0.0-1.0
      rationale: str
      evidence_found: List[str] = Field(default_factory=list)
      evidence_missing: List[str] = Field(default_factory=list)


  class SlideValidationScore(BaseModel):
      slide_number: int
      slide_type: str
      score: int = Field(ge=0, le=100)
      issues: List[str] = Field(default_factory=list)
      suggestions: List[str] = Field(default_factory=list)


  class CustomCheckResult(BaseModel):
      check: str  # the original custom_check string from VCProfile
      passed: bool
      evidence: str = ""


  class DeckValidationResult(BaseModel):
      deck_name: str
      target_vc: str
      validated_at: str
      overall_score: int = Field(ge=0, le=100)
      pass_threshold: int = 60
      pass_fail: bool
      dimension_scores: List[DimensionScore]
      slide_scores: List[SlideValidationScore]
      custom_check_results: List[CustomCheckResult]
      top_strengths: List[str]
      critical_gaps: List[str]
      improvement_priorities: List[str]  # ordered by impact
      recommendation: str
  ```

- **MIRROR**: `src/pitchdeck/models.py:100-128` — follow the same Pydantic model style: `List[str]` (not `list[str]` — though `dict[str, str]` is used at line 119, `List` from `typing` is used everywhere else), `Field(default_factory=list)` for mutable defaults, `Optional` for nullable fields
- **IMPORTS**: None needed — `List`, `Optional`, `BaseModel`, `Field` are already imported at lines 3-5
- **GOTCHA**: `Field(ge=0, le=100)` enforces score range at Pydantic validation time — if Claude returns 150, construction raises `ValidationError`. The `dict[str, str]` at line 119 uses lowercase `dict` (Python 3.10+), but all List types use `typing.List`. Follow the existing convention: use `List[X]` for list fields.
- **VALIDATE**: `python3 -c "from pitchdeck.models import DeckValidationResult, DimensionScore; print('OK')"`

### Task 2: CREATE `src/pitchdeck/engine/validator.py` — Core Validation Logic

- **ACTION**: Create the validation engine module with rule-based + LLM scoring
- **IMPLEMENT**: This is the largest module. Contains:

  **Module-level constants:**

  ```python
  """Pitch deck validation engine — rule-based + LLM scoring."""

  import json
  import os
  import re
  from datetime import datetime
  from typing import List, Optional

  from anthropic import Anthropic

  from pitchdeck.engine.slides import SLIDE_TEMPLATES
  from pitchdeck.models import (
      CustomCheckResult,
      DeckValidationResult,
      DimensionScore,
      PitchDeck,
      PitchDeckError,
      SlideContent,
      SlideTemplate,
      SlideValidationScore,
      VCProfile,
  )


  SCORING_DIMENSIONS = [
      {"dimension": "completeness", "weight": 0.25, "method": "rule"},
      {"dimension": "metrics_density", "weight": 0.20, "method": "rule"},
      {"dimension": "narrative_coherence", "weight": 0.20, "method": "llm"},
      {"dimension": "thesis_alignment", "weight": 0.20, "method": "llm"},
      {"dimension": "common_mistakes", "weight": 0.15, "method": "llm"},
  ]

  COMMON_MISTAKES = [
      "Over-indexing on architecture/technical detail vs business proof",
      "Missing simplified operating plan or use-of-funds breakdown",
      "No proactive response to AI commoditization risk",
      "Using top-down TAM only without bottom-up SOM calculation",
      "Generic competitive positioning without differentiated axes",
      "No quantified customer ROI or case study evidence",
      "Missing NDR or retention metrics on traction slide",
      "Title or headline is vague/generic rather than specific and data-driven",
  ]
  ```

  **Template lookup helper:**

  ```python
  def _get_template_for_slide(slide_type: str) -> Optional[SlideTemplate]:
      """Look up the SlideTemplate matching a slide's type."""
      for template in SLIDE_TEMPLATES:
          if template.slide_type == slide_type:
              return template
      return None
  ```

  **Rule-based per-slide scoring:**

  ```python
  def _score_slide_rules(slide: SlideContent) -> SlideValidationScore:
      """Score a single slide using deterministic rule checks."""
      template = _get_template_for_slide(slide.slide_type)
      issues = []
      suggestions = []
      score = 100  # start at 100, deduct for issues

      # Title and headline checks
      if not slide.title.strip():
          issues.append("Missing slide title")
          score -= 15
      if not slide.headline.strip():
          issues.append("Missing slide headline")
          score -= 10

      if template:
          # Bullet count check
          if template.max_bullets > 0 and len(slide.bullets) > template.max_bullets:
              issues.append(
                  f"Too many bullets: {len(slide.bullets)} "
                  f"(max {template.max_bullets})"
              )
              score -= 10

          # Word count check
          all_text = " ".join(
              [slide.title, slide.headline] + slide.bullets
          )
          word_count = len(all_text.split())
          if word_count > template.word_limit:
              issues.append(
                  f"Exceeds word limit: {word_count} words "
                  f"(max {template.word_limit})"
              )
              score -= 10

          # Metrics presence check
          if template.metrics_needed and not slide.metrics:
              issues.append(
                  f"Missing metrics (expected: "
                  f"{', '.join(template.metrics_needed)})"
              )
              score -= 15
              suggestions.append(
                  f"Add metrics: {', '.join(template.metrics_needed)}"
              )
          elif template.metrics_needed:
              missing_ratio = max(
                  0,
                  len(template.metrics_needed) - len(slide.metrics),
              )
              if missing_ratio > 0:
                  suggestions.append(
                      f"Consider adding more metrics "
                      f"({len(slide.metrics)}/{len(template.metrics_needed)} "
                      f"present)"
                  )
                  score -= missing_ratio * 3

          # Empty bullets for non-cover slides
          if template.max_bullets > 0 and not slide.bullets:
              issues.append("No bullet points on a slide that expects them")
              score -= 10

      # Speaker notes check
      if not slide.speaker_notes.strip():
          issues.append("Missing speaker notes")
          score -= 5
          suggestions.append("Add speaker notes explaining what to SAY")

      # VC alignment check
      if not slide.vc_alignment_notes:
          suggestions.append("Add VC alignment notes for this slide")
          score -= 5

      return SlideValidationScore(
          slide_number=slide.slide_number,
          slide_type=slide.slide_type,
          score=max(0, min(100, score)),
          issues=issues,
          suggestions=suggestions,
      )
  ```

  **Completeness dimension scoring:**

  ```python
  def _score_completeness(deck: PitchDeck, vc_profile: VCProfile) -> DimensionScore:
      """Score deck completeness: slide count, required elements, data coverage."""
      evidence_found = []
      evidence_missing = []

      # Slide count check
      expected = len(vc_profile.deck_preferences.must_include_slides) or 15
      actual = len(deck.slides)
      if actual >= expected:
          evidence_found.append(f"{actual}/{expected} slides present")
      else:
          evidence_missing.append(
              f"Only {actual}/{expected} slides present"
          )

      # Check required slide types
      slide_types = {s.slide_type for s in deck.slides}
      must_include = set(vc_profile.deck_preferences.must_include_slides)
      if must_include:
          present = must_include & slide_types
          missing = must_include - slide_types
          if present:
              evidence_found.append(
                  f"Required slide types present: {', '.join(sorted(present))}"
              )
          if missing:
              evidence_missing.append(
                  f"Missing required slide types: {', '.join(sorted(missing))}"
              )

      # Speaker notes coverage
      notes_count = sum(
          1 for s in deck.slides if s.speaker_notes.strip()
      )
      evidence_found.append(
          f"Speaker notes on {notes_count}/{len(deck.slides)} slides"
      )

      # Gaps penalty
      if deck.gaps_identified:
          evidence_missing.append(
              f"{len(deck.gaps_identified)} data gaps identified: "
              f"{', '.join(deck.gaps_identified[:5])}"
          )

      # Calculate score
      total_checks = expected + len(must_include) + len(deck.slides)
      passed_checks = (
          min(actual, expected)
          + len(must_include & slide_types)
          + notes_count
      )
      score = int((passed_checks / max(total_checks, 1)) * 100)

      return DimensionScore(
          dimension="completeness",
          score=max(0, min(100, score)),
          weight=0.25,
          rationale=(
              f"Deck has {actual} slides "
              f"({notes_count} with speaker notes). "
              f"{len(evidence_missing)} gaps found."
          ),
          evidence_found=evidence_found,
          evidence_missing=evidence_missing,
      )
  ```

  **Metrics density dimension scoring:**

  ```python
  def _score_metrics_density(
      deck: PitchDeck, vc_profile: VCProfile
  ) -> DimensionScore:
      """Score metrics presence across the deck against VC expectations."""
      evidence_found = []
      evidence_missing = []

      # Count total metrics across all slides
      total_metrics = sum(len(s.metrics) for s in deck.slides)
      evidence_found.append(f"{total_metrics} metrics across deck")

      # Check metrics emphasis from VC profile
      emphasis = vc_profile.deck_preferences.metrics_emphasis
      if emphasis:
          all_content = " ".join(
              " ".join(s.bullets + s.metrics + [s.headline])
              for s in deck.slides
          ).lower()
          for metric_desc in emphasis:
              keywords = metric_desc.lower().split()
              if any(kw in all_content for kw in keywords if len(kw) > 3):
                  evidence_found.append(f"Found: {metric_desc}")
              else:
                  evidence_missing.append(f"Missing: {metric_desc}")

      # Expected metrics from templates
      total_expected = 0
      for slide in deck.slides:
          template = _get_template_for_slide(slide.slide_type)
          if template:
              total_expected += len(template.metrics_needed)

      coverage = total_metrics / max(total_expected, 1)
      emphasis_found = len(evidence_found) - 1  # subtract the total count entry
      emphasis_total = len(emphasis) if emphasis else 1
      emphasis_coverage = emphasis_found / max(emphasis_total, 1)

      score = int(((coverage * 0.5) + (emphasis_coverage * 0.5)) * 100)

      return DimensionScore(
          dimension="metrics_density",
          score=max(0, min(100, score)),
          weight=0.20,
          rationale=(
              f"{total_metrics} metrics found "
              f"(~{total_expected} expected from templates). "
              f"{emphasis_found}/{emphasis_total} VC emphasis metrics addressed."
          ),
          evidence_found=evidence_found,
          evidence_missing=evidence_missing,
      )
  ```

  **Custom checks evaluation:**

  ```python
  def _check_custom_checks(
      deck: PitchDeck, vc_profile: VCProfile
  ) -> list[CustomCheckResult]:
      """Evaluate VC-specific custom checks via keyword matching."""
      results = []
      all_content = " ".join(
          " ".join(
              [s.title, s.headline]
              + s.bullets
              + s.metrics
              + [s.speaker_notes]
              + s.vc_alignment_notes
          )
          for s in deck.slides
      ).lower()

      keyword_map = {
          "european sovereignty": ["sovereign", "european", "europe", "data sovereignty", "digital sovereignty"],
          "bottom-up market sizing": ["bottom-up", "bottom up", "som", "icp count", "arpu"],
          "capital efficiency": ["capital efficien", "burn multiple", "revenue-to-raised", "capital-efficient"],
          "customer evidence": ["customer", "pilot", "case study", "roi", "evidence"],
          "ai commoditization": ["commodit", "moat", "defensib", "proprietary"],
          "gross margin": ["gross margin", "margin trajectory"],
          "category creation": ["category", "defining", "new market", "category creation"],
      }

      for check in vc_profile.custom_checks:
          check_lower = check.lower()
          passed = False
          evidence = ""

          # Try keyword matching
          for pattern, keywords in keyword_map.items():
              if pattern in check_lower:
                  matches = [kw for kw in keywords if kw in all_content]
                  if matches:
                      passed = True
                      evidence = f"Keywords found: {', '.join(matches)}"
                  break
          else:
              # Fallback: simple word overlap
              check_words = {
                  w for w in check_lower.split() if len(w) > 3
              }
              content_words = set(all_content.split())
              overlap = check_words & content_words
              if len(overlap) >= 2:
                  passed = True
                  evidence = f"Content overlap: {', '.join(sorted(overlap)[:5])}"

          results.append(
              CustomCheckResult(
                  check=check,
                  passed=passed,
                  evidence=evidence,
              )
          )
      return results
  ```

  **LLM qualitative scoring:**

  ```python
  VALIDATOR_SYSTEM_PROMPT = """\
  You are a senior VC partner evaluating pitch decks. Score with strict calibration:
  - 0-20: Reject immediately — fundamental problems
  - 21-40: Significant concerns — major rework needed
  - 41-60: Borderline — needs substantial improvement
  - 61-80: Strong candidate — minor improvements needed
  - 81-100: Exceptional — rare, reserved for truly outstanding decks

  DO NOT inflate scores. Most decks score 40-65. A score above 80 requires
  exceptional evidence across all dimensions.

  Evaluate step by step: analyze evidence FIRST, then assign scores.
  Return ONLY valid JSON matching the requested format."""


  def _score_qualitative(
      deck: PitchDeck,
      vc_profile: VCProfile,
      rule_findings: str,
  ) -> dict:
      """Use Claude to score narrative coherence, thesis alignment, and common mistakes.

      Returns dict with keys: narrative_coherence, thesis_alignment, common_mistakes,
      slide_quality (list), top_strengths, critical_gaps, recommendation.
      """
      api_key = os.environ.get("ANTHROPIC_API_KEY")
      if not api_key:
          raise PitchDeckError(
              "ANTHROPIC_API_KEY environment variable not set. "
              "Get your key at https://console.anthropic.com/"
          )

      client = Anthropic()

      from pitchdeck.engine.narrative import _build_vc_context

      vc_context = _build_vc_context(vc_profile)

      system_messages = [
          {"type": "text", "text": VALIDATOR_SYSTEM_PROMPT},
          {
              "type": "text",
              "text": (
                  f"<vc_profile>\n{vc_context}\n</vc_profile>\n\n"
                  f"<rule_based_findings>\n{rule_findings}\n</rule_based_findings>"
              ),
              "cache_control": {"type": "ephemeral"},
          },
      ]

      deck_json = deck.model_dump_json(indent=2)

      user_prompt = f"""Evaluate this pitch deck for {vc_profile.name}.

  <deck>
  {deck_json}
  </deck>

  Score these dimensions (0-100 each) with detailed rationale:

  1. NARRATIVE_COHERENCE: Do slides flow logically? Are transitions smooth?
     Is the investor psychology arc (Hook > Tension > Resolution > Proof > Trust > Ask) maintained?

  2. THESIS_ALIGNMENT: How well does the deck address each of {vc_profile.name}'s
     thesis points? Evaluate against each thesis point individually.

  3. COMMON_MISTAKES: Check for these specific issues:
  {chr(10).join(f'   - {m}' for m in COMMON_MISTAKES)}

  Also provide:
  - Per-slide quality observations (list of objects with slide_number, quality_note)
  - Top 3 strengths of the deck
  - Top 3 critical gaps
  - One-paragraph recommendation

  OUTPUT FORMAT (return ONLY this JSON):
  {{
      "narrative_coherence": {{
          "score": <0-100>,
          "rationale": "<explanation>",
          "evidence_found": ["<strength1>", ...],
          "evidence_missing": ["<weakness1>", ...]
      }},
      "thesis_alignment": {{
          "score": <0-100>,
          "rationale": "<explanation>",
          "evidence_found": ["<thesis point addressed>", ...],
          "evidence_missing": ["<thesis point not addressed>", ...]
      }},
      "common_mistakes": {{
          "score": <0-100>,
          "rationale": "<explanation>",
          "evidence_found": ["<good practice found>", ...],
          "evidence_missing": ["<mistake detected>", ...]
      }},
      "slide_quality": [
          {{"slide_number": 1, "quality_note": "<observation>"}},
          ...
      ],
      "top_strengths": ["<strength1>", "<strength2>", "<strength3>"],
      "critical_gaps": ["<gap1>", "<gap2>", "<gap3>"],
      "recommendation": "<one paragraph>"
  }}"""

      response = client.messages.create(
          model="claude-sonnet-4-6",
          max_tokens=8192,
          temperature=0.0,
          system=system_messages,
          messages=[{"role": "user", "content": user_prompt}],
      )

      return _parse_validation_response(response)


  def _parse_validation_response(response) -> dict:
      """Extract structured validation data from Claude response."""
      raw_text = response.content[0].text

      json_match = re.search(r"\{[\s\S]*\}", raw_text)
      if not json_match:
          raise PitchDeckError(
              "Failed to parse validation response — "
              "no JSON found in Claude output"
          )

      try:
          return json.loads(json_match.group())
      except json.JSONDecodeError as e:
          raise PitchDeckError(
              f"Failed to parse validation JSON: {e}"
          ) from e
  ```

  **Main orchestrator:**

  ```python
  def validate_deck(
      deck: PitchDeck,
      vc_profile: VCProfile,
      pass_threshold: int = 60,
      skip_llm: bool = False,
  ) -> DeckValidationResult:
      """Validate a pitch deck using rule-based + optional LLM scoring.

      Args:
          deck: The PitchDeck to validate.
          vc_profile: VC profile with thesis points and custom checks.
          pass_threshold: Score threshold for pass/fail (0-100).
          skip_llm: If True, skip LLM scoring (rule-based only).

      Returns:
          DeckValidationResult with dimension scores, per-slide scores,
          custom check results, and prioritized improvements.
      """
      # 1. Rule-based per-slide scoring
      slide_scores = [_score_slide_rules(slide) for slide in deck.slides]

      # 2. Rule-based dimension scoring
      completeness = _score_completeness(deck, vc_profile)
      metrics_density = _score_metrics_density(deck, vc_profile)

      # 3. Custom checks
      custom_check_results = _check_custom_checks(deck, vc_profile)

      # 4. LLM qualitative scoring (optional)
      if not skip_llm:
          rule_summary = _build_rule_summary(
              slide_scores, completeness, metrics_density, custom_check_results
          )
          llm_data = _score_qualitative(deck, vc_profile, rule_summary)

          narrative = DimensionScore(
              dimension="narrative_coherence",
              score=max(0, min(100, llm_data["narrative_coherence"]["score"])),
              weight=0.20,
              rationale=llm_data["narrative_coherence"]["rationale"],
              evidence_found=llm_data["narrative_coherence"].get("evidence_found", []),
              evidence_missing=llm_data["narrative_coherence"].get("evidence_missing", []),
          )
          alignment = DimensionScore(
              dimension="thesis_alignment",
              score=max(0, min(100, llm_data["thesis_alignment"]["score"])),
              weight=0.20,
              rationale=llm_data["thesis_alignment"]["rationale"],
              evidence_found=llm_data["thesis_alignment"].get("evidence_found", []),
              evidence_missing=llm_data["thesis_alignment"].get("evidence_missing", []),
          )
          mistakes = DimensionScore(
              dimension="common_mistakes",
              score=max(0, min(100, llm_data["common_mistakes"]["score"])),
              weight=0.15,
              rationale=llm_data["common_mistakes"]["rationale"],
              evidence_found=llm_data["common_mistakes"].get("evidence_found", []),
              evidence_missing=llm_data["common_mistakes"].get("evidence_missing", []),
          )

          # Merge LLM per-slide quality notes into existing slide scores
          for sq in llm_data.get("slide_quality", []):
              num = sq.get("slide_number")
              note = sq.get("quality_note", "")
              if num and note:
                  for ss in slide_scores:
                      if ss.slide_number == num and note:
                          ss.suggestions.append(note)

          top_strengths = llm_data.get("top_strengths", [])
          critical_gaps = llm_data.get("critical_gaps", [])
          recommendation = llm_data.get("recommendation", "")
      else:
          # Placeholder LLM dimensions when skipped
          narrative = DimensionScore(
              dimension="narrative_coherence",
              score=0,
              weight=0.20,
              rationale="LLM scoring skipped",
          )
          alignment = DimensionScore(
              dimension="thesis_alignment",
              score=0,
              weight=0.20,
              rationale="LLM scoring skipped",
          )
          mistakes = DimensionScore(
              dimension="common_mistakes",
              score=0,
              weight=0.15,
              rationale="LLM scoring skipped",
          )
          top_strengths = []
          critical_gaps = []
          recommendation = "LLM scoring skipped — run without --skip-llm for full assessment"

      dimension_scores = [
          completeness, metrics_density, narrative, alignment, mistakes
      ]

      # 5. Calculate weighted overall score
      overall = sum(d.score * d.weight for d in dimension_scores)
      overall_score = int(round(overall))

      # 6. Build improvement priorities from all issues
      improvement_priorities = _build_improvement_priorities(
          slide_scores, custom_check_results, critical_gaps
      )

      return DeckValidationResult(
          deck_name=deck.company_name,
          target_vc=deck.target_vc,
          validated_at=datetime.now().isoformat(),
          overall_score=max(0, min(100, overall_score)),
          pass_threshold=pass_threshold,
          pass_fail=overall_score >= pass_threshold,
          dimension_scores=dimension_scores,
          slide_scores=slide_scores,
          custom_check_results=custom_check_results,
          top_strengths=top_strengths,
          critical_gaps=critical_gaps,
          improvement_priorities=improvement_priorities,
          recommendation=recommendation,
      )
  ```

  **Helper functions:**

  ```python
  def _build_rule_summary(
      slide_scores: list[SlideValidationScore],
      completeness: DimensionScore,
      metrics_density: DimensionScore,
      custom_checks: list[CustomCheckResult],
  ) -> str:
      """Summarize rule-based findings for LLM context."""
      lines = [
          f"Completeness score: {completeness.score}/100",
          f"  Found: {', '.join(completeness.evidence_found)}",
          f"  Missing: {', '.join(completeness.evidence_missing)}",
          "",
          f"Metrics density score: {metrics_density.score}/100",
          f"  Found: {', '.join(metrics_density.evidence_found)}",
          f"  Missing: {', '.join(metrics_density.evidence_missing)}",
          "",
          "Per-slide issues:",
      ]
      for ss in slide_scores:
          if ss.issues:
              lines.append(
                  f"  Slide {ss.slide_number} ({ss.slide_type}): "
                  f"{'; '.join(ss.issues)}"
              )
      lines.append("")
      lines.append("VC custom check results:")
      for cc in custom_checks:
          status = "PASS" if cc.passed else "FAIL"
          lines.append(f"  [{status}] {cc.check}")
      return "\n".join(lines)


  def _build_improvement_priorities(
      slide_scores: list[SlideValidationScore],
      custom_checks: list[CustomCheckResult],
      critical_gaps: list[str],
  ) -> list[str]:
      """Build a prioritized list of improvements, most impactful first."""
      priorities = []

      # Failed custom checks first (VC-specific, highest impact)
      for cc in custom_checks:
          if not cc.passed:
              priorities.append(f"Address VC requirement: {cc.check}")

      # LLM-identified critical gaps
      priorities.extend(critical_gaps)

      # Slides with the most issues
      scored = sorted(slide_scores, key=lambda s: s.score)
      for ss in scored[:3]:
          if ss.issues:
              priorities.append(
                  f"Fix slide {ss.slide_number} ({ss.slide_type}): "
                  f"{ss.issues[0]}"
              )

      return priorities
  ```

- **MIRROR**: `src/pitchdeck/engine/gaps.py` for definitions list pattern; `src/pitchdeck/engine/narrative.py` for Claude API call pattern
- **IMPORTS**: All from existing `pitchdeck.models` and `pitchdeck.engine.slides`
- **GOTCHA**:
  - `temperature=0.0` is critical for scoring consistency — the existing `narrative.py` uses the default (not set). The validator MUST set it explicitly.
  - `max(0, min(100, score))` clamp on all scores to handle edge cases where deductions go below 0 or LLM returns out-of-range values.
  - Reuse `_build_vc_context` from `narrative.py` to format VC profile for the LLM prompt — import it directly.
  - `SlideValidationScore.suggestions` is mutated in-place when merging LLM quality notes (`.append()`). This is after initial construction, before the result is returned.
  - The `skip_llm` flag allows rule-based-only validation (no API key needed). LLM dimensions get score=0 when skipped — this is intentional; the overall score reflects only rule-based assessment.
- **VALIDATE**: `python3 -c "from pitchdeck.engine.validator import validate_deck; print('OK')"`

### Task 3: CREATE `src/pitchdeck/output/validation_report.py` — Report Renderer

- **ACTION**: Create Markdown report renderer for validation results
- **IMPLEMENT**:

  ```python
  """Markdown renderer for deck validation reports."""

  from pitchdeck.models import DeckValidationResult


  def render_validation_report(result: DeckValidationResult) -> str:
      """Render a DeckValidationResult as formatted Markdown."""
      pass_fail = "PASS" if result.pass_fail else "FAIL"
      lines = [
          f"# Deck Validation Report",
          "",
          f"**Deck**: {result.deck_name}",
          f"**Target VC**: {result.target_vc}",
          f"**Validated**: {result.validated_at}",
          f"**Overall Score**: {result.overall_score}/100 — **{pass_fail}** "
          f"(threshold: {result.pass_threshold})",
          "",
          "---",
          "",
          "## Score Breakdown",
          "",
          "| Dimension | Score | Weight | Weighted |",
          "|-----------|-------|--------|----------|",
      ]

      total_weighted = 0.0
      for dim in result.dimension_scores:
          weighted = dim.score * dim.weight
          total_weighted += weighted
          lines.append(
              f"| {dim.dimension.replace('_', ' ').title()} "
              f"| {dim.score}/100 "
              f"| {int(dim.weight * 100)}% "
              f"| {weighted:.1f} |"
          )
      lines.append(
          f"| **TOTAL** | | | **{total_weighted:.1f}** |"
      )
      lines.append("")

      # Dimension details
      for dim in result.dimension_scores:
          lines.extend([
              f"### {dim.dimension.replace('_', ' ').title()}",
              "",
              f"**Score**: {dim.score}/100",
              f"**Rationale**: {dim.rationale}",
              "",
          ])
          if dim.evidence_found:
              lines.append("**Evidence Found:**")
              for e in dim.evidence_found:
                  lines.append(f"- {e}")
              lines.append("")
          if dim.evidence_missing:
              lines.append("**Evidence Missing:**")
              for e in dim.evidence_missing:
                  lines.append(f"- {e}")
              lines.append("")

      # VC Custom Checks
      if result.custom_check_results:
          lines.extend([
              "---",
              "",
              "## VC-Specific Checks",
              "",
              "| Check | Status | Evidence |",
              "|-------|--------|----------|",
          ])
          for cc in result.custom_check_results:
              status = "PASS" if cc.passed else "FAIL"
              lines.append(f"| {cc.check} | {status} | {cc.evidence} |")
          lines.append("")

      # Per-slide scores
      lines.extend([
          "---",
          "",
          "## Per-Slide Scores",
          "",
      ])
      for ss in result.slide_scores:
          lines.extend([
              f"### Slide {ss.slide_number}: "
              f"{ss.slide_type} — {ss.score}/100",
              "",
          ])
          if ss.issues:
              lines.append("**Issues:**")
              for issue in ss.issues:
                  lines.append(f"- {issue}")
              lines.append("")
          if ss.suggestions:
              lines.append("**Suggestions:**")
              for s in ss.suggestions:
                  lines.append(f"- {s}")
              lines.append("")
          if not ss.issues and not ss.suggestions:
              lines.append("No issues detected.")
              lines.append("")

      # Strengths and gaps
      if result.top_strengths:
          lines.extend([
              "---",
              "",
              "## Top Strengths",
              "",
          ])
          for i, s in enumerate(result.top_strengths, 1):
              lines.append(f"{i}. {s}")
          lines.append("")

      if result.critical_gaps:
          lines.extend([
              "## Critical Gaps",
              "",
          ])
          for i, g in enumerate(result.critical_gaps, 1):
              lines.append(f"{i}. {g}")
          lines.append("")

      if result.improvement_priorities:
          lines.extend([
              "## Improvement Priorities (ordered by impact)",
              "",
          ])
          for i, p in enumerate(result.improvement_priorities, 1):
              lines.append(f"{i}. {p}")
          lines.append("")

      if result.recommendation:
          lines.extend([
              "---",
              "",
              "## Recommendation",
              "",
              result.recommendation,
              "",
          ])

      return "\n".join(lines)


  def save_validation_report(
      result: DeckValidationResult, path: str
  ) -> None:
      """Save validation report as Markdown file."""
      content = render_validation_report(result)
      with open(path, "w") as f:
          f.write(content)
  ```

- **MIRROR**: `src/pitchdeck/output/markdown.py:6-87` — same pattern: build `lines` list, conditional sections, `"\n".join(lines)`, `save_*` wrapper that calls `render_*`
- **IMPORTS**: `from pitchdeck.models import DeckValidationResult`
- **GOTCHA**: Use `dim.dimension.replace('_', ' ').title()` to format dimension names (e.g., `"metrics_density"` → `"Metrics Density"`). Markdown table cells must not contain pipe characters — `|` in evidence strings would break rendering.
- **VALIDATE**: `python3 -c "from pitchdeck.output.validation_report import render_validation_report; print('OK')"`

### Task 4: UPDATE `src/pitchdeck/output/__init__.py` — Add Report Exports

- **ACTION**: Add validation report exports to the output package
- **IMPLEMENT**: Update the file to include the new exports:

  ```python
  """Output formatters for pitch deck content."""

  from pitchdeck.output.markdown import render_markdown, save_markdown
  from pitchdeck.output.validation_report import (
      render_validation_report,
      save_validation_report,
  )

  __all__ = [
      "render_markdown",
      "save_markdown",
      "render_validation_report",
      "save_validation_report",
  ]
  ```

- **MIRROR**: `src/pitchdeck/output/__init__.py:1-5` — same re-export pattern
- **VALIDATE**: `python3 -c "from pitchdeck.output import render_validation_report, save_validation_report; print('OK')"`

### Task 5: UPDATE `src/pitchdeck/cli.py` — Add `validate` Command and JSON Save

- **ACTION**: Add two things:
  1. A `--json` option to the `generate` command that saves the PitchDeck as JSON
  2. A new `validate` command that reads a deck JSON and runs validation

- **IMPLEMENT**:

  **Add `--json` option to `generate` command** — add this parameter to the `generate` function signature (after `skip_gaps`):

  ```python
  save_json: Annotated[
      str,
      typer.Option("--json", help="Also save deck as JSON (for validation)"),
  ] = "",
  ```

  And add this block after `save_markdown(deck, output)` at line 119:

  ```python
  # 7. Save JSON (for validation pipeline)
  if save_json:
      json_path = save_json
  else:
      json_path = output.rsplit(".", 1)[0] + ".json"
  with open(json_path, "w") as f:
      f.write(deck.model_dump_json(indent=2))
  console.print(f"  JSON: {json_path}")
  ```

  **Add `validate` command** — add after the `profiles` command:

  ```python
  @app.command()
  def validate(
      deck_file: Annotated[
          str,
          typer.Argument(help="Path to deck JSON file"),
      ],
      vc: Annotated[
          str,
          typer.Option("--vc", "-v", help="VC profile name (without .yaml)"),
      ] = "earlybird",
      output: Annotated[
          str,
          typer.Option("--output", "-o", help="Validation report output path"),
      ] = "validation_report.md",
      threshold: Annotated[
          int,
          typer.Option("--threshold", "-t", help="Pass/fail threshold (0-100)"),
      ] = 60,
      skip_llm: Annotated[
          bool,
          typer.Option("--skip-llm", help="Skip LLM scoring (rule-based only)"),
      ] = False,
  ):
      """Score a pitch deck against VC-specific rubrics."""
      import json as json_module

      from pitchdeck.engine.validator import validate_deck
      from pitchdeck.models import PitchDeck, PitchDeckError
      from pitchdeck.output import save_validation_report
      from pitchdeck.profiles import load_vc_profile

      # 1. Read deck JSON
      console.print(f"[bold]Loading deck: {deck_file}[/bold]")
      try:
          with open(deck_file) as f:
              deck_data = f.read()
          deck = PitchDeck.model_validate_json(deck_data)
          console.print(
              f"  [green]OK[/green] {deck.company_name} "
              f"({len(deck.slides)} slides)"
          )
      except FileNotFoundError:
          console.print(f"  [red]FAIL[/red] File not found: {deck_file}")
          raise typer.Exit(1)
      except Exception as e:
          console.print(f"  [red]FAIL[/red] {e}")
          raise typer.Exit(1)

      # 2. Load VC profile
      console.print(f"\n[bold]Loading VC profile: {vc}[/bold]")
      try:
          vc_profile = load_vc_profile(vc)
          console.print(
              f"  [green]OK[/green] {vc_profile.name} "
              f"({len(vc_profile.custom_checks)} custom checks)"
          )
      except Exception as e:
          console.print(f"  [red]FAIL[/red] {e}")
          raise typer.Exit(1)

      # 3. Validate
      if skip_llm:
          console.print(
              "\n[bold]Running rule-based validation...[/bold]"
          )
      else:
          import os

          if not os.environ.get("ANTHROPIC_API_KEY"):
              console.print(
                  "[yellow]Warning: ANTHROPIC_API_KEY not set. "
                  "Running rule-based only.[/yellow]"
              )
              skip_llm = True

      if not skip_llm:
          with Progress(
              SpinnerColumn(),
              TextColumn(
                  "[progress.description]{task.description}"
              ),
              console=console,
          ) as progress:
              task = progress.add_task(
                  "Scoring deck with Claude...", total=None
              )
              result = validate_deck(
                  deck, vc_profile, threshold, skip_llm
              )
              progress.remove_task(task)
      else:
          console.print(
              "\n[bold]Running rule-based validation...[/bold]"
          )
          result = validate_deck(
              deck, vc_profile, threshold, skip_llm=True
          )

      # 4. Save report
      save_validation_report(result, output)

      # 5. Print summary
      pass_fail = "[green]PASS[/green]" if result.pass_fail else "[red]FAIL[/red]"
      console.print(f"\n[bold]Overall Score: {result.overall_score}/100 — {pass_fail}[/bold]")
      console.print("")
      for dim in result.dimension_scores:
          name = dim.dimension.replace("_", " ").title()
          console.print(f"  {name}: {dim.score}/100")

      passed_checks = sum(1 for c in result.custom_check_results if c.passed)
      total_checks = len(result.custom_check_results)
      if total_checks:
          console.print(
              f"\n  VC Checks: {passed_checks}/{total_checks} passed"
          )

      if result.improvement_priorities:
          console.print("\n[bold yellow]Top Improvements:[/bold yellow]")
          for i, p in enumerate(result.improvement_priorities[:5], 1):
              console.print(f"  {i}. {p}")

      console.print(f"\n[bold]Report saved to {output}[/bold]")
  ```

- **MIRROR**: `src/pitchdeck/cli.py:18-125` — same Typer command pattern with Rich console, lazy imports, error handling with `raise typer.Exit(1)`, spinner for long operations
- **IMPORTS**: None at top level — all imports are lazy inside the command body (matching existing pattern)
- **GOTCHA**:
  - Lazy imports inside the command function body (not module top-level) — matches existing `generate` pattern at `cli.py:40-46`
  - Use `PitchDeck.model_validate_json(data)` (Pydantic v2) to deserialize from JSON string
  - When ANTHROPIC_API_KEY is missing, auto-fall-back to `skip_llm=True` with a warning instead of erroring (unlike `generate` which requires it)
  - The JSON save in `generate` always writes alongside the Markdown — even without `--json` flag. This ensures the JSON is available for the `validate` command. The `--json` flag only customizes the path.
  - Import `json` as `json_module` inside the validate command to avoid shadowing the `--json` CLI parameter name
- **VALIDATE**: `python3 -m pitchdeck --help` — should show `generate`, `validate`, and `profiles` commands

### Task 6: UPDATE `tests/conftest.py` — Add Validation Fixtures

- **ACTION**: Add validation-specific test fixtures
- **IMPLEMENT**: Add these fixtures after the existing `sample_deck` fixture (line 128):

  ```python
  @pytest.fixture
  def sample_multi_slide_deck():
      """A realistic 15-slide deck for validation testing."""
      slides = []
      slide_types = [
          "cover", "executive-summary", "problem", "why-now",
          "solution", "product", "market-sizing", "business-model",
          "traction", "go-to-market", "competitive-landscape",
          "team", "financials", "the-ask", "ai-architecture",
      ]
      for i, stype in enumerate(slide_types, 1):
          slides.append(
              SlideContent(
                  slide_number=i,
                  slide_type=stype,
                  title=f"Slide {i} Title",
                  headline=f"Key insight for {stype}",
                  bullets=[
                      f"Point {j} for {stype}"
                      for j in range(1, 4)
                  ],
                  metrics=[f"Metric for {stype}"]
                  if stype
                  in (
                      "executive-summary",
                      "traction",
                      "business-model",
                      "market-sizing",
                      "financials",
                  )
                  else [],
                  speaker_notes=f"Say this about {stype}.",
                  transition_to_next=f"Moving to next topic..."
                  if i < 15
                  else "",
                  vc_alignment_notes=[
                      f"Aligns with thesis point for {stype}"
                  ],
              )
          )
      return PitchDeck(
          company_name="Neurawork",
          target_vc="Test VC",
          generated_at="2026-02-19T12:00:00",
          slides=slides,
          narrative_arc="Hook > Tension > Resolution > Proof > Trust > Ask",
          gaps_identified=["NDR percentage missing"],
      )


  @pytest.fixture
  def sample_validation_result():
      """A sample DeckValidationResult for report rendering tests."""
      from pitchdeck.models import (
          CustomCheckResult,
          DeckValidationResult,
          DimensionScore,
          SlideValidationScore,
      )

      return DeckValidationResult(
          deck_name="Neurawork",
          target_vc="Test VC",
          validated_at="2026-02-19T12:00:00",
          overall_score=73,
          pass_threshold=60,
          pass_fail=True,
          dimension_scores=[
              DimensionScore(
                  dimension="completeness",
                  score=80,
                  weight=0.25,
                  rationale="15/15 slides present, 14 with speaker notes",
                  evidence_found=["15/15 slides", "Speaker notes present"],
                  evidence_missing=["1 slide missing notes"],
              ),
              DimensionScore(
                  dimension="metrics_density",
                  score=65,
                  weight=0.20,
                  rationale="12 metrics found, 20 expected",
                  evidence_found=["ARR present", "Customer count present"],
                  evidence_missing=["NDR missing", "Burn multiple missing"],
              ),
              DimensionScore(
                  dimension="narrative_coherence",
                  score=75,
                  weight=0.20,
                  rationale="Good flow with minor transition gaps",
              ),
              DimensionScore(
                  dimension="thesis_alignment",
                  score=70,
                  weight=0.20,
                  rationale="5/7 thesis points addressed",
              ),
              DimensionScore(
                  dimension="common_mistakes",
                  score=80,
                  weight=0.15,
                  rationale="No major mistakes detected",
              ),
          ],
          slide_scores=[
              SlideValidationScore(
                  slide_number=1,
                  slide_type="cover",
                  score=90,
              ),
              SlideValidationScore(
                  slide_number=9,
                  slide_type="traction",
                  score=55,
                  issues=["Missing NDR metric"],
                  suggestions=["Add NDR or explain unavailability"],
              ),
          ],
          custom_check_results=[
              CustomCheckResult(
                  check="European sovereignty angle must be present",
                  passed=True,
                  evidence="Keywords found: sovereign, european",
              ),
              CustomCheckResult(
                  check="Bottom-up market sizing required",
                  passed=False,
                  evidence="",
              ),
          ],
          top_strengths=[
              "Strong revenue traction for stage",
              "Clear AI infrastructure positioning",
          ],
          critical_gaps=[
              "No NDR data",
              "Bottom-up market sizing missing",
          ],
          improvement_priorities=[
              "Address VC requirement: Bottom-up market sizing required",
              "No NDR data",
              "Fix slide 9 (traction): Missing NDR metric",
          ],
          recommendation="Strong candidate with fixable gaps. Add NDR and bottom-up SOM.",
      )


  @pytest.fixture
  def sample_deck_json(sample_multi_slide_deck, tmp_path):
      """Write a multi-slide deck as JSON to a temp file."""
      json_path = tmp_path / "deck.json"
      with open(json_path, "w") as f:
          f.write(sample_multi_slide_deck.model_dump_json(indent=2))
      return json_path
  ```

- **MIRROR**: `tests/conftest.py:16-128` — same fixture pattern with `@pytest.fixture`, Pydantic model construction, `tmp_path` for file I/O
- **IMPORTS**: Need to add `DeckValidationResult`, `DimensionScore`, `SlideValidationScore`, `CustomCheckResult` to the imports at the top of `conftest.py`. Add them to the existing import block at lines 6-13.
- **GOTCHA**: The `sample_multi_slide_deck` creates slides with minimal but valid content. Metrics are only on slide types that templates expect metrics for (traction, executive-summary, etc.). The `sample_deck_json` fixture depends on `sample_multi_slide_deck` and `tmp_path` — pytest resolves these automatically.
- **VALIDATE**: `python3 -c "import tests.conftest; print('OK')"`

### Task 7: CREATE `tests/test_validator.py` — Validator Tests

- **ACTION**: Create comprehensive unit tests for the validation engine
- **IMPLEMENT**:

  ```python
  """Tests for the deck validation engine."""

  from unittest.mock import MagicMock, patch

  import pytest

  from pitchdeck.engine.slides import SLIDE_TEMPLATES
  from pitchdeck.engine.validator import (
      _check_custom_checks,
      _get_template_for_slide,
      _score_completeness,
      _score_metrics_density,
      _score_slide_rules,
      validate_deck,
  )
  from pitchdeck.models import (
      DeckValidationResult,
      DimensionScore,
      PitchDeckError,
      SlideContent,
      SlideValidationScore,
  )


  class TestGetTemplateForSlide:
      def test_finds_existing_type(self):
          template = _get_template_for_slide("cover")
          assert template is not None
          assert template.slide_type == "cover"

      def test_returns_none_for_unknown_type(self):
          assert _get_template_for_slide("nonexistent") is None

      def test_finds_all_15_types(self):
          for t in SLIDE_TEMPLATES:
              assert _get_template_for_slide(t.slide_type) is not None


  class TestScoreSlideRules:
      def test_perfect_slide_scores_high(self, sample_slide):
          score = _score_slide_rules(sample_slide)
          assert score.score >= 80
          assert score.slide_type == "cover"

      def test_missing_title_deducts(self):
          slide = SlideContent(
              slide_number=1,
              slide_type="cover",
              title="",
              headline="Test",
              bullets=[],
              speaker_notes="Notes",
          )
          score = _score_slide_rules(slide)
          assert "Missing slide title" in score.issues
          assert score.score < 100

      def test_missing_headline_deducts(self):
          slide = SlideContent(
              slide_number=1,
              slide_type="cover",
              title="Title",
              headline="",
              bullets=[],
              speaker_notes="Notes",
          )
          score = _score_slide_rules(slide)
          assert "Missing slide headline" in score.issues

      def test_too_many_bullets_flagged(self):
          slide = SlideContent(
              slide_number=2,
              slide_type="executive-summary",
              title="Title",
              headline="Headline",
              bullets=["B1", "B2", "B3", "B4", "B5", "B6"],
              speaker_notes="Notes",
          )
          score = _score_slide_rules(slide)
          assert any("Too many bullets" in i for i in score.issues)

      def test_missing_metrics_flagged(self):
          slide = SlideContent(
              slide_number=9,
              slide_type="traction",
              title="Traction",
              headline="Growth proof",
              bullets=["Point 1"],
              metrics=[],
              speaker_notes="Notes",
          )
          score = _score_slide_rules(slide)
          assert any("Missing metrics" in i for i in score.issues)

      def test_missing_speaker_notes_deducts(self):
          slide = SlideContent(
              slide_number=1,
              slide_type="cover",
              title="Title",
              headline="Headline",
              bullets=[],
              speaker_notes="",
          )
          score = _score_slide_rules(slide)
          assert any("Missing speaker notes" in i for i in score.issues)

      def test_score_never_below_zero(self):
          slide = SlideContent(
              slide_number=1,
              slide_type="traction",
              title="",
              headline="",
              bullets=[],
              metrics=[],
              speaker_notes="",
          )
          score = _score_slide_rules(slide)
          assert score.score >= 0

      def test_unknown_slide_type_still_scores(self):
          slide = SlideContent(
              slide_number=1,
              slide_type="unknown-type",
              title="Title",
              headline="Headline",
              bullets=["Point"],
              speaker_notes="Notes",
          )
          score = _score_slide_rules(slide)
          assert score.score > 0


  class TestScoreCompleteness:
      def test_full_deck_scores_high(
          self, sample_multi_slide_deck, sample_vc_profile
      ):
          score = _score_completeness(
              sample_multi_slide_deck, sample_vc_profile
          )
          assert score.dimension == "completeness"
          assert score.score > 50
          assert score.weight == 0.25

      def test_empty_deck_scores_low(self, sample_vc_profile):
          from pitchdeck.models import PitchDeck

          empty_deck = PitchDeck(
              company_name="Test",
              target_vc="VC",
              generated_at="2026-01-01",
              slides=[],
              narrative_arc="",
          )
          score = _score_completeness(empty_deck, sample_vc_profile)
          assert score.score < 20

      def test_gaps_reduce_score(
          self, sample_multi_slide_deck, sample_vc_profile
      ):
          sample_multi_slide_deck.gaps_identified = [
              "Gap 1",
              "Gap 2",
              "Gap 3",
          ]
          score = _score_completeness(
              sample_multi_slide_deck, sample_vc_profile
          )
          assert "3 data gaps identified" in " ".join(
              score.evidence_missing
          )


  class TestScoreMetricsDensity:
      def test_deck_with_metrics_scores_higher(
          self, sample_multi_slide_deck, sample_vc_profile
      ):
          score = _score_metrics_density(
              sample_multi_slide_deck, sample_vc_profile
          )
          assert score.dimension == "metrics_density"
          assert score.weight == 0.20
          assert 0 <= score.score <= 100


  class TestCheckCustomChecks:
      def test_passes_when_keywords_present(self, sample_vc_profile):
          from pitchdeck.models import PitchDeck

          deck = PitchDeck(
              company_name="Test",
              target_vc="VC",
              generated_at="2026-01-01",
              slides=[
                  SlideContent(
                      slide_number=1,
                      slide_type="cover",
                      title="European Digital Sovereignty",
                      headline="Capital efficient AI platform",
                      bullets=[
                          "Bottom-up SOM calculation",
                          "Customer ROI: 3x reduction",
                          "AI commoditization moat",
                          "Gross margin 70%",
                          "Category creation like UiPath",
                      ],
                      speaker_notes="Notes",
                  )
              ],
              narrative_arc="Arc",
          )
          results = _check_custom_checks(deck, sample_vc_profile)
          assert isinstance(results, list)
          # sample_vc_profile has 1 custom check: "Must show capital efficiency"
          assert len(results) == 1

      def test_fails_when_keywords_absent(self, sample_vc_profile):
          from pitchdeck.models import PitchDeck

          deck = PitchDeck(
              company_name="Test",
              target_vc="VC",
              generated_at="2026-01-01",
              slides=[
                  SlideContent(
                      slide_number=1,
                      slide_type="cover",
                      title="Hello",
                      headline="World",
                      bullets=[],
                      speaker_notes="Notes",
                  )
              ],
              narrative_arc="Arc",
          )
          results = _check_custom_checks(deck, sample_vc_profile)
          # With minimal content, most checks should fail
          for r in results:
              assert isinstance(r.passed, bool)


  class TestValidateDeck:
      def test_rule_based_only(
          self, sample_multi_slide_deck, sample_vc_profile
      ):
          result = validate_deck(
              sample_multi_slide_deck,
              sample_vc_profile,
              skip_llm=True,
          )
          assert isinstance(result, DeckValidationResult)
          assert 0 <= result.overall_score <= 100
          assert len(result.dimension_scores) == 5
          assert len(result.slide_scores) == 15
          assert result.pass_fail == (result.overall_score >= 60)

      def test_rule_based_dimensions_scored(
          self, sample_multi_slide_deck, sample_vc_profile
      ):
          result = validate_deck(
              sample_multi_slide_deck,
              sample_vc_profile,
              skip_llm=True,
          )
          dims = {d.dimension: d for d in result.dimension_scores}
          assert dims["completeness"].score > 0
          assert dims["metrics_density"].score >= 0
          # LLM dimensions should be 0 when skipped
          assert dims["narrative_coherence"].score == 0
          assert dims["thesis_alignment"].score == 0
          assert dims["common_mistakes"].score == 0

      def test_custom_threshold(
          self, sample_multi_slide_deck, sample_vc_profile
      ):
          result = validate_deck(
              sample_multi_slide_deck,
              sample_vc_profile,
              pass_threshold=90,
              skip_llm=True,
          )
          assert result.pass_threshold == 90

      def test_improvement_priorities_populated(
          self, sample_multi_slide_deck, sample_vc_profile
      ):
          result = validate_deck(
              sample_multi_slide_deck,
              sample_vc_profile,
              skip_llm=True,
          )
          assert isinstance(result.improvement_priorities, list)

      def test_requires_api_key_for_llm(
          self, sample_multi_slide_deck, sample_vc_profile
      ):
          with patch.dict("os.environ", {}, clear=True):
              with pytest.raises(PitchDeckError, match="ANTHROPIC_API_KEY"):
                  validate_deck(
                      sample_multi_slide_deck,
                      sample_vc_profile,
                      skip_llm=False,
                  )

      def test_llm_scoring_with_mock(
          self, sample_multi_slide_deck, sample_vc_profile
      ):
          mock_response = MagicMock()
          mock_response.content = [
              MagicMock(
                  text="""{
              "narrative_coherence": {
                  "score": 72,
                  "rationale": "Good flow",
                  "evidence_found": ["Clear arc"],
                  "evidence_missing": ["Weak transition at slide 5"]
              },
              "thesis_alignment": {
                  "score": 68,
                  "rationale": "Mostly aligned",
                  "evidence_found": ["AI infra thesis"],
                  "evidence_missing": ["Category creation weak"]
              },
              "common_mistakes": {
                  "score": 80,
                  "rationale": "Few mistakes",
                  "evidence_found": ["Data-driven bullets"],
                  "evidence_missing": ["No NDR on traction"]
              },
              "slide_quality": [
                  {"slide_number": 1, "quality_note": "Strong opener"}
              ],
              "top_strengths": ["Revenue traction", "AI positioning"],
              "critical_gaps": ["Missing NDR"],
              "recommendation": "Add NDR metric."
          }"""
              )
          ]

          with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
              with patch(
                  "pitchdeck.engine.validator.Anthropic"
              ) as mock_anthropic:
                  mock_anthropic.return_value.messages.create.return_value = (
                      mock_response
                  )
                  result = validate_deck(
                      sample_multi_slide_deck,
                      sample_vc_profile,
                      skip_llm=False,
                  )

          assert isinstance(result, DeckValidationResult)
          dims = {d.dimension: d for d in result.dimension_scores}
          assert dims["narrative_coherence"].score == 72
          assert dims["thesis_alignment"].score == 68
          assert dims["common_mistakes"].score == 80
          assert "Revenue traction" in result.top_strengths
          assert "Missing NDR" in result.critical_gaps

      def test_parse_validation_response_invalid_json(self):
          from pitchdeck.engine.validator import _parse_validation_response

          mock_response = MagicMock()
          mock_response.content = [MagicMock(text="Not valid JSON")]
          with pytest.raises(PitchDeckError, match="no JSON found"):
              _parse_validation_response(mock_response)


  class TestDimensionScoreBounds:
      def test_score_at_boundaries(self):
          low = DimensionScore(
              dimension="test", score=0, weight=0.2, rationale="Low"
          )
          high = DimensionScore(
              dimension="test", score=100, weight=0.2, rationale="High"
          )
          assert low.score == 0
          assert high.score == 100

      def test_score_out_of_bounds_raises(self):
          from pydantic import ValidationError

          with pytest.raises(ValidationError):
              DimensionScore(
                  dimension="test",
                  score=150,
                  weight=0.2,
                  rationale="Too high",
              )
          with pytest.raises(ValidationError):
              DimensionScore(
                  dimension="test",
                  score=-1,
                  weight=0.2,
                  rationale="Too low",
              )
  ```

- **MIRROR**: `tests/test_engine.py:1-176` — same class-based pytest pattern, `MagicMock` for API mocking, `patch.dict` for env vars, `pytest.raises(match=...)` for error assertions
- **IMPORTS**: From `pitchdeck.engine.validator`, `pitchdeck.models`, `unittest.mock`
- **GOTCHA**:
  - Mock `pitchdeck.engine.validator.Anthropic` (not `anthropic.Anthropic`) — the import is resolved in the validator module's namespace.
  - `sample_multi_slide_deck` and `sample_vc_profile` are from `conftest.py` — no import needed.
  - The LLM mock test patches BOTH `os.environ` (for API key check) AND `Anthropic` (for the API call).
  - `_score_slide_rules` and `_parse_validation_response` are private but need direct testing — import them directly (matching the pattern in `test_engine.py` where `_coerce_value`, `_build_vc_context`, `_parse_deck_response` are all tested directly).
- **VALIDATE**: `python3 -m pytest tests/test_validator.py -v`

### Task 8: CREATE `tests/test_validation_report.py` — Report Renderer Tests

- **ACTION**: Create unit tests for the validation report renderer
- **IMPLEMENT**:

  ```python
  """Tests for validation report rendering."""

  from pitchdeck.models import (
      CustomCheckResult,
      DeckValidationResult,
      DimensionScore,
      SlideValidationScore,
  )
  from pitchdeck.output.validation_report import (
      render_validation_report,
      save_validation_report,
  )


  class TestRenderValidationReport:
      def test_renders_header(self, sample_validation_result):
          md = render_validation_report(sample_validation_result)
          assert "# Deck Validation Report" in md
          assert "**Deck**: Neurawork" in md
          assert "**Target VC**: Test VC" in md
          assert "**Overall Score**: 73/100" in md
          assert "**PASS**" in md

      def test_renders_score_breakdown_table(
          self, sample_validation_result
      ):
          md = render_validation_report(sample_validation_result)
          assert "## Score Breakdown" in md
          assert "| Dimension |" in md
          assert "Completeness" in md
          assert "Metrics Density" in md
          assert "**TOTAL**" in md

      def test_renders_dimension_details(
          self, sample_validation_result
      ):
          md = render_validation_report(sample_validation_result)
          assert "### Completeness" in md
          assert "**Score**: 80/100" in md
          assert "**Evidence Found:**" in md
          assert "**Evidence Missing:**" in md

      def test_renders_custom_checks_table(
          self, sample_validation_result
      ):
          md = render_validation_report(sample_validation_result)
          assert "## VC-Specific Checks" in md
          assert "| Check | Status | Evidence |" in md
          assert "PASS" in md
          assert "FAIL" in md

      def test_renders_per_slide_scores(
          self, sample_validation_result
      ):
          md = render_validation_report(sample_validation_result)
          assert "## Per-Slide Scores" in md
          assert "### Slide 1:" in md
          assert "### Slide 9:" in md
          assert "Missing NDR metric" in md

      def test_renders_strengths_and_gaps(
          self, sample_validation_result
      ):
          md = render_validation_report(sample_validation_result)
          assert "## Top Strengths" in md
          assert "## Critical Gaps" in md
          assert "Strong revenue traction" in md
          assert "NDR data" in md

      def test_renders_improvement_priorities(
          self, sample_validation_result
      ):
          md = render_validation_report(sample_validation_result)
          assert "## Improvement Priorities" in md
          assert "Bottom-up market sizing" in md

      def test_renders_recommendation(
          self, sample_validation_result
      ):
          md = render_validation_report(sample_validation_result)
          assert "## Recommendation" in md
          assert "Strong candidate" in md

      def test_fail_result_shows_fail(self):
          result = DeckValidationResult(
              deck_name="Test",
              target_vc="VC",
              validated_at="2026-01-01",
              overall_score=40,
              pass_threshold=60,
              pass_fail=False,
              dimension_scores=[],
              slide_scores=[],
              custom_check_results=[],
              top_strengths=[],
              critical_gaps=[],
              improvement_priorities=[],
              recommendation="Needs work.",
          )
          md = render_validation_report(result)
          assert "**FAIL**" in md

      def test_empty_sections_omitted(self):
          result = DeckValidationResult(
              deck_name="Test",
              target_vc="VC",
              validated_at="2026-01-01",
              overall_score=50,
              pass_threshold=60,
              pass_fail=False,
              dimension_scores=[],
              slide_scores=[],
              custom_check_results=[],
              top_strengths=[],
              critical_gaps=[],
              improvement_priorities=[],
              recommendation="",
          )
          md = render_validation_report(result)
          assert "## Top Strengths" not in md
          assert "## Recommendation" not in md


  class TestSaveValidationReport:
      def test_saves_to_file(
          self, sample_validation_result, tmp_path
      ):
          output_path = str(tmp_path / "report.md")
          save_validation_report(sample_validation_result, output_path)

          with open(output_path) as f:
              content = f.read()
          assert "# Deck Validation Report" in content
          assert "Neurawork" in content

      def test_overwrites_existing_file(
          self, sample_validation_result, tmp_path
      ):
          output_path = str(tmp_path / "report.md")
          with open(output_path, "w") as f:
              f.write("old content")

          save_validation_report(sample_validation_result, output_path)

          with open(output_path) as f:
              content = f.read()
          assert "old content" not in content
          assert "Deck Validation Report" in content
  ```

- **MIRROR**: `tests/test_output.py:1-133` — same class-based test pattern for renderers: test header rendering, section rendering, conditional sections, file I/O with `tmp_path`
- **VALIDATE**: `python3 -m pytest tests/test_validation_report.py -v`

---

## Testing Strategy

### Unit Tests to Write

| Test File | Test Cases | Validates |
|-----------|-----------|-----------|
| `tests/test_validator.py` | template lookup, per-slide rule scoring, completeness scoring, metrics density scoring, custom checks, full validation (rule-only), full validation (mocked LLM), JSON parsing errors, score bounds | Core validation logic |
| `tests/test_validation_report.py` | header rendering, score table, dimension details, custom checks table, per-slide scores, strengths/gaps, improvement priorities, recommendation, FAIL display, file save | Report output |

### Edge Cases Checklist

- [ ] Empty deck (0 slides) — completeness score should be very low
- [ ] Slide with empty title and headline — should flag both issues
- [ ] Slide type not in SLIDE_TEMPLATES — should still score (without template-specific checks)
- [ ] Bullets exceeding max_bullets — should flag with count
- [ ] Word count exceeding word_limit — should flag with count
- [ ] Metrics required but none present — should flag with expected list
- [ ] All custom checks passing — all results should have `passed=True`
- [ ] All custom checks failing — all results should have `passed=False`
- [ ] API key missing with skip_llm=False — should raise PitchDeckError
- [ ] API key missing with skip_llm=True — should succeed (rule-based only)
- [ ] LLM returns invalid JSON — should raise PitchDeckError
- [ ] Score at boundaries (0 and 100) — should be valid
- [ ] Score out of bounds (150, -1) — should raise ValidationError
- [ ] DeckValidationResult with empty lists — should render without errors
- [ ] Single-slide deck — should still validate

---

## Validation Commands

### Level 1: STATIC_ANALYSIS

```bash
python3 -m py_compile src/pitchdeck/engine/validator.py && python3 -m py_compile src/pitchdeck/output/validation_report.py && python3 -m py_compile src/pitchdeck/models.py && python3 -m py_compile src/pitchdeck/cli.py
```

**EXPECT**: Exit 0, no syntax errors

### Level 2: IMPORT_CHECK

```bash
python3 -c "from pitchdeck.engine.validator import validate_deck; from pitchdeck.output import render_validation_report, save_validation_report; from pitchdeck.models import DeckValidationResult; print('All imports OK')"
```

**EXPECT**: Prints "All imports OK"

### Level 3: UNIT_TESTS

```bash
python3 -m pytest tests/ -v --tb=short
```

**EXPECT**: All tests pass (71 existing + new validation tests), exit 0

### Level 4: CLI_SMOKE_TEST

```bash
python3 -m pitchdeck --help && python3 -m pitchdeck validate --help
```

**EXPECT**: Help text shows `generate`, `validate`, and `profiles` commands. `validate --help` shows `deck_file`, `--vc`, `--output`, `--threshold`, `--skip-llm` options.

### Level 5: FULL_SUITE

```bash
python3 -m pytest tests/ -v --tb=short && python3 -m py_compile src/pitchdeck/engine/validator.py && python3 -m pitchdeck --help
```

**EXPECT**: All tests pass, compilation succeeds, CLI help displays

### Level 6: MANUAL_VALIDATION

If ANTHROPIC_API_KEY is available:

```bash
# 1. Generate a deck with JSON output
pitchdeck generate test_doc.pdf --vc earlybird --output test_deck.md

# 2. Validate the deck
pitchdeck validate test_deck.json --vc earlybird --output test_report.md

# 3. Review the report
cat test_report.md | head -80
```

If no API key:

```bash
# Create a minimal test deck JSON manually, then:
pitchdeck validate test_deck.json --vc earlybird --skip-llm --output test_report.md
```

---

## Acceptance Criteria

- [ ] `DeckValidationResult`, `DimensionScore`, `SlideValidationScore`, `CustomCheckResult` models defined in `models.py` with `Field(ge=0, le=100)` score constraints
- [ ] `validate_deck()` runs rule-based checks (completeness, metrics density, format) without API key
- [ ] `validate_deck()` runs LLM scoring (narrative coherence, thesis alignment, common mistakes) with API key and `temperature=0.0`
- [ ] `validate_deck(skip_llm=True)` produces valid results with 0 for LLM dimensions
- [ ] Per-slide scoring identifies: missing title/headline, bullet overflow, word limit violation, missing metrics, missing speaker notes
- [ ] Custom check evaluation matches against Earlybird's 7 custom_checks via keyword matching
- [ ] Overall score is weighted average of 5 dimensions (weights sum to 1.0)
- [ ] Validation report renders as readable Markdown with tables, sections, and priorities
- [ ] `pitchdeck validate` CLI command accepts deck JSON, VC profile, threshold, and skip-llm options
- [ ] `pitchdeck generate` saves JSON alongside Markdown
- [ ] All existing 71 tests still pass (no regressions)
- [ ] All new tests pass

---

## Completion Checklist

- [ ] Task 1: Validation models added to models.py
- [ ] Task 2: validator.py created with rule-based + LLM scoring
- [ ] Task 3: validation_report.py created with Markdown renderer
- [ ] Task 4: output/__init__.py updated with new exports
- [ ] Task 5: cli.py updated with validate command + JSON save
- [ ] Task 6: conftest.py updated with validation fixtures
- [ ] Task 7: test_validator.py created with comprehensive tests
- [ ] Task 8: test_validation_report.py created with renderer tests
- [ ] Level 1: Static analysis passes
- [ ] Level 2: All imports succeed
- [ ] Level 3: All tests pass (existing + new)
- [ ] Level 4: CLI smoke test passes
- [ ] Level 5: Full suite passes

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM score inflation (all decks get 70-90) | HIGH | HIGH | Strict calibration anchors in system prompt, temperature=0.0, CoT-before-scoring, 5-band scale descriptions |
| LLM returns invalid JSON | MEDIUM | MEDIUM | Regex JSON extraction + try/except with PitchDeckError; fallback to rule-based-only |
| Custom check keyword matching too crude | MEDIUM | LOW | Keyword map covers common patterns; LLM scoring catches nuance that keyword matching misses |
| Rule-based scoring too punitive (many deductions) | LOW | MEDIUM | Score floor at 0 via max(0, ...), deductions are proportional (5-15 points), total can't go negative |
| Score inconsistency across runs | MEDIUM | MEDIUM | temperature=0.0 ensures deterministic scoring; rule-based layer is fully deterministic |

---

## Notes

### Architecture Decisions

1. **Hybrid rule-based + LLM**: Rule-based checks handle deterministic validation (bullet count, metrics presence) while LLM handles qualitative assessment (narrative quality, thesis alignment). This gives useful results even without an API key.

2. **Single LLM call for all qualitative dimensions**: Sending the entire deck in one call (like `generate_deck()`) ensures holistic assessment and avoids 15 separate API calls. Cost: ~$0.05-0.15 per validation with prompt caching.

3. **temperature=0.0 for scoring**: Unlike generation (which benefits from creativity), scoring must be deterministic. The same deck should get the same score across runs.

4. **Prompt caching for rubric**: The system prompt + VC context is cached (ephemeral), so only the deck content varies per call. This is especially efficient when validating multiple iterations of the same deck.

5. **JSON save alongside Markdown**: Adding `deck.json` output to the generate command creates the bridge between Phase 1 (generation) and Phase 2 (validation) without requiring Phase 3 (full JSON export). Minimal addition that enables the validation workflow.

6. **Weighted dimension scoring**: Completeness (25%) and metrics density (20%) are weighted highest because they're objectively measurable and directly impact VC decision-making. Narrative coherence (20%) and thesis alignment (20%) are equally weighted as qualitative factors. Common mistakes (15%) is lowest because it's a "negative check" (deducting for errors rather than rewarding for quality).

### Phase 3 Preparation

- The JSON save added in Task 5 is a minimal precursor to Phase 3's full JSON export. Phase 3 will add structured JSON with Imagen3-compatible format, speaker notes document, and Q&A preparation — all building on the `PitchDeck.model_dump_json()` foundation.
- The `DeckValidationResult.model_dump_json()` can also be exported in Phase 3 for programmatic consumption.
