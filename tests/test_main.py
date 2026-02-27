import sys
from unittest.mock import MagicMock, call, mock_open, patch

import pytest

from src.main import build_parser, main
from src.models import APIEndpoint, APISpec, GeneratedDoc, GenerationResult, HTTPMethod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_spec():
    endpoint = APIEndpoint(
        method=HTTPMethod.GET,
        path="/api/v1/items",
        summary="List items",
    )
    return APISpec(
        title="Test API",
        version="1.0.0",
        endpoints=[endpoint],
    )


@pytest.fixture
def minimal_result():
    doc = GeneratedDoc(
        endpoint_ref="GET /api/v1/items",
        markdown="## GET /api/v1/items\nReturns items.",
        tokens_used=150,
        model="claude-sonnet-4-6",
    )
    return GenerationResult(
        api_title="Test API",
        api_version="1.0.0",
        docs=[doc],
        total_tokens=150,
        total_cost_usd=0.00045,
        model="claude-sonnet-4-6",
    )


SAMPLE_OVERVIEW = "This API provides access to items."


# ---------------------------------------------------------------------------
# build_parser tests
# ---------------------------------------------------------------------------

class TestBuildParser:
    def test_defaults(self):
        parser = build_parser()
        args = parser.parse_args(["specs/sample.json"])
        assert args.spec == "specs/sample.json"
        assert args.output == "output/docs.md"
        assert args.format == "markdown"
        assert args.model == "claude-sonnet-4-6"
        assert args.stream is False
        assert args.verbose is False

    def test_all_flags(self):
        parser = build_parser()
        args = parser.parse_args([
            "specs/other.yaml",
            "-o", "out/result.html",
            "-f", "html",
            "-m", "claude-haiku-4-5-20251001",
            "--stream",
            "--verbose",
        ])
        assert args.spec == "specs/other.yaml"
        assert args.output == "out/result.html"
        assert args.format == "html"
        assert args.model == "claude-haiku-4-5-20251001"
        assert args.stream is True
        assert args.verbose is True

    def test_invalid_format_raises(self):
        parser = build_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["specs/sample.json", "-f", "pdf"])
        assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# main() error path tests
# ---------------------------------------------------------------------------

class TestMainErrors:
    def test_missing_api_key_exits_1(self, capsys):
        with patch.dict("os.environ", {}, clear=True):
            with patch("src.main.load_dotenv"):
                with patch.object(sys, "argv", ["main", "specs/sample.json"]):
                    with pytest.raises(SystemExit) as exc_info:
                        main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "ANTHROPIC_API_KEY" in captured.err

    def test_missing_spec_file_exits_nonzero(self, capsys):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}, clear=False):
            with patch("src.main.load_dotenv"):
                with patch.object(sys, "argv", ["main", "nonexistent.json"]):
                    with patch("src.parser.parse_spec", side_effect=FileNotFoundError("Spec file not found: nonexistent.json")):
                        with pytest.raises(SystemExit) as exc_info:
                            main()
        assert exc_info.value.code != 0
        captured = capsys.readouterr()
        assert "nonexistent.json" in captured.err

    def test_invalid_spec_exits_nonzero(self, capsys):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}, clear=False):
            with patch("src.main.load_dotenv"):
                with patch.object(sys, "argv", ["main", "bad.json"]):
                    with patch("src.parser.parse_spec", side_effect=ValueError("Failed to parse")):
                        with pytest.raises(SystemExit) as exc_info:
                            main()
        assert exc_info.value.code != 0
        captured = capsys.readouterr()
        assert "Error" in captured.err


# ---------------------------------------------------------------------------
# main() success path tests
# ---------------------------------------------------------------------------

class TestMainSuccess:
    def _run_main(self, argv, spec, result, overview, fmt="markdown"):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}, clear=False):
            with patch("src.main.load_dotenv"):
                with patch.object(sys, "argv", argv):
                    with patch("src.parser.parse_spec", return_value=spec) as mock_parse:
                        with patch("src.generator.generate_overview", return_value=overview) as mock_overview:
                            with patch("src.generator.generate_full_docs", return_value=result) as mock_full:
                                with patch("src.formatter.format_markdown", return_value="md output") as mock_md:
                                    with patch("src.formatter.format_html", return_value="html output") as mock_html:
                                        with patch("os.makedirs") as mock_makedirs:
                                            with patch("builtins.open", mock_open()) as mock_file:
                                                with patch("builtins.input", return_value="y"):
                                                    main()
                                                    return (
                                                        mock_parse, mock_overview, mock_full,
                                                        mock_md, mock_html, mock_makedirs, mock_file
                                                    )

    def test_markdown_pipeline(self, minimal_spec, minimal_result):
        argv = ["main", "specs/sample.json"]
        mocks = self._run_main(argv, minimal_spec, minimal_result, SAMPLE_OVERVIEW)
        mock_parse, mock_overview, mock_full, mock_md, mock_html, _, _ = mocks

        mock_parse.assert_called_once_with("specs/sample.json")
        mock_overview.assert_called_once_with(minimal_spec, model="claude-sonnet-4-6")
        mock_full.assert_called_once_with(minimal_spec, model="claude-sonnet-4-6", stream=False)
        mock_md.assert_called_once_with(minimal_result, SAMPLE_OVERVIEW)
        mock_html.assert_not_called()

    def test_html_pipeline(self, minimal_spec, minimal_result):
        argv = ["main", "specs/sample.json", "--format", "html", "-o", "out/docs.html"]
        mocks = self._run_main(argv, minimal_spec, minimal_result, SAMPLE_OVERVIEW, fmt="html")
        mock_parse, mock_overview, mock_full, mock_md, mock_html, _, _ = mocks

        mock_html.assert_called_once_with(minimal_result, SAMPLE_OVERVIEW)
        mock_md.assert_not_called()

    def test_output_directory_created(self, minimal_spec, minimal_result):
        argv = ["main", "specs/sample.json", "-o", "output/subdir/docs.md"]
        mocks = self._run_main(argv, minimal_spec, minimal_result, SAMPLE_OVERVIEW)
        _, _, _, _, _, mock_makedirs, _ = mocks

        mock_makedirs.assert_called_once_with("output/subdir", exist_ok=True)

    def test_stream_flag_passed_to_generator(self, minimal_spec, minimal_result):
        argv = ["main", "specs/sample.json", "--stream"]
        mocks = self._run_main(argv, minimal_spec, minimal_result, SAMPLE_OVERVIEW)
        _, _, mock_full, _, _, _, _ = mocks

        mock_full.assert_called_once_with(minimal_spec, model="claude-sonnet-4-6", stream=True)
