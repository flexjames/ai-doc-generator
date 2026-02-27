## Why

The CLI pipeline needs `src/generator.py` to bridge parsed API specs and the Anthropic API — without it, the tool cannot produce any documentation. This is the core LLM integration layer that all downstream modules (formatter, main) depend on.

## What Changes

- Add `src/generator.py` with three public functions for LLM-powered doc generation
- Add `tests/test_generator.py` with mocked Anthropic API tests
- The module initializes the Anthropic client once at module level and coordinates streaming, cost tracking, and error handling

## Capabilities

### New Capabilities
- `llm-doc-generation`: Anthropic API integration for generating per-endpoint documentation, API overviews, and full-run orchestration with streaming support, retry logic, and cost tracking

### Modified Capabilities

## Impact

- New file: `src/generator.py`
- New file: `tests/test_generator.py`
- Depends on: `src/models.py`, `src/prompts.py`, `src/utils.py`
- Required by: `src/formatter.py`, `src/main.py`
- External dependency: `anthropic` SDK (already in `requirements.txt`)
