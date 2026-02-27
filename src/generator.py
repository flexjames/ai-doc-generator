import time

import anthropic

from src import prompts, utils
from src.models import APIEndpoint, APISpec, GeneratedDoc, GenerationResult

client = anthropic.Anthropic()

_RETRY_DELAYS = [2, 4, 8]


def _call_api(messages: list[dict], model: str, stream: bool) -> tuple[str, int, int]:
    """Make a single API call. Returns (text, input_tokens, output_tokens)."""
    if stream:
        with client.messages.stream(
            model=model,
            max_tokens=4096,
            system=prompts.SYSTEM_PROMPT,
            messages=messages,
        ) as stream_ctx:
            for text in stream_ctx.text_stream:
                print(text, end="", flush=True)
            final = stream_ctx.get_final_message()
        print()
        return final.content[0].text, final.usage.input_tokens, final.usage.output_tokens
    else:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=prompts.SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text, response.usage.input_tokens, response.usage.output_tokens


def _call_with_retry(messages: list[dict], model: str, stream: bool) -> tuple[str, int, int]:
    """Call _call_api with retry logic for transient errors."""
    rate_limit_attempts = 0
    server_error_attempts = 0

    while True:
        try:
            return _call_api(messages, model, stream)
        except anthropic.AuthenticationError:
            raise RuntimeError(
                "Authentication failed: check that ANTHROPIC_API_KEY is set and valid."
            )
        except anthropic.RateLimitError:
            if rate_limit_attempts >= len(_RETRY_DELAYS):
                raise
            delay = _RETRY_DELAYS[rate_limit_attempts]
            rate_limit_attempts += 1
            print(f"Rate limit hit, retrying in {delay}s...")
            time.sleep(delay)
        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                if server_error_attempts >= 1:
                    raise
                server_error_attempts += 1
                print(f"Server error ({e.status_code}), retrying once...")
                time.sleep(1)
            else:
                raise


def generate_endpoint_doc(
    endpoint: APIEndpoint, model: str, stream: bool = True
) -> GeneratedDoc:
    """Generate documentation for a single endpoint."""
    messages = [{"role": "user", "content": prompts.build_endpoint_prompt(endpoint)}]
    markdown, input_tokens, output_tokens = _call_with_retry(messages, model, stream)
    return GeneratedDoc(
        endpoint_ref=f"{endpoint.method.value} {endpoint.path}",
        markdown=markdown,
        tokens_used=input_tokens + output_tokens,
        model=model,
    )


def generate_overview(spec: APISpec, model: str) -> str:
    """Generate an API overview/introduction section."""
    messages = [{"role": "user", "content": prompts.build_overview_prompt(spec)}]
    text, _, _ = _call_with_retry(messages, model, stream=False)
    return text


def generate_full_docs(
    spec: APISpec, model: str, stream: bool = True
) -> GenerationResult:
    """Orchestrate documentation generation for all endpoints."""
    total_input_tokens = 0
    total_output_tokens = 0
    docs = []
    total = len(spec.endpoints)

    for i, endpoint in enumerate(spec.endpoints):
        endpoint_ref = f"{endpoint.method.value} {endpoint.path}"
        print(f"Generating: {endpoint_ref} [{i + 1}/{total}]")
        messages = [{"role": "user", "content": prompts.build_endpoint_prompt(endpoint)}]
        try:
            markdown, in_tok, out_tok = _call_with_retry(messages, model, stream)
            docs.append(
                GeneratedDoc(
                    endpoint_ref=endpoint_ref,
                    markdown=markdown,
                    tokens_used=in_tok + out_tok,
                    model=model,
                )
            )
            total_input_tokens += in_tok
            total_output_tokens += out_tok
            print(f"Done: {endpoint_ref}")
        except RuntimeError:
            raise
        except Exception as e:
            print(f"Warning: skipping {endpoint_ref} — {e}")

    total_cost = utils.estimate_cost(total_input_tokens, total_output_tokens, model)

    return GenerationResult(
        api_title=spec.title,
        api_version=spec.version,
        docs=docs,
        total_tokens=total_input_tokens + total_output_tokens,
        total_cost_usd=total_cost,
        model=model,
    )
