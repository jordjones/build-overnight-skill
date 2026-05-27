# Test-time compute heuristics

Cross-cutting reference for any prompt that controls thinking budgets, effort levels, or test-time compute scaling.

## Why this exists

Reasoning models in 2026 expose a thinking budget / effort knob. The naive heuristic — turn it on and turn it up — drives inference cost up 5–10× without proportionate quality lift on most tasks. The practical heuristic is the opposite: default budget to 0, opt in by task type, cap per task class, cascade tiers. Source: https://idir-mellaz.fr/inference-scaling-test-time-compute-why-reasoning-models-raise-your-compute-bill-2/

## Practical rules

**The 4 routing questions** (decide before raising any budget):

1. **Verifiable?** Can the answer be checked against a deterministic oracle (test suite, schema, regex)? If no, raising the budget does not raise quality — it raises confidence.
2. **Interactive?** Is the user waiting in real time? Interactive flows cap at 2–6k thinking tokens; longer waits abandon.
3. **Error-cost?** Is a wrong answer expensive (production deploy, security audit)? Higher error-cost justifies higher budget.
4. **Novelty?** Is the input within the model's training distribution? Out-of-distribution inputs benefit more from raised budget than in-distribution ones.

If 3 of 4 lean low → keep budget at 0.

**Per-task-class budget table:**

| Task class | Thinking-budget range |
|---|---|
| Chat / autocomplete | 0 |
| Classification / extraction | 0 |
| Code generation (interactive) | 2k–6k |
| Code review / refactor | 4k–8k |
| Multi-file edit / migration | 8k–16k |
| Agentic planning | 8k–20k |
| Research-report synthesis | 16k–40k |
| Security audit | 16k–40k |

**Cascade pattern (Tier 1 / Tier 2 / Tier 3):**

For systems running prompts at scale, route 60–70% of traffic to Tier 1 (fast model, no thinking) and only escalate when Tier 1 abstains or fails a verifier. The cost savings dominate quality at scale.

**Anti-patterns:**

- Default `thinking_budget=high` on every prompt.
- Raising budget on a non-verifiable task ("write a friendlier email") — pure cost increase.
- Raising budget instead of fixing the prompt — overprompting often hides as overthinking.

## When this applies

- Any prompt with `target_mode: thinking` or `reasoning`.
- Cross-references: `references/meta/reasoning-model-prompting.md` (model-family control surfaces), `references/meta/anthropic-opus-4-7-changes.md` (Opus 4.7 effort levels), `references/meta/eval-harness-2026.md` (verifier for cascade).

## Sources

- https://idir-mellaz.fr/inference-scaling-test-time-compute-why-reasoning-models-raise-your-compute-bill-2/
