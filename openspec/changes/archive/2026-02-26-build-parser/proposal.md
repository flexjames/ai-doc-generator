## Why

The data models are in place but the project has no way to read an OpenAPI spec file. `src/parser.py` is the first stage of the pipeline and is required before any other module (generator, formatter, CLI) can be wired together.

## What Changes

- Introduce `src/parser.py` with functions to load, resolve `$ref` pointers, and extract endpoints from OpenAPI 3.x JSON or YAML files into validated `APISpec` / `APIEndpoint` Pydantic models
- Introduce `tests/test_parser.py` covering all parsing logic, edge cases, and file-format support
- Add sample fixture files under `tests/fixtures/` (`minimal-spec.json`, `rewards-api-spec.json`) for use by the test suite

## Capabilities

### New Capabilities

- `spec-parser`: Parse OpenAPI 3.x spec files (JSON and YAML) into validated `APISpec` Pydantic models, including `$ref` resolution, parameter merging, schema summarization, and graceful handling of unsupported HTTP methods and missing optional fields

### Modified Capabilities

*(none)*

## Impact

- New file: `src/parser.py`
- New file: `tests/test_parser.py`
- New files: `tests/fixtures/minimal-spec.json`, `tests/fixtures/rewards-api-spec.json`
- No changes to existing `src/models.py` or other modules
- Unblocks `src/generator.py`, `src/main.py`, and end-to-end integration
