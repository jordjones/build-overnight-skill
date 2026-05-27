# Opus 4.7 prompt-rule changes (released 2026-04-16)

Cross-cutting reference for any prompt targeting Claude Opus 4.7. Opus 4.7 is a four-axis breaking change vs 4.6, not a version bump; prompts written for 4.6 may degrade silently on 4.7.

## Why this exists

The 4.6 → 4.7 transition changed prompt-cache key derivation, tool-use semantics, context economics, and compaction APIs. Each shift can silently degrade a 4.6-tuned prompt without surfacing an error. Authoring prompts for 4.7 requires understanding which 4.6 habits no longer hold. Source: https://www.digitalapplied.com/blog/claude-opus-4-6-to-4-7-migration-playbook-breaking-changes-2026

## Practical rules

**Four breaking axes:**

1. **Prompt-cache keys are re-derived.** 4.6 cache entries do not transfer; cache is more sensitive to byte-ordering and whitespace. Cached-prefix assembly must be byte-deterministic. Re-establish cache hits on 4.7 deliberately rather than assuming transfer.

2. **Tool use emits multiple parallel `tool_use` blocks per turn.** A 4.6 prompt that assumed one tool call per turn will mis-parse 4.7 output. Update the tool-use loop to iterate over all `tool_use` blocks in a single response.

3. **1M context is per-workload economics.** Cost scales differently for prompts that approach 1M tokens vs prompts that stay under 200K. Long-context prompts need explicit budget review; default to chunking under 200K when possible. Cross-ref `references/meta/output-targets.md` long-input rules.

4. **Compaction API replaces manual summarization.** 4.7 ships an explicit compaction API for long-running conversations; prompts that used to embed "summarize prior context" instructions should switch to the API call.

**Extended-thinking control (Opus 4.7-specific):**

- `thinking: {type: 'adaptive'}` is the only supported mode. Fixed `budget_tokens` returns HTTP 400.
- 5-level effort scale: `low / standard / high / xhigh / max`. (The 4.6 4-level scale is gone.)
- Default to `adaptive` for any reasoning/planning/coding/tool-use task.
- Effort by task tier: low (classification/extraction) → medium (short summaries) → high (multi-file edits) → xhigh/max (research synthesis, security audits).

**4.7 verbosity:**

- Stable output style across `text.verbosity={low,medium,high}`. Verbosity is a separate axis from thinking effort.

## When this applies

- Any prompt whose `model_target` is `claude-opus-4-7`.
- Cross-references: `references/meta/reasoning-model-prompting.md`, `references/meta/output-targets.md` Claude API row, `references/meta/test-time-compute.md`.

## Sources

- https://www.digitalapplied.com/blog/claude-opus-4-6-to-4-7-migration-playbook-breaking-changes-2026
- https://claudefa.st/blog/guide/development/opus-4-7-best-practices
