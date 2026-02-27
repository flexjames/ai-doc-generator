## Context

`src/parser.py` is the first stage of the pipeline. It transforms raw OpenAPI 3.x spec files into validated Pydantic models that all downstream modules (generator, formatter, CLI) consume. Without it, the tool cannot process any input. The data models it must produce are already defined in `src/models.py`.

## Goals / Non-Goals

**Goals:**
- Load OpenAPI 3.x spec files in JSON and YAML formats
- Resolve local `$ref` pointers (`#/components/schemas/...`) into inline definitions
- Extract all GET/POST/PUT/PATCH/DELETE endpoints into `APIEndpoint` models
- Merge path-level parameters into each endpoint's parameter list
- Summarize request body and response schemas as human-readable strings
- Return a validated `APISpec` model; surface errors clearly without crashing

**Non-Goals:**
- OpenAPI 2.0 (Swagger) support
- Remote `$ref` resolution (external URLs or file paths)
- Full JSON Schema validation of the spec itself
- Handling `allOf`, `oneOf`, `anyOf` schema composition beyond simple summarization

## Decisions

**Use stdlib `json` + `PyYAML` for file loading (no OpenAPI SDK)**
An OpenAPI-specific library (e.g., `openapi-spec-validator`, `prance`) would add a heavy dependency and impose its own data structures. Since we only need to extract a subset of fields and already have Pydantic models as the target, parsing raw dicts is simpler and more controllable.

**Local-only `$ref` resolution with cycle detection**
Only `#/components/schemas/...` refs are in scope for the MVP. A recursive resolver with a `seen` set prevents infinite loops on circular schemas. Unresolvable refs are logged as warnings and left as-is rather than raising.

**Schema summarization as a flat string**
`_summarize_schema()` converts a JSON Schema dict into a human-readable string (e.g., `"{ id: string, name: string, active: boolean }"`). This string is what the LLM receives — a structured summary is more useful to the model than a raw JSON blob. Nested objects are summarized recursively up to a reasonable depth.

**Skip unsupported HTTP methods silently**
`OPTIONS`, `HEAD`, and `TRACE` are skipped without raising errors. Only the five methods in `HTTPMethod` are extracted. A debug-level log is emitted for skipped methods.

**Path-level parameter merging**
OpenAPI allows parameters to be defined at the path level (shared across all methods on that path). These are merged into each endpoint's parameter list, with operation-level parameters taking precedence on name+location conflicts.

## Risks / Trade-offs

- **Circular `$ref` schemas** → Mitigation: track visited refs in a set; break cycle and log warning
- **Deeply nested schemas produce long summaries** → Mitigation: cap recursion depth at 3 levels; truncate with `...` beyond that
- **Missing required fields in spec (e.g., no `info.title`)** → Mitigation: use empty string defaults for optional fields; `title` and `version` fall back to `"Unknown"` with a warning rather than crashing
- **YAML with anchors/aliases** → Mitigation: PyYAML handles these natively with the default `safe_load`

## Open Questions

*(none — all decisions are resolved based on PROJECT.md spec)*
