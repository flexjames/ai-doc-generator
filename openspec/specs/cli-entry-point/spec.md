## ADDED Requirements

### Requirement: CLI accepts positional spec argument and optional flags
The CLI SHALL accept a positional `spec` argument (path to an OpenAPI JSON or YAML file) and the following optional flags: `-o/--output` (output file path, default `output/docs.md`), `-f/--format` (output format `markdown` or `html`, default `markdown`), `-m/--model` (Claude model ID, default `claude-sonnet-4-6`), `--stream` (stream LLM output to terminal), and `--verbose` (enable verbose logging).

#### Scenario: Default flags produce markdown output at default path
- **WHEN** user runs `python -m src.main specs/sample.json`
- **THEN** output is written to `output/docs.md` in Markdown format using the default model

#### Scenario: User overrides output format and path
- **WHEN** user runs `python -m src.main specs/sample.json --format html -o output/docs.html`
- **THEN** output is written to `output/docs.html` in HTML format

#### Scenario: Invalid format value rejected
- **WHEN** user passes `--format pdf`
- **THEN** argparse prints an error and exits with code 2

### Requirement: Environment is validated before pipeline starts
The CLI SHALL load `.env` via `python-dotenv` and verify that `ANTHROPIC_API_KEY` is set. If it is missing, the CLI SHALL print a clear error message to stderr and exit with code 1 without making any API calls.

#### Scenario: Missing API key exits cleanly
- **WHEN** `ANTHROPIC_API_KEY` is not set in the environment or `.env`
- **THEN** CLI prints an error message referencing the missing key and exits with code 1

#### Scenario: Valid API key allows pipeline to proceed
- **WHEN** `ANTHROPIC_API_KEY` is set
- **THEN** CLI proceeds to parse the spec and call the generator

### Requirement: Startup summary is printed before generation begins
After parsing the spec successfully, the CLI SHALL print the API title, version, and number of endpoints found before any LLM calls are made.

#### Scenario: Startup summary shows endpoint count
- **WHEN** spec is parsed and contains 6 endpoints
- **THEN** CLI prints a line indicating the API title, version, and "6 endpoints found"

### Requirement: Pipeline is orchestrated in correct order
The CLI SHALL call: `parser.parse_spec()` → `generator.generate_overview()` → `generator.generate_full_docs()` → `formatter.format_markdown()` or `formatter.format_html()` → write output file.

#### Scenario: Full pipeline executes end-to-end
- **WHEN** all inputs are valid and the API key is set
- **THEN** each pipeline stage is called in order and the output file is written

#### Scenario: Output directory is created if it does not exist
- **WHEN** the output path is `output/subdir/docs.md` and `output/subdir/` does not exist
- **THEN** the directory is created automatically before writing the file

### Requirement: Completion summary is printed after output is written
After writing the output file, the CLI SHALL print the output file path, total tokens used, estimated cost, and elapsed time in seconds.

#### Scenario: Completion summary includes all fields
- **WHEN** generation completes successfully
- **THEN** CLI prints output path, total tokens, formatted cost (e.g. `$0.0042`), and elapsed time

### Requirement: Spec file errors exit cleanly
If the spec file does not exist or cannot be parsed, the CLI SHALL print an error message to stderr with the file path and exit with a non-zero code.

#### Scenario: Missing spec file exits with error
- **WHEN** user provides a path to a file that does not exist
- **THEN** CLI prints an error referencing the path and exits without making API calls

#### Scenario: Invalid JSON/YAML exits with error
- **WHEN** spec file contains malformed JSON or YAML
- **THEN** CLI prints a parse error message and exits with a non-zero code
