import os

# Must be set before src.generator is imported, as the module initializes
# the Anthropic client at module level and requires this env var.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
