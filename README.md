# AI Doc Generator

A CLI tool that reads an OpenAPI/Swagger specification file and uses the Anthropic Claude API to generate clear, developer-friendly API documentation in Markdown or HTML.

## How it works

```
OpenAPI spec (JSON/YAML)
  → parse endpoints
  → generate docs per endpoint via Claude
  → assemble into Markdown or HTML
  → write to output file
```

## Requirements

- Python 3.12+
- An [Anthropic API key](https://console.anthropic.com/)

## Installation

```bash
# Clone the repo
git clone https://github.com/your-org/ai-doc-generator.git
cd ai-doc-generator

# Create and activate a virtual environment
python -m venv .venv
source .venv/Scripts/activate   # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---|---|
| `anthropic>=0.40.0` | Anthropic Claude API client |
| `pydantic>=2.0.0` | Data validation and models |
| `python-dotenv>=1.0.0` | Load environment variables from `.env` |
| `PyYAML>=6.0` | Parse YAML spec files |
| `markdown>=3.0` | Convert Markdown to HTML for `--format html` |
| `pytest>=8.0.0` | Test runner |

## Environment setup

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | — | Your Anthropic API key |
| `DEFAULT_MODEL` | No | `claude-sonnet-4-6` | Claude model to use |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

## Usage

```bash
python -m src.main <path-to-spec> [options]
```

### Arguments

| Argument | Description |
|---|---|
| `spec` | Path to OpenAPI spec file (JSON or YAML) |
| `-o`, `--output` | Output file path (default: `output/docs.md`) |
| `-f`, `--format` | Output format: `markdown` or `html` (default: `markdown`) |
| `-m`, `--model` | Claude model to use (default: `claude-sonnet-4-6`) |
| `--stream` | Stream LLM output to the terminal in real-time |
| `--verbose` | Enable verbose logging |

### Examples

Generate Markdown docs from a JSON spec:
```bash
python -m src.main specs/sample-rewards-api.json
```

Generate HTML docs and write to a custom path:
```bash
python -m src.main specs/sample-rewards-api.json --format html -o output/docs.html
```

Stream output in real-time using a faster model:
```bash
python -m src.main specs/api.yaml --stream -m claude-haiku-4-5-20251001
```

## Running tests

```bash
python -m pytest tests/ -v
```

## Project structure

```
ai-doc-generator/
├── src/
│   ├── main.py        # CLI entry point
│   ├── parser.py      # OpenAPI spec parsing
│   ├── generator.py   # Anthropic API calls and doc generation
│   ├── formatter.py   # Markdown/HTML assembly
│   ├── prompts.py     # LLM prompt templates
│   ├── models.py      # Pydantic data models
│   └── utils.py       # Cost estimation and helpers
├── specs/             # Place your OpenAPI spec files here
├── output/            # Generated docs are written here
├── tests/             # pytest test suite
├── .env               # Your API key (not committed)
└── requirements.txt
```
