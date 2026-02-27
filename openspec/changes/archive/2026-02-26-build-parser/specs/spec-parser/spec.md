## ADDED Requirements

### Requirement: Parser loads JSON spec files
The system SHALL load OpenAPI spec files with a `.json` extension using the stdlib `json` module and return the parsed dict.

#### Scenario: Valid JSON file loads successfully
- **WHEN** `parse_spec()` is called with a path to a valid `.json` OpenAPI spec file
- **THEN** it SHALL return a populated `APISpec` model with no errors

#### Scenario: Malformed JSON raises a clear error
- **WHEN** `parse_spec()` is called with a `.json` file containing invalid JSON
- **THEN** it SHALL raise a `ValueError` with a message describing the parse failure and the file path

---

### Requirement: Parser loads YAML spec files
The system SHALL load OpenAPI spec files with `.yaml` or `.yml` extensions using `PyYAML`'s `safe_load`.

#### Scenario: Valid YAML file loads successfully
- **WHEN** `parse_spec()` is called with a path to a valid `.yaml` OpenAPI spec file
- **THEN** it SHALL return a populated `APISpec` model with no errors

#### Scenario: YAML with anchors and aliases loads successfully
- **WHEN** the YAML file uses anchor (`&`) and alias (`*`) syntax
- **THEN** `safe_load` SHALL resolve them and the parser SHALL proceed normally

#### Scenario: Missing file raises a clear error
- **WHEN** `parse_spec()` is called with a path that does not exist
- **THEN** it SHALL raise a `FileNotFoundError` with the attempted path in the message

---

### Requirement: Parser resolves local $ref pointers
The system SHALL resolve `$ref` strings of the form `#/components/schemas/<Name>` by inlining the referenced schema from the spec's `components.schemas` section before extraction begins.

#### Scenario: $ref in request body is resolved
- **WHEN** a request body schema uses `$ref: '#/components/schemas/User'`
- **THEN** the referenced schema SHALL be inlined before `_summarize_schema()` is called

#### Scenario: Circular $ref is handled without infinite loop
- **WHEN** schema A references schema B and schema B references schema A
- **THEN** the resolver SHALL break the cycle, log a warning, and return a partial resolution without raising

#### Scenario: Unresolvable $ref is handled gracefully
- **WHEN** a `$ref` points to a path not present in `components.schemas`
- **THEN** a warning SHALL be logged and the ref SHALL be left as-is without crashing

---

### Requirement: Parser extracts supported HTTP method endpoints
The system SHALL iterate all paths and methods in the spec and create one `APIEndpoint` per supported HTTP method (GET, POST, PUT, PATCH, DELETE).

#### Scenario: All five supported methods are extracted
- **WHEN** a path defines GET, POST, PUT, PATCH, and DELETE operations
- **THEN** five `APIEndpoint` instances SHALL be created, one per method

#### Scenario: Unsupported methods are skipped
- **WHEN** a path defines OPTIONS, HEAD, or TRACE operations
- **THEN** those operations SHALL be silently skipped and not appear in the returned endpoints list

#### Scenario: Spec with no paths returns empty endpoint list
- **WHEN** the spec dict has no `paths` key or an empty `paths` value
- **THEN** `parse_spec()` SHALL return an `APISpec` with an empty `endpoints` list and log a warning

---

### Requirement: Parser merges path-level parameters into each endpoint
The system SHALL merge parameters defined at the path level into each endpoint on that path, with operation-level parameters taking precedence when both define a parameter with the same `name` and `in` (location) values.

#### Scenario: Path-level parameters appear on all operations
- **WHEN** a path defines a `parameters` list and has multiple operations
- **THEN** each operation's `parameters` list SHALL include the path-level parameters

#### Scenario: Operation-level parameter overrides path-level parameter
- **WHEN** an operation defines a parameter with the same name and location as a path-level parameter
- **THEN** the operation-level definition SHALL be used and the path-level definition SHALL be discarded

---

### Requirement: Parser handles missing optional fields without crashing
The system SHALL treat missing optional OpenAPI fields as empty or null rather than raising an error.

#### Scenario: Missing summary and description use None
- **WHEN** an endpoint operation has no `summary` or `description` fields
- **THEN** the resulting `APIEndpoint` SHALL have `summary=None` and `description=None`

#### Scenario: Missing info.description uses None
- **WHEN** the spec's `info` object has no `description` field
- **THEN** the resulting `APISpec` SHALL have `description=None`

#### Scenario: Missing info.title or info.version falls back to "Unknown"
- **WHEN** the spec's `info` object is missing `title` or `version`
- **THEN** the parser SHALL use `"Unknown"` for the missing field and log a warning

---

### Requirement: Parser summarizes schemas as human-readable strings
The system SHALL convert JSON Schema objects into a concise readable string showing field names and types for use in `RequestBody.schema_summary` and `ResponseInfo.schema_summary`.

#### Scenario: Flat object schema produces bracketed field list
- **WHEN** `_summarize_schema()` is called with `{"type": "object", "properties": {"id": {"type": "string"}, "count": {"type": "integer"}}}`
- **THEN** it SHALL return a string like `"{ id: string, count: integer }"`

#### Scenario: Nested objects are summarized up to depth 3
- **WHEN** a schema has objects nested more than 3 levels deep
- **THEN** the summary SHALL truncate with `...` beyond the third level

#### Scenario: Array schema includes item type
- **WHEN** a schema has `"type": "array"` with an `items` definition
- **THEN** the summary SHALL indicate the array and its item type (e.g., `"array of { id: string }"`)

#### Scenario: Empty or null schema returns empty string
- **WHEN** `_summarize_schema()` is called with `None` or an empty dict
- **THEN** it SHALL return an empty string `""`

---

### Requirement: Parser extracts request body into RequestBody model
The system SHALL extract an endpoint's `requestBody` field into a `RequestBody` model when present.

#### Scenario: JSON request body is extracted with content type
- **WHEN** an endpoint has a `requestBody` with `content["application/json"]`
- **THEN** the resulting `RequestBody` SHALL have `content_type="application/json"` and a non-empty `schema_summary`

#### Scenario: Endpoint with no requestBody produces None
- **WHEN** an endpoint has no `requestBody` field
- **THEN** `APIEndpoint.request_body` SHALL be `None`

---

### Requirement: Parser extracts responses into ResponseInfo models
The system SHALL extract each status code entry from an endpoint's `responses` dict into a `ResponseInfo` model.

#### Scenario: Multiple status codes are all extracted
- **WHEN** an endpoint defines `200`, `400`, and `404` responses
- **THEN** three `ResponseInfo` instances SHALL be created with the correct `status_code` strings

#### Scenario: Response with no schema produces None schema_summary
- **WHEN** a response entry has no `content` field (e.g., a 204 No Content)
- **THEN** the resulting `ResponseInfo.schema_summary` SHALL be `None`
