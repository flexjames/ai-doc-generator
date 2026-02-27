## Why

`src/generator.py` needs cost estimation and formatting helpers — no utility layer exists yet. `src/utils.py` must be built before `src/generator.py` so that token-based cost tracking is available from the start of generation work.

## What Changes

- Introduce `src/utils.py` with the pricing table constant and four helper functions: `estimate_cost`, `format_cost`, `sanitize_anchor`, and `create_progress_bar`
- Introduce `tests/test_utils.py` covering all functions including edge cases

## Capabilities

### New Capabilities

- `cost-and-formatting-utils`: Provide cost estimation from token counts and model name, human-readable cost formatting, Markdown anchor sanitization, and CLI progress display

### Modified Capabilities

*(none)*

## Impact

- New file: `src/utils.py`
- New file: `tests/test_utils.py`
- No changes to existing modules
- Unblocks `src/generator.py`
