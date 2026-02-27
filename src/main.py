import argparse
import logging
import os
import sys
import time

from dotenv import load_dotenv

load_dotenv()

from src import formatter, generator, parser, prompts, utils

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_OUTPUT = "output/docs.md"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="main.py",
        description="Generate API documentation from OpenAPI specs using AI.",
    )
    p.add_argument("spec", help="Path to OpenAPI spec file (JSON or YAML)")
    p.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output file path (default: {DEFAULT_OUTPUT})",
    )
    p.add_argument(
        "-f", "--format",
        choices=["markdown", "html"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    p.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help=f"Claude model to use (default: {DEFAULT_MODEL})",
    )
    p.add_argument(
        "--stream",
        action="store_true",
        help="Stream LLM output to terminal in real-time",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    p.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip cost confirmation prompt",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "Error: ANTHROPIC_API_KEY is not set. "
            "Add it to your .env file or export it as an environment variable.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        spec = parser.parse_spec(args.spec)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"{spec.title} v{spec.version} — {len(spec.endpoints)} endpoints found")

    estimated_input = sum(
        utils.estimate_tokens(prompts.build_endpoint_prompt(ep)) for ep in spec.endpoints
    ) + utils.estimate_tokens(prompts.build_overview_prompt(spec))
    estimated_output = 800 * len(spec.endpoints) + 500
    estimated_cost = utils.estimate_cost(estimated_input, estimated_output, args.model)
    print(
        f"Estimated cost: ~{utils.format_cost(estimated_cost)} "
        f"(~{estimated_input + estimated_output:,} tokens)"
    )

    if not args.yes:
        answer = input("Proceed? [y/N]: ").strip().lower()
        if answer != "y":
            print("Aborted.")
            sys.exit(0)

    start = time.time()

    overview = generator.generate_overview(spec, model=args.model)
    result = generator.generate_full_docs(spec, model=args.model, stream=args.stream)

    if args.format == "html":
        output_text = formatter.format_html(result, overview)
    else:
        output_text = formatter.format_markdown(result, overview)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output_text)

    elapsed = time.time() - start
    cost_str = utils.format_cost(result.total_cost_usd)
    print(
        f"\nDone! Output written to: {args.output}\n"
        f"  Tokens: {result.total_tokens:,}  |  Cost: {cost_str}  |  Time: {elapsed:.1f}s"
    )


if __name__ == "__main__":
    main()
