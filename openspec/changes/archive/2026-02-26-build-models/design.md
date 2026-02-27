## Context

`src/models.py` is the shared data contract for the entire application. Every other module imports from it: the parser produces `APISpec` objects, the generator consumes `APIEndpoint` objects and produces `GeneratedDoc` objects, the formatter consumes `GenerationResult`, and tests validate against all of them. This module must exist before any other module can be implemented.

Currently the file does not exist. All model definitions are specified in `PROJECT.md` and are treated as the authoritative source of truth for this change.

## Goals / Non-Goals

**Goals:**
- Implement all eight Pydantic v2 models exactly as specified in `PROJECT.md`
- Write `tests/test_models.py` covering valid construction, invalid data rejection, default values, and `model_dump()` output
- Ensure the module can be imported cleanly with no circular dependencies

**Non-Goals:**
- Implementing any other module (`parser.py`, `generator.py`, etc.)
- Adding models beyond what PROJECT.md specifies (no speculative additions)
- Database persistence or serialization to formats other than Python dicts

## Decisions

**Use `str, Enum` for `HTTPMethod`**
`HTTPMethod` inherits from both `str` and `Enum` so instances compare equal to plain strings (e.g., `HTTPMethod.GET == "GET"`). This simplifies parser code that reads raw strings from OpenAPI spec dicts without requiring explicit conversion at every call site. Alternative considered: plain `Enum` — rejected because it would require `.value` unwrapping throughout the codebase.

**Use `Field(default_factory=list)` for list fields**
Pydantic v2 requires `default_factory` for mutable defaults. Using `Field(default_factory=list)` is the idiomatic pattern and avoids the common Python gotcha of shared mutable default arguments. All list fields on `APIEndpoint` and `APISpec` use this pattern.

**`Optional[str]` fields default to `None`, not `""`**
Fields like `summary`, `description`, `operation_id`, and `base_url` are `Optional[str] = None`. Callers that need a safe string can use `endpoint.summary or ""`. This preserves the distinction between "field was absent in the spec" and "field was explicitly set to empty string" — important for the parser's edge-case handling.

**No cross-model validators in this module**
Business-rule validation (e.g., "a `GenerationResult` must have at least one doc") belongs in the modules that produce those objects, not in the models themselves. Keeping models as pure data containers makes them easier to construct in tests and reduces coupling.

## Risks / Trade-offs

- **All downstream modules depend on this** → Any field rename or type change here is a breaking change across the whole codebase. Mitigation: treat `models.py` as a stable contract; changes require updating PROJECT.md and this change simultaneously.
- **Pydantic v2 migration pitfalls** → v2 has breaking changes from v1 (`model_dump()` vs `dict()`, validators syntax, etc.). Mitigation: the convention is already set to use `model_dump()` everywhere; tests will catch v1-style usage.
