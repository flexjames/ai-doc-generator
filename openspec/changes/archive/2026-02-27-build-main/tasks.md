## 1. Implement src/main.py

- [x] 1.1 Create `src/main.py` with `build_parser()` function that returns a configured `argparse.ArgumentParser` with all flags: positional `spec`, `-o/--output` (default `output/docs.md`), `-f/--format` (choices `markdown`/`html`, default `markdown`), `-m/--model` (default `claude-sonnet-4-6`), `--stream`, `--verbose`
- [x] 1.2 Implement `main()` function: load `.env` via `load_dotenv()`, validate `ANTHROPIC_API_KEY` is set (print error to stderr and `sys.exit(1)` if missing)
- [x] 1.3 In `main()`, configure logging based on `--verbose` flag, then call `parser.parse_spec(args.spec)` (catch `FileNotFoundError` and parse errors, print to stderr, exit non-zero)
- [x] 1.4 Print startup summary to stdout: API title, version, and endpoint count
- [x] 1.5 Call `generator.generate_overview(spec, model=args.model)` to get the overview string
- [x] 1.6 Call `generator.generate_full_docs(spec, model=args.model, stream=args.stream)` to get a `GenerationResult`
- [x] 1.7 Call `formatter.format_markdown(result, overview)` or `formatter.format_html(result, overview)` based on `args.format`
- [x] 1.8 Create output directory with `os.makedirs(os.path.dirname(args.output), exist_ok=True)` (handle case where output path has no directory component), then write the formatted string to `args.output`
- [x] 1.9 Print completion summary: output path, total tokens, formatted cost (`utils.format_cost(result.total_cost_usd)`), and elapsed time in seconds
- [x] 1.10 Add `if __name__ == "__main__": main()` guard at module bottom

## 2. Tests

- [x] 2.1 Create `tests/test_main.py`; add fixtures: a minimal `APISpec`, a minimal `GenerationResult`, and a sample overview string
- [x] 2.2 Test `build_parser()` defaults: verify `format=markdown`, `output=output/docs.md`, `stream=False`, `verbose=False`
- [x] 2.3 Test `build_parser()` with all flags provided: verify each parsed value is correct
- [x] 2.4 Test `main()` exits with code 1 when `ANTHROPIC_API_KEY` is not set (patch env and `sys.exit`)
- [x] 2.5 Test `main()` prints error to stderr and exits non-zero when spec file does not exist
- [x] 2.6 Test full pipeline success path: patch `parse_spec`, `generate_overview`, `generate_full_docs`, `format_markdown`, and file write; assert each is called once with correct arguments
- [x] 2.7 Test HTML format path: same as 2.6 but with `--format html`; assert `format_html` is called instead of `format_markdown`
- [x] 2.8 Test that output directory is created before writing (`os.makedirs` is called with `exist_ok=True`)
- [x] 2.9 Run `pytest tests/test_main.py -v` and confirm all tests pass
- [x] 2.10 Run full test suite `pytest tests/ -v` and confirm no regressions (all 106+ tests pass)
