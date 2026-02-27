## 1. Implement src/utils.py

- [x] 1.1 Create `src/utils.py` with no project imports and no external dependencies
- [x] 1.2 Define `PRICING` as a module-level dict constant:
  ```python
  PRICING = {
      "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
      "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
  }
  # costs per 1,000,000 tokens
  ```
- [x] 1.3 Implement `estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float` — look up model in `PRICING`, raise `ValueError` for unknown models, compute `(input_tokens * input_rate + output_tokens * output_rate) / 1_000_000` and return as `float`
- [x] 1.4 Implement `format_cost(cost: float) -> str` — return `f"${cost:.4f}"` (always 4 decimal places, dollar sign prefix, no locale dependency)
- [x] 1.5 Implement `sanitize_anchor(text: str) -> str` — lowercase the text, replace spaces with `-`, strip all characters that are not alphanumeric or `-`, and return the result
- [x] 1.6 Implement `create_progress_bar(current: int, total: int) -> str` — return `f"[{current}/{total}] Generating..."`

## 2. Implement tests/test_utils.py

- [x] 2.1 Create `tests/test_utils.py` with imports for `pytest` and all exports from `src.utils`
- [x] 2.2 Test `PRICING` is a non-empty dict and contains `"claude-sonnet-4-6"` and `"claude-haiku-4-5-20251001"`
- [x] 2.3 Test `PRICING` entries each have `"input"` and `"output"` keys with positive float values
- [x] 2.4 Test `estimate_cost()` returns correct float for `claude-sonnet-4-6` with known token counts (e.g. 1000 input + 500 output = `(1000*3.00 + 500*15.00) / 1_000_000 = 0.0105`)
- [x] 2.5 Test `estimate_cost()` returns correct float for `claude-haiku-4-5-20251001`
- [x] 2.6 Test `estimate_cost()` raises `ValueError` for an unknown model string
- [x] 2.7 Test `estimate_cost()` returns `0.0` when both token counts are `0`
- [x] 2.8 Test `format_cost()` returns `"$0.0042"` for input `0.0042`
- [x] 2.9 Test `format_cost()` returns `"$0.0000"` for input `0.0`
- [x] 2.10 Test `format_cost()` returns a string starting with `"$"` and containing exactly one `"."` with 4 decimal digits
- [x] 2.11 Test `sanitize_anchor()` lowercases input (e.g. `"GET /Users"` → `"get-/users"` → final anchor contains no uppercase)
- [x] 2.12 Test `sanitize_anchor()` replaces spaces with `-` (e.g. `"List Members"` → `"list-members"`)
- [x] 2.13 Test `sanitize_anchor()` strips non-alphanumeric/hyphen characters (e.g. `"POST /api/v1/members"` → `"post-apiv1members"` with slashes removed)
- [x] 2.14 Test `sanitize_anchor()` handles empty string input without raising
- [x] 2.15 Test `create_progress_bar()` returns `"[3/12] Generating..."` for inputs `3, 12`
- [x] 2.16 Test `create_progress_bar()` returns `"[1/1] Generating..."` for inputs `1, 1`

## 3. Verify

- [x] 3.1 Run `pytest tests/test_utils.py -v` and confirm all tests pass
- [x] 3.2 Run `pytest tests/ -v` and confirm no regressions across the full suite
