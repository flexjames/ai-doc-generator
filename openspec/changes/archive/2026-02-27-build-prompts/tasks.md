## 1. Implement src/prompts.py

- [x] 1.1 Create `src/prompts.py` with imports: `from src.models import APIEndpoint, APISpec`
- [x] 1.2 Define `SYSTEM_PROMPT` as a module-level string constant that instructs the LLM to act as a senior technical writer, output Markdown, use realistic domain-appropriate sample data (not "foo", "bar", "example"), and include: description, use cases, request example, response example, error scenarios, and tips
- [x] 1.3 Implement `build_endpoint_prompt(endpoint: APIEndpoint) -> str` — build a prompt string containing: HTTP method and path, operation ID and summary, description, all parameters (name, location, type, required), request body content type and schema summary (if present), all response status codes and descriptions, and a request for realistic examples and error handling guidance
- [x] 1.4 Implement `build_overview_prompt(spec: APISpec) -> str` — build a prompt string containing: API title and version, description (omit if None), base URL (omit if None), list of endpoint method+path pairs, and a request for an overview/introduction section

## 2. Implement tests/test_prompts.py

- [x] 2.1 Create `tests/test_prompts.py` with imports for `pytest` and all prompt exports from `src.prompts`, and model constructors from `src.models`
- [x] 2.2 Test `SYSTEM_PROMPT` is a non-empty string
- [x] 2.3 Test `SYSTEM_PROMPT` contains "Markdown" (case-insensitive)
- [x] 2.4 Test `SYSTEM_PROMPT` instructs realistic sample data (contains instruction against "foo", "bar", or "example" placeholders, or affirmative instruction to use realistic data)
- [x] 2.5 Test `SYSTEM_PROMPT` references "technical writer"
- [x] 2.6 Test `build_endpoint_prompt()` includes HTTP method and path
- [x] 2.7 Test `build_endpoint_prompt()` includes parameter name, location, type, and required status when parameters are present
- [x] 2.8 Test `build_endpoint_prompt()` includes request body content type and schema summary when `request_body` is present
- [x] 2.9 Test `build_endpoint_prompt()` does not raise and omits misleading content when `request_body` is `None`
- [x] 2.10 Test `build_endpoint_prompt()` includes all response status codes and descriptions
- [x] 2.11 Test `build_endpoint_prompt()` contains a request for examples
- [x] 2.12 Test `build_overview_prompt()` includes API title and version
- [x] 2.13 Test `build_overview_prompt()` includes endpoint count or list
- [x] 2.14 Test `build_overview_prompt()` does not raise and does not contain the literal string "None" when spec description is `None`
- [x] 2.15 Test `build_overview_prompt()` contains a request for overview or introduction

## 3. Verify

- [x] 3.1 Run `pytest tests/test_prompts.py -v` and confirm all tests pass
- [x] 3.2 Run `pytest tests/ -v` and confirm no regressions
