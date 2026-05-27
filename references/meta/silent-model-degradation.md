# Silent model degradation — don't bake exact behavioral assumptions

Cross-cutting reference for any prompt that depends on a specific behavior pattern of a named model version.

## Why this exists

Model behavior can change materially under a stable model label without any version-string change. Anthropic's own April 2026 postmortem confirms three independent serving-side changes during March–April 2026 — a default-effort downgrade (March 4), a broken cache-thinking eviction (March 26), and a verbosity cap (April 16) — that each silently degraded Claude Code quality. Users observed the drift before Anthropic acknowledged it. Prompts that bake exact behavioral assumptions ("the model will always preserve thinking blocks", "Opus 4.6 always returns 3 paragraphs") are fragile against these silent changes. Source: https://www.anthropic.com/engineering/april-23-postmortem

## Practical rules

**Anti-pattern: behavioral assumption baked into prompt prose.**

Bad:
- "You will preserve all `<thinking>` blocks unchanged."
- "You always respond in exactly 3 paragraphs."
- "Opus 4.6 returns markdown by default, so do not specify format."

Good:
- "Preserve `<thinking>` blocks unchanged" (instruction, not assumption).
- "Respond in 3 paragraphs" (instruction, not assumption).
- "Return markdown" (instruction; do not rely on the model's default).

The prompt states what the model should do; it does not assert what the model will do.

**Anti-pattern: hardcoded model-version assumptions.**

If the prompt says "this works because Opus 4.6 has 8K thinking budget by default," that assumption breaks the moment serving-side changes update the default. State the budget you want explicitly via API parameters; do not depend on defaults.

**Behavior-eval canary pattern:**

For any prompt that runs at scale, pair it with a behavior-eval suite that runs nightly against a small held-out set. When the eval drifts, the prompt may need re-tuning even though the model version did not change. Cross-ref `references/meta/eval-harness-2026.md`.

**Surface uncertainty in the prompt itself.**

When a behavioral assumption is load-bearing, surface it in the assumptions list:

```
- Assumes Opus 4.7 default thinking is adaptive [inferred from API docs 2026-04-16; verify if model version changes]
```

So the user (and a future reader) can verify.

## When this applies

- Any prompt the user identifies as "production," "long-lived," or "I want this to keep working."
- Cross-references: `references/meta/eval-harness-2026.md` (canary suite), `references/meta/anthropic-opus-4-7-changes.md` (model-specific shifts), `references/meta/anti-patterns.md`.

## Sources

- https://www.anthropic.com/engineering/april-23-postmortem
- https://www.reddit.com/r/ClaudeCode/comments/1t2uur9/even_opus_46_sucks_now/
