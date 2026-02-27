## Why

The generator module needs prompt templates to instruct the LLM, but no prompt infrastructure exists yet. `src/prompts.py` must be built before `src/generator.py` can be implemented, as it is the single source of truth for all LLM prompt text in the project.

## What Changes

- Introduce `src/prompts.py` with the system prompt, endpoint documentation prompt builder, and API overview prompt builder
- Introduce `tests/test_prompts.py` covering prompt construction and content correctness

## Capabilities

### New Capabilities

- `prompt-templates`: Define and construct all LLM prompt templates used to generate API documentation, including the system prompt, per-endpoint prompt, and API overview prompt

### Modified Capabilities

*(none)*

## Impact

- New file: `src/prompts.py`
- New file: `tests/test_prompts.py`
- No changes to existing modules
- Unblocks `src/generator.py`
