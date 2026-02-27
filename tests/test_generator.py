from unittest.mock import MagicMock, patch

import anthropic
import httpx
import pytest

import src.generator as generator_module
from src.models import APIEndpoint, APISpec, HTTPMethod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_httpx_response(status_code: int) -> httpx.Response:
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    return httpx.Response(status_code, request=request)


def _make_api_response(text: str, input_tokens: int, output_tokens: int) -> MagicMock:
    response = MagicMock()
    response.content = [MagicMock(text=text)]
    response.usage.input_tokens = input_tokens
    response.usage.output_tokens = output_tokens
    return response


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_client(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(generator_module, "client", mock)
    return mock


@pytest.fixture
def endpoint():
    return APIEndpoint(
        method=HTTPMethod.GET,
        path="/users/{id}",
        summary="Get a user by ID",
    )


@pytest.fixture
def spec(endpoint):
    return APISpec(
        title="Test API",
        version="1.0.0",
        endpoints=[endpoint],
    )


# ---------------------------------------------------------------------------
# 3.2 generate_endpoint_doc — non-streaming
# ---------------------------------------------------------------------------

class TestGenerateEndpointDocNonStreaming:
    def test_returns_generated_doc(self, mock_client, endpoint):
        mock_client.messages.create.return_value = _make_api_response(
            "# GET /users/{id}\nSome docs.", 100, 200
        )

        doc = generator_module.generate_endpoint_doc(endpoint, "claude-sonnet-4-6", stream=False)

        assert doc.markdown == "# GET /users/{id}\nSome docs."
        assert doc.tokens_used == 300
        assert doc.model == "claude-sonnet-4-6"

    def test_endpoint_ref_format(self, mock_client, endpoint):
        mock_client.messages.create.return_value = _make_api_response("docs", 10, 20)

        doc = generator_module.generate_endpoint_doc(endpoint, "claude-sonnet-4-6", stream=False)

        assert doc.endpoint_ref == "GET /users/{id}"


# ---------------------------------------------------------------------------
# 3.3 generate_endpoint_doc — streaming
# ---------------------------------------------------------------------------

class TestGenerateEndpointDocStreaming:
    def test_prints_tokens_and_returns_doc(self, mock_client, endpoint, capsys):
        stream_ctx = MagicMock()
        stream_ctx.__enter__ = MagicMock(return_value=stream_ctx)
        stream_ctx.__exit__ = MagicMock(return_value=False)
        stream_ctx.text_stream = ["Hello", " world"]
        final = _make_api_response("Hello world", 50, 100)
        stream_ctx.get_final_message.return_value = final
        mock_client.messages.stream.return_value = stream_ctx

        doc = generator_module.generate_endpoint_doc(endpoint, "claude-sonnet-4-6", stream=True)

        captured = capsys.readouterr()
        assert "Hello" in captured.out
        assert " world" in captured.out
        assert doc.markdown == "Hello world"
        assert doc.tokens_used == 150
        assert doc.endpoint_ref == "GET /users/{id}"


# ---------------------------------------------------------------------------
# 3.4 generate_overview
# ---------------------------------------------------------------------------

class TestGenerateOverview:
    def test_returns_non_empty_string(self, mock_client, spec):
        mock_client.messages.create.return_value = _make_api_response(
            "## Overview\nThis API does things.", 80, 120
        )

        result = generator_module.generate_overview(spec, "claude-sonnet-4-6")

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Overview" in result


# ---------------------------------------------------------------------------
# 3.5 generate_full_docs
# ---------------------------------------------------------------------------

class TestGenerateFullDocs:
    def test_doc_count_and_totals(self, mock_client, spec):
        mock_client.messages.create.return_value = _make_api_response("endpoint docs", 100, 200)

        result = generator_module.generate_full_docs(spec, "claude-sonnet-4-6", stream=False)

        assert len(result.docs) == 1
        assert result.total_tokens == 300
        assert result.api_title == "Test API"
        assert result.api_version == "1.0.0"
        assert result.model == "claude-sonnet-4-6"

    def test_cost_calculated(self, mock_client, spec):
        mock_client.messages.create.return_value = _make_api_response("docs", 1_000_000, 0)

        result = generator_module.generate_full_docs(spec, "claude-sonnet-4-6", stream=False)

        # 1M input tokens at $3.00/M = $3.00
        assert result.total_cost_usd == pytest.approx(3.00)

    def test_progress_printed(self, mock_client, spec, capsys):
        mock_client.messages.create.return_value = _make_api_response("docs", 10, 20)

        generator_module.generate_full_docs(spec, "claude-sonnet-4-6", stream=False)

        captured = capsys.readouterr()
        assert "GET /users/{id}" in captured.out


# ---------------------------------------------------------------------------
# 3.6 Rate limit retry
# ---------------------------------------------------------------------------

class TestRateLimitRetry:
    def test_retries_on_429_then_succeeds(self, endpoint):
        rate_limit_err = anthropic.RateLimitError(
            message="Rate limit exceeded",
            response=_make_httpx_response(429),
            body=None,
        )
        success = ("docs", 10, 20)

        with patch("src.generator._call_api", side_effect=[rate_limit_err, success]):
            with patch("src.generator.time.sleep") as mock_sleep:
                doc = generator_module.generate_endpoint_doc(
                    endpoint, "claude-sonnet-4-6", stream=False
                )

        mock_sleep.assert_called_once_with(2)
        assert doc.tokens_used == 30

    def test_raises_after_max_retries(self, endpoint):
        rate_limit_err = anthropic.RateLimitError(
            message="Rate limit exceeded",
            response=_make_httpx_response(429),
            body=None,
        )

        with patch("src.generator._call_api", side_effect=[rate_limit_err] * 4):
            with patch("src.generator.time.sleep"):
                with pytest.raises(anthropic.RateLimitError):
                    generator_module.generate_endpoint_doc(
                        endpoint, "claude-sonnet-4-6", stream=False
                    )


# ---------------------------------------------------------------------------
# 3.7 Server error skip
# ---------------------------------------------------------------------------

class TestServerErrorSkip:
    def test_skips_endpoint_after_two_500s(self, spec, capsys):
        server_err = anthropic.InternalServerError(
            message="Internal server error",
            response=_make_httpx_response(500),
            body=None,
        )

        with patch("src.generator._call_api", side_effect=[server_err, server_err]):
            with patch("src.generator.time.sleep"):
                result = generator_module.generate_full_docs(
                    spec, "claude-sonnet-4-6", stream=False
                )

        assert len(result.docs) == 0
        captured = capsys.readouterr()
        assert "Warning: skipping" in captured.out


# ---------------------------------------------------------------------------
# 3.8 Auth error
# ---------------------------------------------------------------------------

class TestAuthError:
    def test_raises_runtime_error_on_401(self, endpoint):
        auth_err = anthropic.AuthenticationError(
            message="Invalid API key",
            response=_make_httpx_response(401),
            body=None,
        )

        with patch("src.generator._call_api", side_effect=auth_err):
            with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
                generator_module.generate_endpoint_doc(
                    endpoint, "claude-sonnet-4-6", stream=False
                )

    def test_auth_error_propagates_from_full_docs(self, spec):
        auth_err = anthropic.AuthenticationError(
            message="Invalid API key",
            response=_make_httpx_response(401),
            body=None,
        )

        with patch("src.generator._call_api", side_effect=auth_err):
            with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
                generator_module.generate_full_docs(spec, "claude-sonnet-4-6", stream=False)
