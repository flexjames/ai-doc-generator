## Why

The project's data models are fully specified in PROJECT.md but don't yet exist as code. Without `src/models.py`, no other module (parser, generator, formatter) can be built, since they all depend on the Pydantic models as their shared data contract.

## What Changes

- Create `src/models.py` with all Pydantic v2 data models as defined in PROJECT.md
- Create `tests/test_models.py` with a full pytest test suite covering validation, defaults, and serialization

## Capabilities

### New Capabilities

- `data-models`: Pydantic v2 models representing the full data contract for the application — `HTTPMethod`, `Parameter`, `RequestBody`, `ResponseInfo`, `APIEndpoint`, `APISpec`, `GeneratedDoc`, and `GenerationResult`

### Modified Capabilities

_(none — no existing specs to modify)_

## Impact

- **New file**: `src/models.py`
- **New file**: `tests/test_models.py`
- All downstream modules (`parser.py`, `generator.py`, `formatter.py`, `utils.py`) will import from `src/models.py`; this change must be completed first
- No external dependencies added; Pydantic v2 is already in `requirements.txt`
