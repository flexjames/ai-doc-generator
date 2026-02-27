## Why

`src/formatter.py` is the final assembly layer of the documentation pipeline. Once `generator.py` has produced `GeneratedDoc` instances for each endpoint and an overview string, the formatter combines them into a complete, human-readable document. Without it, the CLI has no way to produce the final output file.

## What Changes

- Introduce `src/formatter.py` with `format_markdown` and `format_html` output assembly functions
- Introduce `tests/test_formatter.py` covering structure, TOC generation, stats section, and HTML output
- Add `markdown>=3.0` to `requirements.txt` for Markdown-to-HTML conversion

## Capabilities

### New Capabilities

- `doc-formatter`: Assemble a `GenerationResult` and an overview string into a complete Markdown or HTML document, including a structured header, table of contents, per-endpoint sections, and a generation stats footer

### Modified Capabilities

*(none)*

## Impact

- New file: `src/formatter.py`
- New file: `tests/test_formatter.py`
- Updated: `requirements.txt` (adds `markdown>=3.0`)
- No changes to existing modules
- Unblocks `src/main.py`
