import re
import pytest
from src.utils import PRICING, estimate_cost, format_cost, sanitize_anchor, create_progress_bar


class TestPricing:
    def test_pricing_is_non_empty_dict(self):
        assert isinstance(PRICING, dict)
        assert len(PRICING) > 0

    def test_pricing_contains_expected_models(self):
        assert "claude-sonnet-4-6" in PRICING
        assert "claude-haiku-4-5-20251001" in PRICING

    def test_pricing_entries_have_input_and_output_keys(self):
        for model, rates in PRICING.items():
            assert "input" in rates, f"{model} missing 'input' key"
            assert "output" in rates, f"{model} missing 'output' key"
            assert rates["input"] > 0, f"{model} input rate must be positive"
            assert rates["output"] > 0, f"{model} output rate must be positive"


class TestEstimateCost:
    def test_sonnet_known_token_counts(self):
        # 1000 input * $3.00 + 500 output * $15.00 / 1_000_000 = 0.0105
        result = estimate_cost(1000, 500, "claude-sonnet-4-6")
        assert result == pytest.approx(0.0105)

    def test_haiku_known_token_counts(self):
        # 2000 input * $0.80 + 1000 output * $4.00 / 1_000_000 = 0.0056
        result = estimate_cost(2000, 1000, "claude-haiku-4-5-20251001")
        assert result == pytest.approx(0.0056)

    def test_unknown_model_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown model"):
            estimate_cost(100, 100, "gpt-4-turbo")

    def test_zero_tokens_returns_zero(self):
        result = estimate_cost(0, 0, "claude-sonnet-4-6")
        assert result == 0.0


class TestFormatCost:
    def test_formats_small_cost(self):
        assert format_cost(0.0042) == "$0.0042"

    def test_formats_zero(self):
        assert format_cost(0.0) == "$0.0000"

    def test_format_structure(self):
        result = format_cost(1.23456789)
        assert result.startswith("$")
        parts = result[1:].split(".")
        assert len(parts) == 2
        assert len(parts[1]) == 4


class TestSanitizeAnchor:
    def test_lowercases_input(self):
        result = sanitize_anchor("GET /Users")
        assert result == result.lower()

    def test_replaces_spaces_with_hyphens(self):
        assert sanitize_anchor("List Members") == "list-members"

    def test_strips_non_alphanumeric_non_hyphen(self):
        result = sanitize_anchor("POST /api/v1/members")
        assert "/" not in result
        assert result == "post-apiv1members"

    def test_empty_string(self):
        result = sanitize_anchor("")
        assert result == ""


class TestCreateProgressBar:
    def test_standard_progress(self):
        assert create_progress_bar(3, 12) == "[3/12] Generating..."

    def test_single_item(self):
        assert create_progress_bar(1, 1) == "[1/1] Generating..."
