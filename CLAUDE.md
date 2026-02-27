# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (use a virtual environment)
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run a single test file
pytest tests/test_models.py -v

# Run a single test class or method
pytest tests/test_models.py::TestHTTPMethod -v
pytest tests/test_models.py::TestHTTPMethod::test_members_exist -v

# Run the CLI (once main.py exists)
python -m src.main specs/sample-rewards-api.json
python -m src.main specs/sample-rewards-api.json --stream --format html -o output/docs.html
```

## Architecture

This is a CLI tool that reads an OpenAPI/Swagger spec and uses the Anthropic Claude API to generate developer-friendly Markdown documentation.

**Pipeline:**
```
CLI (src/main.py)
  → parser.py        # Loads JSON/YAML spec → APISpec model
  → generator.py     # Calls Anthropic API per endpoint → GenerationResult
  → formatter.py     # Assembles full Markdown/HTML document
  → output file
```

**Key design rules:**
- All prompt text lives exclusively in `src/prompts.py` — no prompt strings in other modules
- `src/models.py` defines Pydantic v2 models used across all modules as the shared data contract
- `src/utils.py` holds cost estimation and token counting helpers; pricing table lives there
- `src/generator.py` initializes the `anthropic.Anthropic()` client once at module level

**Data flow through models:**
`APISpec` (parsed from file) → `APIEndpoint` list → `GeneratedDoc` per endpoint → `GenerationResult` (full run summary)

## Security

Never print or display environment variables, even partially. This includes `ANTHROPIC_API_KEY` and any other values loaded from `.env`.

## Environment

Requires a `.env` file with:
```
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=claude-sonnet-4-6        # optional, default shown
LOG_LEVEL=INFO                          # optional
```

## Current State

Only `src/models.py` and `tests/test_models.py` are implemented. `PROJECT.md` contains the full specification for all remaining modules (`parser.py`, `generator.py`, `formatter.py`, `prompts.py`, `utils.py`, `main.py`) including function signatures, behavior details, and edge cases. Read `PROJECT.md` before implementing any module.

## Claude Model IDs

Use these when referencing models in code or docs:
- Sonnet 4.6: `claude-sonnet-4-6`
- Haiku 4.5: `claude-haiku-4-5-20251001`
