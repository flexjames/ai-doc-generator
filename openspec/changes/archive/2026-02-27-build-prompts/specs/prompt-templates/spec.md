## ADDED Requirements

### Requirement: System prompt defines the LLM's role and output requirements
The system SHALL define a module-level `SYSTEM_PROMPT` string constant that instructs the LLM to act as a senior technical writer, output Markdown, use realistic domain-appropriate sample data, and include description, use cases, request/response examples, error scenarios, and tips for each endpoint.

#### Scenario: SYSTEM_PROMPT is a non-empty string
- **WHEN** `SYSTEM_PROMPT` is imported from `src.prompts`
- **THEN** it SHALL be a `str` instance with length greater than zero

#### Scenario: SYSTEM_PROMPT instructs Markdown output
- **WHEN** the content of `SYSTEM_PROMPT` is inspected
- **THEN** it SHALL contain the word "Markdown" (case-insensitive)

#### Scenario: SYSTEM_PROMPT instructs realistic sample data
- **WHEN** the content of `SYSTEM_PROMPT` is inspected
- **THEN** it SHALL instruct the model to use realistic sample data and not use placeholder values like "foo", "bar", or "example"

#### Scenario: SYSTEM_PROMPT instructs technical writer role
- **WHEN** the content of `SYSTEM_PROMPT` is inspected
- **THEN** it SHALL reference the role of a technical writer

---

### Requirement: build_endpoint_prompt constructs a user message for a single endpoint
The system SHALL provide a `build_endpoint_prompt(endpoint: APIEndpoint) -> str` function that builds a prompt string containing the endpoint's HTTP method, path, summary, description, all parameters with types and descriptions, request body schema, and response schemas, and requests realistic examples and common error handling guidance.

#### Scenario: Prompt includes HTTP method and path
- **WHEN** `build_endpoint_prompt()` is called with an `APIEndpoint`
- **THEN** the returned string SHALL contain the endpoint's HTTP method value and path

#### Scenario: Prompt includes parameters when present
- **WHEN** `build_endpoint_prompt()` is called with an endpoint that has parameters
- **THEN** the returned string SHALL include each parameter's name, location, type, and required status

#### Scenario: Prompt includes request body when present
- **WHEN** `build_endpoint_prompt()` is called with an endpoint that has a `request_body`
- **THEN** the returned string SHALL include the content type and schema summary

#### Scenario: Prompt handles missing request body gracefully
- **WHEN** `build_endpoint_prompt()` is called with an endpoint where `request_body` is `None`
- **THEN** the returned string SHALL not raise and SHALL not contain misleading request body content

#### Scenario: Prompt includes all response status codes
- **WHEN** `build_endpoint_prompt()` is called with an endpoint that has multiple responses
- **THEN** the returned string SHALL include each response's status code and description

#### Scenario: Prompt requests realistic examples
- **WHEN** the content of the returned prompt is inspected
- **THEN** it SHALL contain a request for examples or sample values

---

### Requirement: build_overview_prompt constructs a user message for the API overview
The system SHALL provide a `build_overview_prompt(spec: APISpec) -> str` function that builds a prompt string containing the API title, version, description, base URL, and a summary of available endpoints, and requests an introduction section suitable for the top of the documentation.

#### Scenario: Prompt includes API title and version
- **WHEN** `build_overview_prompt()` is called with an `APISpec`
- **THEN** the returned string SHALL contain the spec's title and version

#### Scenario: Prompt includes endpoint count
- **WHEN** `build_overview_prompt()` is called with a spec containing endpoints
- **THEN** the returned string SHALL reference the number or list of endpoints

#### Scenario: Prompt handles spec with no description
- **WHEN** `build_overview_prompt()` is called with a spec where `description` is `None`
- **THEN** the returned string SHALL not raise and SHALL not contain "None" as a literal value

#### Scenario: Prompt requests an overview/introduction section
- **WHEN** the content of the returned prompt is inspected
- **THEN** it SHALL contain a request for an overview or introduction
