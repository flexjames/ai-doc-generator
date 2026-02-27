# doc-formatter Specification

## Purpose
TBD - created by archiving change build-formatter. Update Purpose after archive.
## Requirements
### Requirement: format_markdown assembles a complete Markdown document from a GenerationResult
The system SHALL provide a `format_markdown(result: GenerationResult, overview: str) -> str` function that returns a complete Markdown string containing: a title heading, version and attribution lines, an overview section, a table of contents with anchor links, a per-endpoint section for each `GeneratedDoc`, and a generation stats footer.

#### Scenario: Returns a string
- **WHEN** `format_markdown()` is called with a valid `GenerationResult` and overview string
- **THEN** it SHALL return a `str` instance

#### Scenario: Document title includes the API title
- **WHEN** `format_markdown()` is called with a `GenerationResult` whose `api_title` is "My API"
- **THEN** the returned string SHALL contain "My API"

#### Scenario: Table of contents includes endpoint refs
- **WHEN** `format_markdown()` is called with a `GenerationResult` containing one or more `GeneratedDoc` entries
- **THEN** the returned string SHALL contain a "Table of Contents" section with a link for each `endpoint_ref`

#### Scenario: Stats section contains model, tokens, and cost
- **WHEN** `format_markdown()` is called with a `GenerationResult`
- **THEN** the returned string SHALL contain a "Generation Stats" section with the model name, total token count, and a cost string starting with "$"

#### Scenario: Endpoint ref appears as a heading
- **WHEN** `format_markdown()` is called with a `GenerationResult` containing a `GeneratedDoc` with `endpoint_ref` "GET /users"
- **THEN** the returned string SHALL contain a `###` heading with that endpoint ref

#### Scenario: Overview text appears in the document
- **WHEN** `format_markdown()` is called with overview text "This API does X"
- **THEN** the returned string SHALL contain "This API does X"

---

### Requirement: format_html produces a complete, self-contained HTML document
The system SHALL provide a `format_html(result: GenerationResult, overview: str) -> str` function that returns a complete `<html>` document string. It SHALL derive its content from `format_markdown()` and convert it using the `markdown` package with `fenced_code` and `tables` extensions.

#### Scenario: Returns valid HTML
- **WHEN** `format_html()` is called with a valid `GenerationResult` and overview string
- **THEN** the returned string SHALL contain `<html`

#### Scenario: HTML document contains the API title
- **WHEN** `format_html()` is called with a `GenerationResult` whose `api_title` is "My API"
- **THEN** the returned string SHALL contain "My API"

#### Scenario: HTML document contains endpoint markdown content
- **WHEN** `format_html()` is called with a `GenerationResult` containing a `GeneratedDoc` with non-empty `markdown`
- **THEN** the returned string SHALL contain text from that markdown content

