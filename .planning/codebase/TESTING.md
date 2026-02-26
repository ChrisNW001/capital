# Testing Patterns

**Analysis Date:** 2026-02-26

## Test Framework

**Runner:**
- `pytest` 8.0+ (configured in `pyproject.toml`)
- Config: `pytest.ini` section in `pyproject.toml`
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  pythonpath = ["src"]
  ```

**Assertion Library:**
- Built-in pytest assertions (no third-party assertion library)
- Standard `assert` statements with descriptive messages

**Run Commands:**
```bash
pytest                          # Run all tests
pytest tests/test_models.py     # Run single test file
pytest -k "test_creates"        # Run tests matching pattern
pytest --cov=src/pitchdeck      # Run with coverage report
pytest -v                       # Verbose output
pytest -x                       # Stop on first failure
```

## Test File Organization

**Location:**
- Test files are in separate `tests/` directory at project root (not co-located with source)
- Structure: `tests/test_<module>.py` mirrors `src/pitchdeck/<module>.py`
- Example mapping:
  - `src/pitchdeck/models.py` → `tests/test_models.py`
  - `src/pitchdeck/engine/validator.py` → `tests/test_validator.py`
  - `src/pitchdeck/cli.py` → `tests/test_cli_validate.py`, `tests/test_cli_generate.py` (split by command)

**Naming:**
- Files: `test_<feature>.py`
- Test classes: `Test<Feature>` (PascalCase)
- Test methods: `test_<specific_behavior>` (snake_case, verb-first)

**Structure:**
```
tests/
├── conftest.py                 # Shared fixtures
├── test_models.py              # Pydantic model tests
├── test_engine.py              # Engine component tests
├── test_validator.py           # Validation engine tests
├── test_cli_validate.py        # validate command tests
├── test_cli_generate.py        # generate command tests
├── test_output.py              # Markdown/report rendering
├── test_profiles.py            # Profile loading
├── test_parsers.py             # PDF/DOCX extraction
├── test_validation_report.py   # Report generation
└── __init__.py                 # (empty, marks as package)
```

## Test Structure

**Suite Organization:**

Class-based tests using pytest. Classes group related test methods.

```python
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
```

**Patterns:**
- No explicit setup/teardown methods (fixtures used instead)
- Each test method is independent (can run in any order)
- Assertions check behavior and state, not implementation

## Mocking

**Framework:** `unittest.mock` (built-in)

**Patterns:**

Mock the Anthropic API client to avoid real API calls:

```python
from unittest.mock import MagicMock, patch

@patch("pitchdeck.engine.narrative.Anthropic")
def test_generate_deck_success(self, mock_anthropic_class, sample_company, sample_vc_profile):
    # Create mock client and response
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"slides": [...]}')]
    mock_client.messages.create.return_value = mock_response

    # Call function under test
    deck = generate_deck(sample_company, sample_vc_profile, [])

    # Assertions
    assert deck.company_name == sample_company.name
    mock_client.messages.create.assert_called_once()
```

**Decorator Syntax:**
- Use `@patch("module.path.Class")` to patch at the point of use
- Order of decorator parameters (bottom-to-top): `@patch("B") @patch("A")` → `test_func(self, mock_a, mock_b)`

**What to Mock:**
- Anthropic API calls (all of them — see `test_engine.py`, `test_validator.py`)
- File I/O when testing logic (use `tmp_path` fixture instead for real files)
- External services (none in this project beyond Anthropic)

**What NOT to Mock:**
- Pydantic models — test with real instances
- Internal functions (test end-to-end behavior through public API)
- File system operations — use `tmp_path` fixture for real temporary files

## Fixtures and Factories

**Test Data:**

Shared fixtures defined in `conftest.py`. Commonly used fixtures:

```python
@pytest.fixture
def sample_company():
    """Fully populated CompanyProfile."""
    return CompanyProfile(
        name="Neurawork",
        product_name="NeuraPlox",
        one_liner="The AI Control Plane for European SMEs",
        founded_year=2024,
        employee_count=20,
        revenue_eur=2300000,
        revenue_type="revenue",
        growth_rate_yoy=None,
        customer_count=4,
        funding_stage="bootstrapped",
        raw_document_text="Sample document text for testing purposes.",
    )

@pytest.fixture
def sample_company_with_gaps():
    """CompanyProfile with many missing fields — for gap detection tests."""
    return CompanyProfile(
        name="",
        product_name="",
        one_liner="",
        founded_year=0,
        employee_count=0,
        revenue_eur=0,
        revenue_type="revenue",
        funding_stage="bootstrapped",
        raw_document_text="Some text",
    )

@pytest.fixture
def sample_multi_slide_deck():
    """Realistic 15-slide deck for validation testing."""
    slides = []
    slide_types = [
        "cover", "executive-summary", "problem", "why-now",
        "solution", "product", "market-sizing", "business-model",
        "traction", "go-to-market", "competitive-landscape",
        "team", "financials", "the-ask", "ai-architecture",
    ]
    for i, stype in enumerate(slide_types, 1):
        slides.append(SlideContent(...))
    return PitchDeck(
        company_name="Neurawork",
        target_vc="Test VC",
        generated_at="2026-02-19T12:00:00",
        slides=slides,
        narrative_arc="Hook > Tension > Resolution > Proof > Trust > Ask",
        gaps_identified=["NDR percentage missing"],
    )
```

**Location:**
- All fixtures in `tests/conftest.py` (shared across all test files)
- Fixtures are parameterized and reusable
- No factory classes (fixtures are the pattern)

**Fixture Usage in Tests:**
```python
def test_creates_valid_profile(self, sample_company):
    assert sample_company.name == "Neurawork"
    assert sample_company.revenue_eur == 2300000
```

## Coverage

**Requirements:** Not enforced (no minimum coverage threshold in config)

**View Coverage:**
```bash
pytest --cov=src/pitchdeck --cov-report=html
# Opens htmlcov/index.html in browser
```

**Current State:**
- `.coverage` added to `.gitignore` (see commit 671877c)
- Coverage reports are generated locally but not committed

## Test Types

**Unit Tests:**
- Scope: Individual functions and classes
- Approach: Test function behavior with isolated inputs; mock external dependencies
- Examples: `test_coerce_numeric_value()`, `test_missing_title_deducts()`, `test_detects_missing_fields()`
- Coverage: Models (`test_models.py`), engine functions (`test_engine.py`), validation rules (`test_validator.py`)

**Integration Tests:**
- Scope: Multiple components working together
- Approach: Test complete workflows (parsing → generation, validation → report)
- Examples: CLI commands (`test_cli_validate.py`, `test_cli_generate.py`), output rendering (`test_output.py`)
- API calls are still mocked to avoid real Anthropic costs

**E2E Tests:**
- Not used in this codebase
- Could be added for end-to-end workflows if integration with real Claude API is desired

## Common Patterns

**Testing Validation/Constraints:**

Pydantic model validation tests:
```python
def test_required_fields(self):
    with pytest.raises(ValidationError):
        CompanyProfile()

def test_score_field_bounds(self):
    with pytest.raises(ValidationError):
        DimensionScore(
            dimension="completeness",
            score=150,  # Out of bounds
            weight=0.5,
            rationale="Test"
        )
```

**Testing Error Handling:**

```python
def test_file_not_found_exits_1(self):
    result = runner.invoke(
        app, ["validate", "nonexistent.json", "--skip-llm"]
    )
    assert result.exit_code == 1
    assert "File not found" in result.output

def test_invalid_json_schema_exits_1(self, tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text('{"company_name": "X"}')
    result = runner.invoke(
        app, ["validate", str(bad_json), "--skip-llm"]
    )
    assert result.exit_code == 1
    assert "Invalid deck JSON schema" in result.output
```

**Async Testing:**
- Not used (synchronous Python codebase)

**CLI Testing:**

Use Typer's `CliRunner` to invoke commands:

```python
from typer.testing import CliRunner

runner = CliRunner()

def test_skip_llm_succeeds(self, sample_deck_json, tmp_path):
    report_path = tmp_path / "report.md"
    result = runner.invoke(app, [
        "validate", str(sample_deck_json),
        "--skip-llm",
        "--output", str(report_path),
    ])
    assert result.exit_code == 0
    assert "Overall Score" in result.output
    assert report_path.exists()
```

**Parameterized Tests:**

Not explicitly used in existing tests, but could use pytest parametrize:
```python
@pytest.mark.parametrize("value,expected", [
    ("5,000,000", 5000000.0),
    ("EUR 50000", 50000.0),
    ("115", 115.0),
])
def test_coerce_numeric_value(self, value, expected):
    assert _coerce_value("target_raise_eur", value) == expected
```

## Test Examples by Module

**Models (`test_models.py`):**
- Validates Pydantic fields and defaults
- Tests field constraints (score bounds, weights)
- Tests computed fields and validators

**Engine (`test_engine.py`):**
- Tests slide template loading and filtering
- Tests gap detection algorithm
- Tests value coercion for gap filling
- Narrative arc generation

**Validator (`test_validator.py`):**
- Tests rule-based slide scoring
- Tests dimension scoring (completeness, metrics density, etc.)
- Tests custom check evaluation
- Tests LLM response parsing (with mocked Claude API)

**CLI (`test_cli_validate.py`, `test_cli_generate.py`):**
- Tests file handling and error messages
- Tests API key requirements
- Tests output file creation
- Tests command-line option parsing

## Mock Pattern for Anthropic API

**Standard pattern for all Claude API tests:**

```python
@patch("pitchdeck.engine.validator.Anthropic")
def test_validate_with_llm(self, mock_anthropic_class, sample_deck, sample_vc_profile):
    # Setup mock
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client

    # Mock response with JSON content
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(text='{"dimension_scores": [...], "slide_scores": [...], ...}')
    ]
    mock_client.messages.create.return_value = mock_response

    # Call function
    result = validate_deck(sample_deck, sample_vc_profile, threshold=60, skip_llm=False)

    # Verify and assert
    mock_client.messages.create.assert_called_once()
    assert result.overall_score > 0
```

---

*Testing analysis: 2026-02-26*
