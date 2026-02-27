## Context

`src/generator.py` is the LLM integration layer. It sits between the parsed `APISpec` (from `parser.py`) and the output formatters (`formatter.py`). It depends on `prompts.py` for all prompt text and `utils.py` for cost estimation. The Anthropic `anthropic` SDK is already in `requirements.txt`.

## Goals / Non-Goals

**Goals:**
- Generate per-endpoint documentation via the Anthropic API
- Generate an API overview section
- Orchestrate full-run generation across all endpoints with progress output
- Support streaming mode (print tokens to stdout as they arrive)
- Track token usage and compute cost per run
- Handle API errors gracefully with retry logic

**Non-Goals:**
- Output formatting or file writing (belongs in `formatter.py`)
- Prompt construction (belongs in `prompts.py`)
- Spec parsing (belongs in `parser.py`)
- CLI argument handling (belongs in `main.py`)

## Decisions

**Single module-level client instance**
Initialize `anthropic.Anthropic()` once at module level rather than per-call. This avoids repeated auth overhead and keeps the pattern consistent with the project convention.

**`generate_full_docs` as the primary orchestrator**
Callers (i.e. `main.py`) only need to call one function. It internally calls `generate_overview` and `generate_endpoint_doc` per endpoint, accumulates cost and tokens, and returns a `GenerationResult`. This keeps `main.py` thin.

**Streaming via `client.messages.stream()` context manager**
When `stream=True`, tokens are printed to stdout as they arrive. The final `usage` block is read from the stream's `get_final_message()` to get token counts. Non-streaming uses `client.messages.create()` directly. Both paths produce the same `GeneratedDoc` return value.

**Retry with exponential backoff for transient errors**
- Rate limit (429): retry up to 3× with delays of 2s, 4s, 8s
- Server error (500+): retry once, then skip endpoint with a warning
- Auth error (401): print message and raise immediately (non-retryable)
This avoids silent failures while not blocking the whole run on a single bad endpoint.

**`endpoint_ref` format: `"METHOD /path"`**
e.g. `"GET /users/{id}"`. Matches the display format used in prompts and formatter output.

## Risks / Trade-offs

- **Real API calls in tests** → Mitigation: mock the `anthropic` client at module level using `unittest.mock.patch`
- **Streaming token counts** → The stream context manager's `get_final_message()` provides usage; if this API changes, token tracking breaks. Mitigation: pin SDK version in `requirements.txt`.
- **Skipping endpoints on 500 errors** → A partial `GenerationResult` is returned. Callers should check `len(result.docs)` vs the number of endpoints if completeness matters.
