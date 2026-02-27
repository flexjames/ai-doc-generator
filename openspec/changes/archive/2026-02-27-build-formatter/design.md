## Context

`src/formatter.py` sits at the end of the pipeline, taking a `GenerationResult` and an overview string and producing the final output. It must handle both Markdown and HTML output formats. It has two dependencies: `src/models.py` (for `GenerationResult`) and `src/utils.py` (for `sanitize_anchor` and `format_cost`).

## Goals / Non-Goals

**Goals:**
- Implement `format_markdown(result: GenerationResult, overview: str) -> str` that assembles a complete Markdown document
- Implement `format_html(result: GenerationResult, overview: str) -> str` that converts the Markdown output to a complete, self-contained HTML page
- Generate a table of contents with working anchor links
- Include a generation stats section (model, tokens, cost, timestamp)

**Non-Goals:**
- Streaming output (handled by generator.py)
- CSS theming or template customization
- PDF export

## Decisions

**`format_html` delegates to `format_markdown`**
HTML output is derived from the Markdown output by calling `format_markdown` first, then converting the result with the `markdown` package. This avoids duplicating assembly logic and ensures Markdown and HTML output are always structurally equivalent.

**Python `markdown` package for HTML conversion**
The standard library has no Markdown-to-HTML converter. The `markdown` package is the most widely used, well-maintained option. The `fenced_code` and `tables` extensions are enabled to handle code blocks and tables common in API documentation.

**Fully static HTML with embedded CSS**
The generated HTML must render correctly offline in any browser. All styles are embedded in a `<style>` block — no external CSS, no CDN dependencies. Styling is kept minimal: readable font, comfortable line length, subtle code block background.

**`sanitize_anchor` from utils for TOC links**
GitHub-flavored Markdown anchor IDs are derived from heading text by lowercasing and stripping non-alphanumeric characters. `utils.sanitize_anchor` already implements this. Using it for TOC links keeps the logic consistent and avoids duplication.

**Timestamp format: `%Y-%m-%d %H:%M:%S`**
ISO 8601-like format, human-readable, unambiguous — consistent with project log output conventions.

## Risks / Trade-offs

- **`markdown` package version drift** → Mitigation: pin to `>=3.0` in requirements.txt; the API is stable across v3.x
- **TOC anchors may not match rendered HTML headings** → Mitigation: `sanitize_anchor` is applied to `endpoint_ref` for both TOC entries and `###` headings; format_html relies on the markdown renderer for heading IDs

## Open Questions

*(none)*
