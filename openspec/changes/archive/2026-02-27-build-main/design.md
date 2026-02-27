## Context

All pipeline modules (`parser`, `generator`, `formatter`, `utils`, `prompts`) are implemented and tested. `src/main.py` is the only missing file. The module needs to wire these components into a single runnable command with a clean CLI interface and consistent error handling.

## Goals / Non-Goals

**Goals:**
- Implement `src/main.py` as the `argparse`-based CLI entry point
- Orchestrate the full pipeline: parse → generate overview → generate all endpoint docs → format → write output
- Validate environment (API key) before any API calls are made
- Print user-friendly startup and completion summaries
- Handle all error exits cleanly with non-zero exit codes
- Add `tests/test_main.py` with unit tests covering arg parsing, pipeline flow, and error paths

**Non-Goals:**
- No changes to any existing module (`parser`, `generator`, `formatter`, `utils`, `prompts`, `models`)
- No new dependencies (uses `argparse` from stdlib, existing packages)
- No stretch goals (batch mode, diff mode, caching, PDF output)

## Decisions

### Use `argparse` directly (not `click` or `typer`)

The project spec and `CLAUDE.md` prescribe `argparse`. All other modules are already implemented; adding a new CLI framework dependency is unnecessary and inconsistent with the established stack.

### Run pipeline steps sequentially, not concurrently

`generate_overview` and `generate_full_docs` both make Anthropic API calls. Running them sequentially keeps control flow simple and error handling predictable. The generator module already handles endpoint-level progress printing.

### Print summaries to stdout, errors to stderr

Startup summary (API title, endpoint count) and completion summary (output path, tokens, cost, elapsed time) go to `stdout`. Error messages go to `stderr` so they don't pollute piped output.

### Use `time.time()` for elapsed time

No need for a higher-precision timer; wall-clock seconds is sufficient for the completion summary.

### Default output path: `output/docs.md`

Matches PROJECT.md. The `output/` directory is created if it doesn't exist (`os.makedirs(..., exist_ok=True)`).

### Test strategy: mock all external calls

`tests/test_main.py` patches `parser.parse_spec`, `generator.generate_overview`, `generator.generate_full_docs`, and `formatter.format_markdown`/`format_html` so tests run without filesystem or API access. Arg parsing is tested by calling `main()` directly with patched `sys.argv`.

## Risks / Trade-offs

- [Streaming output interleaved with progress prints] → Streaming is handled inside `generator.generate_full_docs`; `main.py` just passes the `--stream` flag through. No additional interleaving logic needed.
- [Output directory may not exist] → Mitigated by `os.makedirs(output_dir, exist_ok=True)` before writing.
- [API key loaded from `.env` but also settable via env var directly] → `python-dotenv` `load_dotenv()` does not override existing env vars by default, so both sources work correctly.

## Open Questions

*(none — requirements are fully specified in PROJECT.md)*
