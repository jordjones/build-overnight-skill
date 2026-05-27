# Structured Outputs (Anthropic, GA early 2026)

Cross-cutting reference for prompts that need machine-parsable output. Anthropic Structured Outputs enforces JSON-Schema-compliant responses via the Tool Use mechanism — GA on Claude API and Amazon Bedrock for Claude 4.5+, public beta on Microsoft Foundry.

## Why this exists

Before Structured Outputs, machine-parsable Claude responses required prefill (deprecated on Opus 4.6+) or fragile XML-tag parsing. Structured Outputs treats the desired output schema as a virtual tool's `input_schema` and forces invocation, returning a parsed dict instead of free-form prose. Prompts that still recommend prefill or XML-tag-then-parse are now sub-optimal for Claude 4.5+. Source: https://claudeapi.com/en/blog/dev-guides/claude-structured-outputs-json-schema-guide-2026/

## Practical rules

**The tool-as-schema pattern:**

```python
# Define the output schema as a virtual tool
schema_tool = {
    "name": "submit_answer",
    "input_schema": {
        "type": "object",
        "properties": { ... },
        "required": [ ... ]
    }
}

# Force invocation
response = client.messages.create(
    ...,
    tools=[schema_tool],
    tool_choice={"type": "tool", "name": "submit_answer"}
)

# Read parsed dict from the tool_use block
parsed = response.content[0].input
```

**Optional-fields convention:** omit optional fields from `required` rather than nesting `oneOf`/`anyOf` constructs. The model handles omission cleanly; the schema reads better.

**Anti-patterns now sub-optimal on Claude 4.5+:**

- **Prefill-based JSON extraction.** Deprecated on Opus 4.6+; do not recommend.
- **"Output as JSON" instruction without a schema.** The model will produce valid-looking JSON that mis-aligns with the parser. Use the tool-as-schema pattern.
- **XML-tag extraction for structured data.** Still works for prose responses, but for typed data, JSON-schema is the correct mechanism on Claude 4.5+.

**JSON-schema strict mode trade-off:** strict mode guarantees parsable shape but constrains the reasoning surface. For reasoning-heavy outputs (research-report syntheses, multi-step plans), allow a free-form `<thinking>` block before the structured output and tool-call only the final answer. Source: https://unblockdevs.com/blog/llm-structured-json-outputs-complete-guide-2026

## When this applies

- Any prompt where the response will be parsed programmatically.
- Categories: `data-extraction`, `classification`, `structured-data-generation`, plus anywhere `output_format` is a fixed schema.
- Cross-references: `references/meta/output-targets.md` Claude API row, `references/meta/managed-agents.md` (tool-use semantics).

## Sources

- https://claudeapi.com/en/blog/dev-guides/claude-structured-outputs-json-schema-guide-2026/
- https://unblockdevs.com/blog/llm-structured-json-outputs-complete-guide-2026
