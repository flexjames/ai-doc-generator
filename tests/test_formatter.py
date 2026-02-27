import pytest

from src.formatter import format_html, format_markdown
from src.models import GeneratedDoc, GenerationResult


@pytest.fixture
def sample_result():
    doc = GeneratedDoc(
        endpoint_ref="GET /users",
        markdown="Returns a list of users.",
        tokens_used=100,
        model="claude-sonnet-4-6",
    )
    return GenerationResult(
        api_title="My API",
        api_version="1.0.0",
        docs=[doc],
        total_tokens=100,
        total_cost_usd=0.0015,
        model="claude-sonnet-4-6",
    )


class TestFormatMarkdown:
    def test_returns_string(self, sample_result):
        result = format_markdown(sample_result, "An overview.")
        assert isinstance(result, str)

    def test_title_includes_api_title(self, sample_result):
        result = format_markdown(sample_result, "An overview.")
        assert "My API" in result

    def test_toc_section_contains_endpoint_ref(self, sample_result):
        result = format_markdown(sample_result, "An overview.")
        assert "Table of Contents" in result
        assert "GET /users" in result

    def test_stats_section_contains_model(self, sample_result):
        result = format_markdown(sample_result, "An overview.")
        assert "Generation Stats" in result
        assert "claude-sonnet-4-6" in result

    def test_stats_section_contains_total_tokens(self, sample_result):
        result = format_markdown(sample_result, "An overview.")
        assert "100" in result

    def test_stats_section_contains_cost_string(self, sample_result):
        result = format_markdown(sample_result, "An overview.")
        assert "$" in result

    def test_endpoint_ref_appears_as_heading(self, sample_result):
        result = format_markdown(sample_result, "An overview.")
        assert "### GET /users" in result

    def test_overview_text_appears(self, sample_result):
        result = format_markdown(sample_result, "This is the overview text.")
        assert "This is the overview text." in result


class TestFormatHTML:
    def test_returns_html(self, sample_result):
        result = format_html(sample_result, "An overview.")
        assert "<html" in result

    def test_contains_api_title(self, sample_result):
        result = format_html(sample_result, "An overview.")
        assert "My API" in result

    def test_contains_endpoint_markdown_content(self, sample_result):
        result = format_html(sample_result, "An overview.")
        assert "Returns a list of users." in result
