## Why

All pipeline modules (`parser`, `generator`, `formatter`, `utils`, `prompts`) are fully implemented and tested, but there is no CLI entry point — the tool cannot be run end-to-end. `src/main.py` is the final piece that wires everything together into a usable command.

## What Changes

- Add `src/main.py` as the CLI entry point using `argparse`
- Accepts a positional `spec` argument (path to OpenAPI JSON/YAML file) and optional flags: `-o/--output`, `-f/--format`, `-m/--model`, `--stream`, `--verbose`
- Loads `.env`, validates `ANTHROPIC_API_KEY`, then orchestrates: parse → generate overview → generate all endpoint docs → format → write output file
- Prints a startup summary (API title, version, endpoint count) and a completion summary (output path, total tokens, cost, elapsed time)
- Handles all error exits with clear messages (missing key, file not found, parse errors)
- Add `tests/test_main.py` covering argument parsing, pipeline integration, and error paths

## Capabilities

### New Capabilities
- `cli-entry-point`: CLI argument parsing, pipeline orchestration, environment validation, progress reporting, and file output for the doc generator tool

### Modified Capabilities

*(none)*

## Impact

- New file: `src/main.py`
- New file: `tests/test_main.py`
- No changes to existing modules
- Tool becomes fully runnable: `python -m src.main specs/sample-rewards-api.json`
