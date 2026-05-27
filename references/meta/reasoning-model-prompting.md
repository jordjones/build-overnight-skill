# Reasoning-model prompting (Opus 4.7 / GPT-5.5 / Gemini 3)

Reasoning-native models in 2026 punish 2023-era prompt scaffolding. This file is the cross-cutting reference any category file links to when the target mode is `reasoning` or `thinking`.

## Why this exists

The 2024–2025 prompt-engineering canon (chain-of-thought triggers, few-shot examples, self-consistency wrapping, least-to-most decomposition, skeleton-of-thought) prescribed reasoning paths to models that did not reason internally. Opus 4.7, GPT-5.5, and Gemini 3 execute multi-step reasoning internally; prescribing an external path now constrains the model toward a worse one or wastes tokens replaying steps the model already runs. The five classic techniques actively degrade reasoning-model output per PromptHub's 2026 study. Source: https://karozieminski.substack.com/p/ai-prompting-techniques-reasoning-models-2026

## Practical rules

- **State goal + constraints + success criteria. Stop there.** Skip few-shot examples for reasoning-class tasks; the example's path constrains the model.
- **Do not add "think step by step" or "reason carefully."** Raise the effort/thinking budget instead.
- **Do not self-consistency-wrap** (n-sample voting) for reasoning models — the internal reasoning already runs multiple paths.
- **Match control surface to the model family:**
  - **Opus 4.7:** `thinking: {type: 'adaptive'}` with a 5-level effort scale (`low / medium / high / xhigh / max`). Default to `adaptive`; raise effort to unlock more reasoning. Fixed `budget_tokens` returns HTTP 400. Source: https://claudefa.st/blog/guide/development/opus-4-7-best-practices
  - **GPT-5.5:** defaults to `effort=medium` with separate `text.verbosity` control. Start at `effort=low` and only raise when evals justify it. Source: https://www.webreactiva.com/blog/guia-prompt-opus-gpt
  - **Gemini 3:** `thinking_level` enum (`minimal / low / medium / high`). Replace prompt-side CoT with a higher `thinking_level`. Source: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-flash
- **Effort by task tier (Opus 4.7):**
  - `low` — classification, extraction, simple lookups
  - `medium` — short summaries, docs lookups, single-step refactors
  - `high` — multi-file edits, architectural review, debugging
  - `xhigh / max` — research-report synthesis, security audits, long-running planning

## When this applies

Linked from any category file whose `Model and effort guidance` section recommends `target_mode: thinking` or `reasoning`. Cross-references:
- `references/meta/anti-patterns.md` items R2, R5 (retired CoT triggers and few-shot for reasoning models)
- `references/meta/output-targets.md` GPT-5.5 / Gemini 3 / Claude API rows
- `references/meta/test-time-compute.md` for token-budget heuristics

## Sources

- https://www.webreactiva.com/blog/guia-prompt-opus-gpt
- https://karozieminski.substack.com/p/ai-prompting-techniques-reasoning-models-2026
- https://claudefa.st/blog/guide/development/opus-4-7-best-practices
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-flash
