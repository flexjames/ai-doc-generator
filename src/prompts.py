from src.models import APIEndpoint, APISpec

SYSTEM_PROMPT = """You are a senior technical writer specializing in API documentation.

Your task is to write clear, accurate, and developer-friendly API documentation in Markdown format.

Guidelines:
- Write for developers who are integrating with this API for the first time
- Include a concise description of what the endpoint does and when to use it
- Provide realistic, domain-appropriate request and response examples — never use placeholder values like "foo", "bar", "example", "test", or "string"
- Cover common error codes and explain how a developer should handle them
- Add practical tips where relevant (e.g. pagination, rate limits, required headers)
- Keep the tone clear and direct
- Output only Markdown — no preamble, no commentary outside the documentation itself
"""


def build_endpoint_prompt(endpoint: APIEndpoint) -> str:
    """Build the user-turn prompt asking the LLM to document a single API endpoint."""
    lines: list[str] = []

    lines.append(f"Document the following API endpoint:\n")
    lines.append(f"**Method:** {endpoint.method.value}")
    lines.append(f"**Path:** {endpoint.path}")

    if endpoint.operation_id:
        lines.append(f"**Operation ID:** {endpoint.operation_id}")

    if endpoint.summary:
        lines.append(f"**Summary:** {endpoint.summary}")

    if endpoint.description:
        lines.append(f"**Description:** {endpoint.description}")

    if endpoint.tags:
        lines.append(f"**Tags:** {', '.join(endpoint.tags)}")

    if endpoint.parameters:
        lines.append("\n**Parameters:**")
        for param in endpoint.parameters:
            required_label = "required" if param.required else "optional"
            schema_type = param.schema_type
            if param.format:
                schema_type = f"{schema_type} ({param.format})"
            desc = f" — {param.description}" if param.description else ""
            extras = []
            if param.enum:
                extras.append(f"allowed values: {', '.join(param.enum)}")
            if param.example:
                extras.append(f"example: {param.example}")
            extras_str = f" [{'; '.join(extras)}]" if extras else ""
            lines.append(
                f"- `{param.name}` ({param.location}, {schema_type}, {required_label}){desc}{extras_str}"
            )

    if endpoint.request_body:
        lines.append(f"\n**Request Body** (`{endpoint.request_body.content_type}`):")
        lines.append(f"{endpoint.request_body.schema_summary}")

    if endpoint.responses:
        lines.append("\n**Responses:**")
        for response in endpoint.responses:
            schema = f" — {response.schema_summary}" if response.schema_summary else ""
            lines.append(f"- `{response.status_code}`: {response.description}{schema}")

    lines.append(
        "\nWrite complete documentation for this endpoint including: a description of its purpose "
        "and use cases, a realistic request example with domain-appropriate sample values, a "
        "realistic response example, common error codes and how to handle them, and any practical "
        "tips for developers."
    )

    return "\n".join(lines)


def build_overview_prompt(spec: APISpec) -> str:
    """Build the user-turn prompt asking the LLM to write an API overview/introduction section."""
    lines: list[str] = []

    lines.append(f"Write an overview and introduction section for the following API:\n")
    lines.append(f"**Title:** {spec.title}")
    lines.append(f"**Version:** {spec.version}")

    if spec.description:
        lines.append(f"**Description:** {spec.description}")

    if spec.base_url:
        lines.append(f"**Base URL:** {spec.base_url}")

    lines.append(f"\n**Endpoints ({len(spec.endpoints)}):**")
    for ep in spec.endpoints:
        summary = f" — {ep.summary}" if ep.summary else ""
        lines.append(f"- {ep.method.value} {ep.path}{summary}")

    lines.append(
        "\nWrite an introduction section suitable for the top of the API documentation. "
        "Include: what this API does, who it is for, key concepts a developer needs to understand, "
        "and a brief overview of the available endpoints."
    )

    return "\n".join(lines)
