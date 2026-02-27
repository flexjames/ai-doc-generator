## Context

`src/prompts.py` is a prerequisite for `src/generator.py`. The project convention requires all LLM prompt text to live exclusively in this module — no prompt strings anywhere else. It has no external dependencies beyond the existing Pydantic models in `src/models.py`.

## Goals / Non-Goals

**Goals:**
- Define a `SYSTEM_PROMPT` constant that establishes the LLM's role and output requirements
- Implement `build_endpoint_prompt(endpoint: APIEndpoint) -> str` to construct a per-endpoint user message
- Implement `build_overview_prompt(spec: APISpec) -> str` to construct the API overview user message
- Keep all prompt text readable and maintainable in one place

**Non-Goals:**
- Dynamic prompt selection or prompt versioning
- Prompt caching or templating engines (Jinja2, etc.)
- Few-shot examples embedded in prompts (keep prompts concise)

## Decisions

**Plain f-strings over a templating library**
The prompts are straightforward string interpolations of model fields. A templating library (Jinja2, etc.) would add a dependency with no meaningful benefit at this complexity level. F-strings are readable, zero-dependency, and easy to test.

**`SYSTEM_PROMPT` as a module-level constant**
The system prompt doesn't vary per request — it defines the LLM's persistent role. Making it a constant (rather than a function) reflects this and avoids unnecessary function calls on every generation.

**Prompt functions accept Pydantic models directly**
`build_endpoint_prompt` takes an `APIEndpoint` and `build_overview_prompt` takes an `APISpec`. This keeps the interface clean and type-safe — callers don't need to manually extract fields before calling.

**Realistic sample data instruction in prompts**
The system prompt explicitly instructs the model to use realistic, domain-appropriate sample data rather than placeholders like "foo" or "example". This is a key quality requirement for the generated documentation.

## Risks / Trade-offs

- **Prompt quality affects all downstream output** → Mitigation: prompts are tested for required content sections and can be iterated without touching generator logic
- **Long prompts increase token usage** → Mitigation: prompts are kept concise; verbose descriptions are the endpoint data's responsibility, not the prompt's

## Open Questions

*(none)*
