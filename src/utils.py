import re

PRICING = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
}
# costs per 1,000,000 tokens


def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    if model not in PRICING:
        raise ValueError(f"Unknown model: {model!r}")
    rates = PRICING[model]
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000


def format_cost(cost: float) -> str:
    return f"${cost:.4f}"


def sanitize_anchor(text: str) -> str:
    text = text.lower()
    text = text.replace(" ", "-")
    text = re.sub(r"[^a-z0-9-]", "", text)
    return text


def create_progress_bar(current: int, total: int) -> str:
    return f"[{current}/{total}] Generating..."


def estimate_tokens(text: str) -> int:
    """Rough token estimate based on character count (~4 chars per token)."""
    return max(1, len(text) // 4)
