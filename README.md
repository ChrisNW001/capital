# Capital

Pitch deck generator and validator for B2B AI/SaaS companies targeting European VCs.

## Install

```bash
pip install -e ".[dev]"
```

Requires Python 3.10+. Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Commands

### Generate a pitch deck

```bash
pitchdeck generate company.pdf --vc earlybird
```

Parses the input document(s), fills any missing information gaps interactively, then generates a slide deck with Claude. Saves two files:

- `deck.md` — formatted Markdown presentation
- `deck.json` — structured JSON for the validation pipeline

Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--vc` | `earlybird` | VC profile name (filename without `.yaml`) |
| `--output` | `deck.md` | Markdown output path |
| `--json` | `<output>.json` | Override JSON output path |
| `--skip-gaps` | off | Skip interactive gap-filling prompts |

### Validate a deck

```bash
pitchdeck validate deck.json --vc earlybird
```

Scores the deck against VC-specific rubrics across five weighted dimensions. Rule-based checks run without an API key; LLM scoring requires `ANTHROPIC_API_KEY`. Saves a `validation_report.md` with per-slide scores, dimension breakdowns, and prioritized improvements.

Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--vc` | `earlybird` | VC profile to validate against |
| `--output` | `validation_report.md` | Report output path |
| `--threshold` | `60` | Pass/fail score threshold (0–100) |
| `--skip-llm` | off | Run rule-based checks only (no API key needed) |

Scoring dimensions:

| Dimension | Weight | Method |
|-----------|--------|--------|
| Completeness | 25% | Rule-based |
| Metrics density | 20% | Rule-based |
| Narrative coherence | 20% | LLM |
| Thesis alignment | 20% | LLM |
| Common mistakes | 15% | LLM |

### List available profiles

```bash
pitchdeck profiles
```

## VC Profiles

Profiles live in `profiles/<name>.yaml`. The included profile is `earlybird`. Each profile defines thesis points, custom validation checks, and deck preferences used by both the generator and validator.

## Typical workflow

```bash
# Generate deck and JSON
pitchdeck generate pitch_materials.pdf --vc earlybird

# Validate rule-based only (no API key needed)
pitchdeck validate deck.json --vc earlybird --skip-llm

# Full validation with LLM scoring
pitchdeck validate deck.json --vc earlybird
```
