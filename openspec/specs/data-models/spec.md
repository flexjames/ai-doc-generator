## ADDED Requirements

### Requirement: HTTPMethod enum covers all supported HTTP verbs
The system SHALL define an `HTTPMethod` enum that inherits from both `str` and `Enum`, with members GET, POST, PUT, PATCH, and DELETE.

#### Scenario: Enum members compare equal to plain strings
- **WHEN** `HTTPMethod.GET` is compared to the string `"GET"`
- **THEN** the comparison SHALL return `True`

#### Scenario: Unsupported verbs are not members
- **WHEN** code attempts to access `HTTPMethod.OPTIONS` or `HTTPMethod.HEAD`
- **THEN** an `AttributeError` SHALL be raised

---

### Requirement: Parameter model validates API parameter data
The system SHALL define a `Parameter` Pydantic v2 model with fields: `name` (str, required), `location` (str, required), `required` (bool, default `False`), `schema_type` (str, default `"string"`), and `description` (Optional[str], default `None`).

#### Scenario: Valid parameter with all fields
- **WHEN** a `Parameter` is constructed with `name="page"`, `location="query"`, `required=False`, `schema_type="integer"`, `description="Page number"`
- **THEN** the model SHALL be created without errors and all fields SHALL reflect the supplied values

#### Scenario: Parameter with only required fields
- **WHEN** a `Parameter` is constructed with only `name` and `location`
- **THEN** `required` SHALL default to `False`, `schema_type` SHALL default to `"string"`, `description` SHALL default to `None`

#### Scenario: Parameter rejects missing required fields
- **WHEN** a `Parameter` is constructed without a `name`
- **THEN** Pydantic SHALL raise a `ValidationError`

---

### Requirement: RequestBody model captures request payload metadata
The system SHALL define a `RequestBody` Pydantic v2 model with fields: `content_type` (str, default `"application/json"`), `schema_summary` (str, required), and `required` (bool, default `True`).

#### Scenario: Valid request body
- **WHEN** a `RequestBody` is constructed with `schema_summary="{ id: string, name: string }"`
- **THEN** the model SHALL be created and `content_type` SHALL default to `"application/json"` and `required` SHALL default to `True`

#### Scenario: RequestBody rejects missing schema_summary
- **WHEN** a `RequestBody` is constructed without `schema_summary`
- **THEN** Pydantic SHALL raise a `ValidationError`

---

### Requirement: ResponseInfo model captures HTTP response metadata
The system SHALL define a `ResponseInfo` Pydantic v2 model with fields: `status_code` (str, required), `description` (str, required), and `schema_summary` (Optional[str], default `None`).

#### Scenario: Valid response with schema
- **WHEN** a `ResponseInfo` is constructed with `status_code="200"`, `description="Success"`, `schema_summary="{ id: string }"`
- **THEN** all fields SHALL reflect the supplied values

#### Scenario: Valid response without schema
- **WHEN** a `ResponseInfo` is constructed with only `status_code` and `description`
- **THEN** `schema_summary` SHALL default to `None`

---

### Requirement: APIEndpoint model aggregates all data for a single endpoint
The system SHALL define an `APIEndpoint` Pydantic v2 model with fields: `method` (HTTPMethod, required), `path` (str, required), `operation_id` (Optional[str], default `None`), `summary` (Optional[str], default `None`), `description` (Optional[str], default `None`), `tags` (list[str], default empty list), `parameters` (list[Parameter], default empty list), `request_body` (Optional[RequestBody], default `None`), and `responses` (list[ResponseInfo], default empty list).

#### Scenario: Minimal valid endpoint
- **WHEN** an `APIEndpoint` is constructed with only `method=HTTPMethod.GET` and `path="/users"`
- **THEN** the model SHALL be created and list fields SHALL default to empty lists and optional fields SHALL default to `None`

#### Scenario: Full endpoint with all fields
- **WHEN** an `APIEndpoint` is constructed with method, path, operation_id, summary, description, tags, parameters, request_body, and responses
- **THEN** all fields SHALL reflect the supplied values

#### Scenario: Endpoint rejects invalid HTTP method
- **WHEN** an `APIEndpoint` is constructed with `method="OPTIONS"`
- **THEN** Pydantic SHALL raise a `ValidationError`

#### Scenario: List fields are independent across instances
- **WHEN** two `APIEndpoint` instances are created with default list fields and a tag is appended to the first instance's tags
- **THEN** the second instance's `tags` SHALL still be empty

---

### Requirement: APISpec model aggregates all endpoints for an API
The system SHALL define an `APISpec` Pydantic v2 model with fields: `title` (str, required), `version` (str, required), `description` (Optional[str], default `None`), `base_url` (Optional[str], default `None`), and `endpoints` (list[APIEndpoint], required).

#### Scenario: Valid spec with endpoints
- **WHEN** an `APISpec` is constructed with `title`, `version`, and a non-empty `endpoints` list
- **THEN** the model SHALL be created and all fields SHALL reflect the supplied values

#### Scenario: Valid spec with empty endpoints list
- **WHEN** an `APISpec` is constructed with an empty `endpoints` list
- **THEN** the model SHALL be created without errors

#### Scenario: APISpec rejects missing title
- **WHEN** an `APISpec` is constructed without `title`
- **THEN** Pydantic SHALL raise a `ValidationError`

---

### Requirement: GeneratedDoc model holds a single endpoint's output
The system SHALL define a `GeneratedDoc` Pydantic v2 model with fields: `endpoint_ref` (str, required), `markdown` (str, required), `tokens_used` (int, required), and `model` (str, required).

#### Scenario: Valid generated doc
- **WHEN** a `GeneratedDoc` is constructed with `endpoint_ref="GET /users/{id}"`, `markdown="# GET /users/{id}\n..."`, `tokens_used=450`, `model="claude-sonnet-4-20250514"`
- **THEN** the model SHALL be created and all fields SHALL reflect the supplied values

#### Scenario: GeneratedDoc serializes to dict
- **WHEN** `model_dump()` is called on a valid `GeneratedDoc`
- **THEN** it SHALL return a dict with keys `endpoint_ref`, `markdown`, `tokens_used`, and `model`

---

### Requirement: GenerationResult model aggregates all endpoint docs and cost data
The system SHALL define a `GenerationResult` Pydantic v2 model with fields: `api_title` (str, required), `api_version` (str, required), `docs` (list[GeneratedDoc], required), `total_tokens` (int, required), `total_cost_usd` (float, required), and `model` (str, required).

#### Scenario: Valid generation result
- **WHEN** a `GenerationResult` is constructed with all required fields including a non-empty `docs` list
- **THEN** the model SHALL be created and all fields SHALL reflect the supplied values

#### Scenario: GenerationResult serializes to dict with nested docs
- **WHEN** `model_dump()` is called on a `GenerationResult` containing `GeneratedDoc` instances
- **THEN** the returned dict SHALL contain a `docs` key whose value is a list of dicts (not `GeneratedDoc` instances)

#### Scenario: GenerationResult rejects invalid total_cost_usd type
- **WHEN** a `GenerationResult` is constructed with `total_cost_usd="not-a-float"`
- **THEN** Pydantic SHALL raise a `ValidationError`
