## ADDED Requirements

### Requirement: Module-level Anthropic client
The module SHALL initialize a single `anthropic.Anthropic()` client instance at module level, reused across all function calls.

#### Scenario: Client initialized on import
- **WHEN** `src.generator` is imported
- **THEN** a single `anthropic.Anthropic()` instance is available at module scope

---

### Requirement: Generate endpoint documentation
`generate_endpoint_doc(endpoint: APIEndpoint, model: str, stream: bool) -> GeneratedDoc` SHALL call the Anthropic API using prompts from `src.prompts` and return a `GeneratedDoc` with the generated markdown, token count, and model name.

#### Scenario: Non-streaming generation
- **WHEN** `generate_endpoint_doc` is called with `stream=False`
- **THEN** it calls `client.messages.create()` and returns a `GeneratedDoc` with `markdown`, `tokens_used` (input + output tokens), and `model`

#### Scenario: Streaming generation
- **WHEN** `generate_endpoint_doc` is called with `stream=True`
- **THEN** it uses `client.messages.stream()`, prints tokens to stdout as they arrive, and still returns a valid `GeneratedDoc` with correct token counts from `get_final_message()`

#### Scenario: endpoint_ref format
- **WHEN** a `GeneratedDoc` is returned
- **THEN** `endpoint_ref` is formatted as `"METHOD /path"` (e.g. `"GET /users/{id}"`)

---

### Requirement: Generate API overview
`generate_overview(spec: APISpec, model: str) -> str` SHALL call the Anthropic API using `prompts.build_overview_prompt(spec)` and return the generated overview as a plain string.

#### Scenario: Overview returned as string
- **WHEN** `generate_overview` is called with a valid `APISpec`
- **THEN** it returns a non-empty string containing the overview markdown

---

### Requirement: Full-run orchestration
`generate_full_docs(spec: APISpec, model: str, stream: bool) -> GenerationResult` SHALL call `generate_overview` and `generate_endpoint_doc` for each endpoint, accumulate tokens and cost, and return a `GenerationResult`.

#### Scenario: All endpoints processed
- **WHEN** `generate_full_docs` is called with a spec containing N endpoints
- **THEN** the returned `GenerationResult.docs` contains up to N `GeneratedDoc` entries and `total_tokens` equals the sum of all endpoint token counts plus the overview tokens

#### Scenario: Cost calculated
- **WHEN** `generate_full_docs` completes
- **THEN** `total_cost_usd` is computed via `utils.estimate_cost()` using the total token counts and model

#### Scenario: Progress printed
- **WHEN** `generate_full_docs` is running
- **THEN** each endpoint's start and completion is printed to stdout (e.g. `"Generating: GET /users/{id}"`)

---

### Requirement: Rate limit retry
The generator SHALL retry API calls that return a 429 (rate limit) response up to 3 times with exponential backoff (2s, 4s, 8s).

#### Scenario: Retry on 429
- **WHEN** the Anthropic API returns a rate limit error
- **THEN** the call is retried up to 3 times with delays of 2, 4, and 8 seconds before raising

---

### Requirement: Server error handling
The generator SHALL retry on 500+ server errors once, then skip the endpoint with a printed warning if it fails again.

#### Scenario: Skip endpoint after repeated 500
- **WHEN** the Anthropic API returns a 500+ error twice for the same endpoint
- **THEN** the endpoint is skipped, a warning is printed, and generation continues with remaining endpoints

---

### Requirement: Auth error handling
The generator SHALL immediately raise on a 401 authentication error with a clear message directing the user to check their API key.

#### Scenario: Auth error exits cleanly
- **WHEN** the Anthropic API returns a 401 error
- **THEN** an exception is raised with a message indicating the API key is invalid or missing
