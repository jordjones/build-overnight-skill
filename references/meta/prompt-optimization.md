# Prompt optimization — DSPy + GEPA as the 2026 default stack

Cross-cutting reference for any prompt that will run at scale or be optimized programmatically. The build-prompt skill hand-tunes individual prompts; this file is the referral path when the user wants automatic optimization.

## Why this exists

The 2026 optimizer landscape consolidated around DSPy + GEPA. GEPA (Genetic-Pareto reflective prompt evolution, ICLR 2026 Oral, Agrawal/Khattab et al.) is now a first-class DSPy optimizer and beats GRPO by 6–19 percentage points across six benchmarks while using up to 35× fewer rollouts. The production playbook for a prompt that runs at scale is no longer "hand-tune in build-prompt" — it is "wrap in DSPy module, optimize with GEPA, deploy." Source: https://llm-stats.com/blog/research/fine-tuning-vs-prompt-engineering-2026

## Practical rules

**Decision rule — when to refer users to DSPy + GEPA:**

| Prompt characteristic | Path |
|---|---|
| One-shot, ad-hoc | Hand-tune in build-prompt; no optimizer |
| Repeated < 100 invocations/week | Hand-tune in build-prompt; no optimizer |
| Repeated at scale with measurable success metric | Wrap in DSPy module → optimize with `dspy.GEPA` → deploy |
| Repeated at scale without a success metric | Define a metric first; do not optimize blind |

**Optimizer landscape (compact):**

- **APE (2022)** — baseline; useful as a sanity check, not for production.
- **OPRO (2023)** — deprecated for serious work in 2026; GEPA dominates on the same benchmarks.
- **MIPROv2** — Bayesian over instructions + few-shot demonstrations; still relevant when GEPA's reflective mutation does not converge.
- **GEPA (2026 default)** — reflective prompt evolution, Pareto-frontier search, ICLR Oral. `dspy.GEPA` and `mlflow.genai.optimize_prompts` ship with it.

**Production playbook:**

1. Write the candidate prompt with build-prompt (this skill).
2. Wrap in a DSPy module with the success metric.
3. Run `dspy.GEPA` against a held-out eval set.
4. Compare against the hand-tuned baseline; only deploy if the optimized version beats baseline on the metric.
5. Re-run optimization when the base model changes (Opus 4.7 → 4.8, etc.).

**Anti-pattern:** running an optimizer without a metric. GEPA needs a Pareto frontier; "make it better" is not a metric.

## When this applies

- Any prompt the user says will be "production," "at scale," or "run many times."
- Cross-references: `references/meta/eval-harness-2026.md` (Pareto frontier comes from eval suites), `references/style-guide.md` (the hand-tuned baseline is what optimizers improve on).

## Sources

- https://llm-stats.com/blog/research/fine-tuning-vs-prompt-engineering-2026
- ICLR 2026 GEPA paper (Agrawal, Khattab, et al.)
