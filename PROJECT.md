# PROJECT.md — AI-Powered API Documentation Generator

## Overview

A Python CLI tool that reads an OpenAPI/Swagger specification file (JSON or YAML) and uses the Anthropic Claude API to generate clear, developer-friendly API documentation in Markdown format.

## Goals

- Parse OpenAPI 3.x specification files and extract all endpoint definitions
- Use Claude to transform raw endpoint data into polished, practical documentation
- Output well-structured Markdown documentation with realistic examples
- Support streaming output, multiple output formats, and cost tracking
- Maintain clean separation between parsing logic, prompt management, and LLM calls

## Tech Stack

- **Language:** Python 3.12+
- **LLM Provider:** Anthropic Claude API (`anthropic` SDK)
- **Data Validation:** Pydantic v2
- **Config Management:** `python-dotenv`
- **YAML Support:** `PyYAML`
- **CLI Framework:** `argparse` (stdlib)
- **Testing:** `pytest`

## Project Structure

```
ai-doc-generator/
├── .env                      # Environment variables (ANTHROPIC_API_KEY)
├── .env.example              # Template for .env (committed to git)
├── .gitignore
├── requirements.txt
├── README.md
├── PROJECT.md                # This file
├── src/
│   ├── __init__.py
│   ├── main.py               # CLI entry point and argument parsing
│   ├── parser.py             # OpenAPI spec parsing and normalization
│   ├── generator.py          # LLM-powered documentation generation
│   ├── models.py             # Pydantic data models
│   ├── prompts.py            # All LLM prompt templates
│   ├── formatter.py          # Output formatting (Markdown, HTML)
│   └── utils.py              # Token counting, cost estimation, helpers
├── specs/
│   └── sample-rewards-api.json   # Sample OpenAPI spec for testing
├── output/                   # Generated documentation output directory
└── tests/
    ├── __init__.py
    ├── test_parser.py
    ├── test_models.py
    ├── test_generator.py
    └── fixtures/
        ├── minimal-spec.json
        └── rewards-api-spec.json
```

## Dependencies

```
anthropic>=0.40.0
python-dotenv>=1.0.0
pydantic>=2.0.0
PyYAML>=6.0
pytest>=8.0.0
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key (starts with `sk-ant-`) |
| `DEFAULT_MODEL` | No | Claude model to use. Default: `claude-sonnet-4-20250514` |
| `LOG_LEVEL` | No | Logging verbosity. Default: `INFO` |

## Data Models (`src/models.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class Parameter(BaseModel):
    name: str
    location: str               # "path", "query", "header", "cookie"
    required: bool = False
    schema_type: str = "string"
    description: Optional[str] = None

class RequestBody(BaseModel):
    content_type: str = "application/json"
    schema_summary: str         # Stringified or summarized JSON schema
    required: bool = True

class ResponseInfo(BaseModel):
    status_code: str
    description: str
    schema_summary: Optional[str] = None

class APIEndpoint(BaseModel):
    method: HTTPMethod
    path: str
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    parameters: list[Parameter] = Field(default_factory=list)
    request_body: Optional[RequestBody] = None
    responses: list[ResponseInfo] = Field(default_factory=list)

class APISpec(BaseModel):
    title: str
    version: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    endpoints: list[APIEndpoint]

class GeneratedDoc(BaseModel):
    endpoint_ref: str           # e.g. "GET /users/{id}"
    markdown: str
    tokens_used: int
    model: str

class GenerationResult(BaseModel):
    api_title: str
    api_version: str
    docs: list[GeneratedDoc]
    total_tokens: int
    total_cost_usd: float
    model: str
```

## Module Specifications

### `src/parser.py`

**Purpose:** Parse OpenAPI 3.x specs (JSON and YAML) into normalized `APISpec` models.

**Functions:**

| Function | Input | Output | Description |
|---|---|---|---|
| `parse_spec(file_path: str)` | Path to spec file | `APISpec` | Main entry point. Detects JSON/YAML, loads, and parses. |
| `_load_file(file_path: str)` | Path string | `dict` | Reads JSON or YAML based on file extension. |
| `_resolve_refs(spec: dict)` | Raw spec dict | `dict` | Resolves local `$ref` pointers (e.g., `#/components/schemas/User`). Does not handle remote refs. |
| `_extract_endpoints(spec: dict)` | Resolved spec dict | `list[APIEndpoint]` | Iterates `paths`, extracts each method into an `APIEndpoint`. |
| `_extract_parameters(params: list)` | Raw param list | `list[Parameter]` | Normalizes parameter objects into `Parameter` models. |
| `_extract_request_body(body: dict)` | Raw requestBody | `RequestBody` | Extracts and summarizes request body schema. |
| `_extract_responses(responses: dict)` | Raw responses dict | `list[ResponseInfo]` | Extracts status codes, descriptions, and schema summaries. |
| `_summarize_schema(schema: dict)` | JSON Schema object | `str` | Converts a JSON Schema into a readable string summary showing field names, types, and nesting. |

**Edge Cases to Handle:**
- Spec files with no `paths` key → return empty endpoint list with warning
- Methods like `options`, `head`, `trace` → skip, only process GET/POST/PUT/PATCH/DELETE
- Parameters defined at path level (shared across methods) → merge into each endpoint
- Missing `summary` or `description` fields → use empty string, don't error
- Circular `$ref` references → detect and break cycle, log warning

---

### `src/prompts.py`

**Purpose:** All LLM prompt templates in one place. No prompt text should exist in other modules.

**Constants/Functions:**

| Name | Type | Description |
|---|---|---|
| `SYSTEM_PROMPT` | `str` | System prompt defining the AI's role as a technical writer. |
| `build_endpoint_prompt(endpoint: APIEndpoint)` | `function` | Constructs the user message for documenting a single endpoint. |
| `build_overview_prompt(spec: APISpec)` | `function` | Constructs a prompt for generating the API overview/introduction section. |

**System Prompt Requirements:**
- Instruct the model to write as a senior technical writer
- Require inclusion of: description, use cases, request example with realistic data, response example, error scenarios, and tips
- Specify Markdown as the output format
- Instruct the model to use realistic sample data (not "foo", "bar", "example")
- Tell the model to tailor examples to the API's domain when possible

**Endpoint Prompt Requirements:**
- Include: HTTP method, path, summary, description, all parameters with types and descriptions, request body schema, response schemas
- Ask for realistic example values relevant to the endpoint's purpose
- Request common error codes and how to handle them

---

### `src/generator.py`

**Purpose:** Handles all interactions with the Anthropic API.

**Functions:**

| Function | Input | Output | Description |
|---|---|---|---|
| `generate_endpoint_doc(endpoint: APIEndpoint, model: str, stream: bool)` | Single endpoint + config | `GeneratedDoc` | Generates docs for one endpoint. Supports streaming to stdout. |
| `generate_overview(spec: APISpec, model: str)` | Full API spec | `str` | Generates an API overview/introduction section. |
| `generate_full_docs(spec: APISpec, model: str, stream: bool)` | Full spec + config | `GenerationResult` | Orchestrates generation for all endpoints. Prints progress. |

**Behavior:**
- Initialize `anthropic.Anthropic()` client once at module level
- When `stream=True`, print tokens to stdout as they arrive using `client.messages.stream()`
- Track `input_tokens` and `output_tokens` from each API response
- Pass token counts to `utils.estimate_cost()` for cost tracking
- Handle API errors gracefully: rate limits (retry with backoff), auth errors (clear message), network errors (retry once)
- Log each endpoint generation start/finish with timing

---

### `src/formatter.py`

**Purpose:** Assembles individual endpoint docs into a complete, well-structured output file.

**Functions:**

| Function | Input | Output | Description |
|---|---|---|---|
| `format_markdown(result: GenerationResult, overview: str)` | Generation result + overview | `str` | Assembles full Markdown document with table of contents, overview, and all endpoint docs. |
| `format_html(result: GenerationResult, overview: str)` | Generation result + overview | `str` | Wraps Markdown output in a styled HTML template. |

**Markdown Output Structure:**
```
# {API Title} — API Documentation
> Version {version}
> Generated by AI Doc Generator

## Overview
{LLM-generated overview}

## Table of Contents
- [GET /endpoint-1](#get-endpoint-1)
- [POST /endpoint-2](#post-endpoint-2)
...

## Endpoints

### GET /endpoint-1
{LLM-generated documentation}

---

### POST /endpoint-2
{LLM-generated documentation}

---

## Generation Stats
- Model: {model}
- Total tokens: {total_tokens}
- Estimated cost: ${cost}
- Generated at: {timestamp}
```

---

### `src/utils.py`

**Purpose:** Helper functions for cost estimation, token counting, and general utilities.

**Functions:**

| Function | Input | Output | Description |
|---|---|---|---|
| `estimate_cost(input_tokens: int, output_tokens: int, model: str)` | Token counts + model | `float` | Calculates estimated cost in USD based on model pricing. |
| `format_cost(cost: float)` | Float | `str` | Formats cost to human-readable string (e.g., "$0.0042"). |
| `sanitize_anchor(text: str)` | Heading text | `str` | Converts heading text to a valid Markdown anchor link. |
| `create_progress_bar(current: int, total: int)` | Counters | `str` | Returns a simple progress string like "[3/12] Generating..." |

**Pricing Table (update as needed):**

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| claude-sonnet-4-20250514 | $3.00 | $15.00 |
| claude-haiku-4-5-20251001 | $0.80 | $4.00 |

---

### `src/main.py`

**Purpose:** CLI entry point. Parses arguments, orchestrates the pipeline.

**CLI Interface:**

```
usage: main.py [-h] [-o OUTPUT] [-f {markdown,html}] [-m MODEL]
               [--stream] [--verbose] spec

Generate API documentation from OpenAPI specs using AI.

positional arguments:
  spec                    Path to OpenAPI spec file (JSON or YAML)

options:
  -h, --help              Show help message
  -o, --output OUTPUT     Output file path (default: output/docs.md)
  -f, --format {markdown,html}
                          Output format (default: markdown)
  -m, --model MODEL       Claude model to use (default: claude-sonnet-4-20250514)
  --stream                Stream LLM output to terminal in real-time
  --verbose               Enable verbose logging
```

**Execution Flow:**
1. Parse CLI arguments
2. Load environment variables from `.env`
3. Validate that `ANTHROPIC_API_KEY` is set
4. Call `parser.parse_spec()` to load and parse the OpenAPI spec
5. Print summary: API title, version, number of endpoints found
6. Call `generator.generate_overview()` for the intro section
7. Call `generator.generate_full_docs()` for all endpoints
8. Call `formatter.format_markdown()` or `formatter.format_html()`
9. Write output to file
10. Print summary: output path, total tokens, estimated cost, elapsed time

---

## Sample OpenAPI Spec (`specs/sample-rewards-api.json`)

Provide a sample spec with 4–6 endpoints modeling a rewards platform API:

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/members/{memberId}` | Retrieve a member's profile and points balance |
| POST | `/api/v1/members` | Enroll a new member in the rewards program |
| GET | `/api/v1/members/{memberId}/transactions` | List a member's point transactions with pagination |
| POST | `/api/v1/transactions/earn` | Award points to a member for a qualifying action |
| POST | `/api/v1/transactions/redeem` | Redeem points for a reward |
| GET | `/api/v1/rewards` | List available rewards in the catalog |

The sample spec should include realistic schemas with fields like `memberId`, `pointsBalance`, `tier`, `transactionType`, `rewardId`, `pointsCost`, etc.

---

## Testing (`tests/`)

### `test_parser.py`
- Test parsing a minimal valid OpenAPI spec → returns correct `APISpec`
- Test parsing spec with no paths → returns empty endpoint list
- Test `$ref` resolution for component schemas
- Test parameter extraction at path and operation level
- Test JSON and YAML file loading
- Test handling of missing optional fields (summary, description)

### `test_models.py`
- Test all Pydantic models accept valid data
- Test models reject invalid data with clear errors
- Test `model_dump()` produces expected dict structure
- Test default values are applied correctly

### `test_generator.py`
- Mock the Anthropic API client
- Test `generate_endpoint_doc` returns a valid `GeneratedDoc`
- Test token counting is extracted from the API response
- Test error handling for API failures (mock rate limit, auth error)
- Test streaming mode calls the correct API method

### Running Tests

```bash
pytest tests/ -v
```

---

## Error Handling Strategy

| Error | Behavior |
|---|---|
| Missing `ANTHROPIC_API_KEY` | Print clear error message and exit with code 1 |
| Spec file not found | Print error with the path attempted and exit |
| Invalid JSON/YAML in spec | Print parse error details and exit |
| Anthropic rate limit (429) | Retry up to 3 times with exponential backoff (2s, 4s, 8s) |
| Anthropic auth error (401) | Print message to check API key and exit |
| Anthropic server error (500+) | Retry once, then print error and skip endpoint |
| Invalid model response (unparseable) | Log warning, include raw response in output with a note |

---

## Stretch Goals (Post-MVP)

- [ ] **Batch mode:** Process multiple spec files in one run
- [ ] **Diff mode:** Compare two versions of a spec and document only the changes
- [ ] **Interactive mode:** Ask the user which endpoints to document
- [ ] **Custom prompts:** Allow users to provide their own prompt templates via a config file
- [ ] **Caching:** Cache LLM responses by endpoint hash to avoid re-generating unchanged endpoints
- [ ] **PDF output:** Generate PDF documentation using a Markdown-to-PDF converter
- [ ] **CI integration:** Output generation stats as JSON for pipeline consumption