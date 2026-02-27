## 1. Add dependency

- [x] 1.1 Add `markdown>=3.0` to `requirements.txt`

## 2. Implement src/formatter.py

- [x] 2.1 Create `src/formatter.py` with imports: `datetime`, `markdown`, `GenerationResult` from `src.models`, `sanitize_anchor` and `format_cost` from `src.utils`
- [x] 2.2 Implement `format_markdown(result: GenerationResult, overview: str) -> str` that assembles the document in this order: title heading (`# {api_title} — API Documentation`), version/generated-by blockquote lines, `## Overview` section with overview text, `## Table of Contents` with one link per `GeneratedDoc` using `sanitize_anchor(doc.endpoint_ref)`, `## Endpoints` section with each `### {endpoint_ref}` heading followed by `doc.markdown` and a `---` divider, `## Generation Stats` section with model, total tokens, estimated cost (via `format_cost`), and timestamp
- [x] 2.3 Implement `format_html(result: GenerationResult, overview: str) -> str` that calls `format_markdown`, converts it with `markdown.markdown(md, extensions=["fenced_code", "tables"])`, and wraps the result in a complete `<html>` document with a `<style>` block containing minimal readable CSS

## 3. Implement tests/test_formatter.py

- [x] 3.1 Create `tests/test_formatter.py` with imports for `pytest`, `format_markdown`, `format_html` from `src.formatter`, and model constructors from `src.models`
- [x] 3.2 Add a `pytest` fixture that builds a minimal `GenerationResult` with one `GeneratedDoc`
- [x] 3.3 `TestFormatMarkdown` — test that the return value is a string
- [x] 3.4 `TestFormatMarkdown` — test that the document title includes the API title
- [x] 3.5 `TestFormatMarkdown` — test that the TOC section exists and contains the endpoint ref
- [x] 3.6 `TestFormatMarkdown` — test that the stats section contains model name, total tokens, and cost string
- [x] 3.7 `TestFormatMarkdown` — test that the endpoint ref appears as a heading
- [x] 3.8 `TestFormatMarkdown` — test that the overview text appears in the output
- [x] 3.9 `TestFormatHTML` — test that the return value contains `<html`
- [x] 3.10 `TestFormatHTML` — test that the return value contains the API title
- [x] 3.11 `TestFormatHTML` — test that the return value contains content from the endpoint markdown

## 4. Verify

- [x] 4.1 Run `pytest tests/test_formatter.py -v` and confirm all tests pass
- [x] 4.2 Run `pytest tests/ -v` and confirm no regressions
