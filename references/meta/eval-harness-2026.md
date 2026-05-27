# Eval-harness landscape (2026)

Cross-cutting reference for prompts whose target is an eval harness, or prompts that the user will optimize with a harness later.

## Why this exists

The 2026 eval-harness market consolidated and bifurcated simultaneously. Three patterns dominate; users planning multi-vendor evals must disclose vendor alignment to avoid lock-in. The skill's `output-targets.md` row for `Eval harness` used to treat all harnesses as one target; that is no longer accurate. Sources: https://www.digitalapplied.com/blog/ai-agent-eval-frameworks-testing-guide-2026 and https://www.augmentcode.com/tools/best-ai-agent-evaluation-tools

## Practical rules

**Three-layer eval pattern (recommended stack):**

| Layer | Purpose | Recommended tool |
|---|---|---|
| 1. CLI gate | Regression suite that runs on PR / CI | Promptfoo (now OpenAI-owned) |
| 2. Production tracing | Per-call traces with cost + quality scores | Braintrust (vendor-neutral) or LangSmith |
| 3. Safety / governance | Pre-release safety-grade test suite | Inspect AI (UK AISI) |

Teams running prompts at scale should stack at least two layers (CLI + tracing).

**Vendor alignment (May 2026):**

| Tool | Alignment | Notes |
|---|---|---|
| Promptfoo | OpenAI-aligned | Acquired 2026-03-09, still closing |
| LangSmith | LangChain-aligned | Bundled with LangChain platform |
| Braintrust | Vendor-neutral | $80M Series B Feb 2026 |
| Inspect AI | UK AISI | Governance / safety-grade |
| DeepEval | Vendor-neutral | Lightweight, Python-native |

**Decision rule:** users planning multi-vendor evaluations should prefer neutral harnesses (Braintrust, Inspect AI, DeepEval). Vendor-aligned harnesses are fine for single-vendor pipelines.

**Prompt-format implications:**

- Eval-harness prompts need deterministic output formats (XML or JSON schema). Cross-ref `references/meta/output-targets.md` Eval harness row.
- Prompts going through Promptfoo CLI regression should use `{{INPUT}}` / `{{EXPECTED_OUTPUT}}` placeholders for per-row substitution.

## When this applies

- Any prompt the user identifies as "going into an eval suite" or "I want to test this against a dataset."
- Cross-references: `references/meta/prompt-optimization.md` (optimizers consume eval scores), `references/meta/output-targets.md` Eval harness row.

## Sources

- https://www.digitalapplied.com/blog/ai-agent-eval-frameworks-testing-guide-2026
- https://www.augmentcode.com/tools/best-ai-agent-evaluation-tools
