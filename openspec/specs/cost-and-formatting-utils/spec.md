## ADDED Requirements

### Requirement: PRICING table maps model IDs to per-million-token rates
The system SHALL define a module-level `PRICING` dict constant in `src/utils.py` mapping model ID strings to dicts with `"input"` and `"output"` keys representing USD cost per 1,000,000 tokens.

#### Scenario: PRICING contains known models
- **WHEN** `PRICING` is imported from `src.utils`
- **THEN** it SHALL be a non-empty `dict` containing entries for `"claude-sonnet-4-6"` and `"claude-haiku-4-5-20251001"`

#### Scenario: PRICING entries have valid rate keys
- **WHEN** any entry in `PRICING` is inspected
- **THEN** it SHALL have both `"input"` and `"output"` keys with positive `float` values

---

### Requirement: estimate_cost computes USD cost from token counts and model
The system SHALL provide an `estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float` function that looks up the model in `PRICING` and returns the total cost in USD using the formula `(input_tokens * input_rate + output_tokens * output_rate) / 1_000_000`.

#### Scenario: Cost is correct for a known model
- **WHEN** `estimate_cost()` is called with known token counts and a model in `PRICING`
- **THEN** it SHALL return a `float` equal to `(input_tokens * input_rate + output_tokens * output_rate) / 1_000_000`

#### Scenario: Unknown model raises ValueError
- **WHEN** `estimate_cost()` is called with a model string not present in `PRICING`
- **THEN** it SHALL raise a `ValueError` with a message identifying the unknown model

#### Scenario: Zero tokens returns zero cost
- **WHEN** `estimate_cost()` is called with `input_tokens=0` and `output_tokens=0`
- **THEN** it SHALL return `0.0`

---

### Requirement: format_cost renders a cost float as a dollar string
The system SHALL provide a `format_cost(cost: float) -> str` function that returns the cost formatted as `"$X.XXXX"` — a dollar sign followed by the value to exactly 4 decimal places, with no locale dependency.

#### Scenario: Non-zero cost formats correctly
- **WHEN** `format_cost(0.0042)` is called
- **THEN** it SHALL return `"$0.0042"`

#### Scenario: Zero cost formats correctly
- **WHEN** `format_cost(0.0)` is called
- **THEN** it SHALL return `"$0.0000"`

#### Scenario: Output always has dollar sign and 4 decimal places
- **WHEN** `format_cost()` is called with any float
- **THEN** the returned string SHALL start with `"$"` and have exactly 4 digits after the decimal point

---

### Requirement: sanitize_anchor converts heading text to a Markdown anchor slug
The system SHALL provide a `sanitize_anchor(text: str) -> str` function that lowercases the input, replaces spaces with `-`, and strips all characters that are not alphanumeric or `-`.

#### Scenario: Output is lowercased
- **WHEN** `sanitize_anchor()` is called with text containing uppercase characters
- **THEN** the returned string SHALL contain no uppercase characters

#### Scenario: Spaces are replaced with hyphens
- **WHEN** `sanitize_anchor("List Members")` is called
- **THEN** it SHALL return `"list-members"`

#### Scenario: Non-alphanumeric/non-hyphen characters are stripped
- **WHEN** `sanitize_anchor()` is called with text containing slashes, dots, or other punctuation
- **THEN** the returned string SHALL contain only lowercase alphanumeric characters and hyphens

#### Scenario: Empty string input does not raise
- **WHEN** `sanitize_anchor("")` is called
- **THEN** it SHALL return `""` without raising

---

### Requirement: create_progress_bar returns a CLI progress string
The system SHALL provide a `create_progress_bar(current: int, total: int) -> str` function that returns a string in the format `"[{current}/{total}] Generating..."`.

#### Scenario: Progress string matches expected format
- **WHEN** `create_progress_bar(3, 12)` is called
- **THEN** it SHALL return `"[3/12] Generating..."`
