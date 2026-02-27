## 1. Create test fixtures

- [x] 1.1 Create `tests/fixtures/` directory
- [x] 1.2 Create `tests/fixtures/minimal-spec.json` — minimal valid OpenAPI 3.x spec with one GET endpoint, no `$ref`s, and all optional fields omitted
- [x] 1.3 Create `tests/fixtures/rewards-api-spec.json` — rewards platform spec with 6 endpoints (GET/POST members, GET transactions, POST earn/redeem, GET rewards), realistic schemas, and `$ref` usage in `components/schemas`

## 2. Implement src/parser.py

- [x] 2.1 Create `src/parser.py` with imports: `json`, `yaml`, `logging`, `from src.models import *`
- [x] 2.2 Implement `_load_file(file_path: str) -> dict` — detect `.json` / `.yaml` / `.yml` extension, load accordingly, raise `FileNotFoundError` if path missing, raise `ValueError` with path on parse failure
- [x] 2.3 Implement `_resolve_refs(spec: dict) -> dict` — recursively walk the dict and replace any `{"$ref": "#/components/schemas/X"}` with the inlined schema; track visited refs in a set to break cycles; log warning on circular or unresolvable ref
- [x] 2.4 Implement `_summarize_schema(schema: dict, depth: int = 0) -> str` — return `""` for None/empty; return `"array of <items_summary>"` for array type; return `"{ field: type, ... }"` for object type up to depth 3, truncating deeper nesting with `...`; return the raw `type` string for scalar types
- [x] 2.5 Implement `_extract_parameters(params: list) -> list[Parameter]` — map each param dict to a `Parameter` model using `name`, `in` → `location`, `required`, `schema.type` → `schema_type`, `description`
- [x] 2.6 Implement `_extract_request_body(body: dict) -> RequestBody | None` — return `None` if `body` is None; extract first content type key and its schema; call `_summarize_schema()` for `schema_summary`
- [x] 2.7 Implement `_extract_responses(responses: dict) -> list[ResponseInfo]` — iterate status code keys; extract `description` and optionally summarize the response schema via `_summarize_schema()`
- [x] 2.8 Implement `_extract_endpoints(spec: dict) -> list[APIEndpoint]` — iterate `spec["paths"]`; for each path collect path-level parameters; for each method key check if it is in `HTTPMethod` (skip others); merge path-level params with operation-level params (operation takes precedence by name+location); call `_extract_parameters`, `_extract_request_body`, `_extract_responses`; build and append `APIEndpoint`
- [x] 2.9 Implement `parse_spec(file_path: str) -> APISpec` — call `_load_file`, `_resolve_refs`, `_extract_endpoints`; read `info.title` / `info.version` with `"Unknown"` fallback and warning; read `info.description` and `servers[0].url` as `base_url` (both optional); return `APISpec`

## 3. Implement tests/test_parser.py

- [x] 3.1 Create `tests/test_parser.py` with imports for `pytest`, `json`, `pathlib.Path`, all parser functions, and models
- [x] 3.2 Test `parse_spec()` with `minimal-spec.json` — asserts `APISpec` returned, correct title/version, one endpoint extracted
- [x] 3.3 Test `parse_spec()` with `rewards-api-spec.json` — asserts 6 endpoints, correct HTTP methods, at least one endpoint has parameters and a request body
- [x] 3.4 Test `parse_spec()` with a `.yaml` file — load a YAML version of the minimal spec (write inline or from fixture), assert correct result
- [x] 3.5 Test `parse_spec()` with a missing file — assert `FileNotFoundError` raised
- [x] 3.6 Test `parse_spec()` with malformed JSON — assert `ValueError` raised
- [x] 3.7 Test `parse_spec()` with a spec that has no `paths` key — assert `APISpec` returned with empty `endpoints` list
- [x] 3.8 Test `_resolve_refs()` — build a dict with a `$ref` pointing to `components.schemas`, call `_resolve_refs`, assert the ref is replaced with inline schema
- [x] 3.9 Test `_resolve_refs()` with a circular ref — assert no infinite loop, result is returned (may be partial)
- [x] 3.10 Test `_extract_endpoints()` skips unsupported methods — include `options` and `head` in a path dict, assert they do not appear in the output list
- [x] 3.11 Test path-level parameter merging — define a path-level param and an operation-level param with the same name/location; assert only the operation-level version appears in the endpoint
- [x] 3.12 Test `_summarize_schema()` with a flat object — assert `"{ id: string, name: string }"` style output
- [x] 3.13 Test `_summarize_schema()` with an array schema — assert output contains `"array of"`
- [x] 3.14 Test `_summarize_schema()` with `None` — assert returns `""`
- [x] 3.15 Test endpoint with no `summary` or `description` — assert `APIEndpoint.summary is None` and `APIEndpoint.description is None`
- [x] 3.16 Test endpoint with no `requestBody` — assert `APIEndpoint.request_body is None`
- [x] 3.17 Test response with no `content` (e.g. 204) — assert `ResponseInfo.schema_summary is None`

## 4. Verify

- [x] 4.1 Run `pytest tests/test_parser.py -v` and confirm all tests pass
- [x] 4.2 Run `pytest tests/ -v` and confirm no regressions in `test_models.py`
