## 1. Core Implementation

- [x] 1.1 Create `src/generator.py` with module-level `anthropic.Anthropic()` client instance
- [x] 1.2 Implement `generate_endpoint_doc(endpoint, model, stream)` — non-streaming path using `client.messages.create()`
- [x] 1.3 Implement streaming path in `generate_endpoint_doc` using `client.messages.stream()` context manager, printing tokens to stdout and reading token counts from `get_final_message()`
- [x] 1.4 Implement `generate_overview(spec, model)` using `prompts.build_overview_prompt(spec)`
- [x] 1.5 Implement `generate_full_docs(spec, model, stream)` — orchestrates overview + per-endpoint generation, accumulates tokens, computes cost via `utils.estimate_cost()`, prints progress, returns `GenerationResult`

## 2. Error Handling

- [x] 2.1 Add retry logic for rate limit errors (429): up to 3 retries with 2s, 4s, 8s backoff
- [x] 2.2 Add retry-once logic for server errors (500+): skip endpoint with printed warning on second failure
- [x] 2.3 Add immediate raise for auth errors (401) with a clear message about the API key

## 3. Tests

- [x] 3.1 Create `tests/test_generator.py` with fixtures that mock `anthropic.Anthropic` at module level
- [x] 3.2 Test `generate_endpoint_doc` non-streaming: verify `GeneratedDoc` fields (endpoint_ref format, tokens_used, model, markdown)
- [x] 3.3 Test `generate_endpoint_doc` streaming: verify tokens printed and correct `GeneratedDoc` returned
- [x] 3.4 Test `generate_overview`: verify returns non-empty string
- [x] 3.5 Test `generate_full_docs`: verify `GenerationResult` has correct doc count, total_tokens, and total_cost_usd
- [x] 3.6 Test rate limit retry: mock 429 then success, assert retried correct number of times
- [x] 3.7 Test server error skip: mock 500 twice, assert endpoint skipped and warning printed
- [x] 3.8 Test auth error: mock 401, assert exception raised with key message

## 4. Verification

- [x] 4.1 Run `pytest tests/ -v` and confirm all tests pass including new `test_generator.py`
