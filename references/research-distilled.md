# Research distilled — primary substrate for build-overnight

Replaces what was originally a 50-item `build-overnight-research/` substrate. The convention itself produced the substrate; this file summarizes and cites it.

**Primary sources** (all at `~/.claude/plans/jiggly-marinating-parnas-convention/`): 4 adversarial reports (`01-skeptic`, `02-operator`, `03-safety`, `04-eval-engineer`) + 7 research reports (`R1-ecosystem-2026`, `R2-failure-modes`, `R3-cost-observability`, `R4-durable-execution`, `R5-morning-ux`, `R6-eval-methodology`, `R7-managed-agents`). Round 1 orchestrator outputs: `CONVERGENT_FINDINGS.md` (35 findings), `CONFLICTS.md`, `QUESTIONS.md`. Round 2 reconcilers: `RECONCILER-{01,02,03}-*.md`. Final synthesis: `SYNTHESIS.md`.

## The 14 items that shape every drafted prompt

| # | Distilled finding | Convention source | Realized as |
|---|---|---|---|
| D1 | Hard cost ceiling with soft (80%) ship-mode trigger is mandatory; "$400 overnight bill" and Uber-$1.2M-burn are documented incidents | F1; R2 (mode #3); R3 §2; Operator §3; Safety §3 | Clause C1 in `references/scaffold/universal.md` |
| D2 | Wall-clock budget with self-extension forbidden; no runtime exposes `--max-duration` natively as of 2026-05-27 | F2; R1 §3; R3 §3; R5 §6; R7 §3 | Clause C2 + `<time_budget>` runtime variants in `runtime-adaptation.md` |
| D3 | Verifiable progress proof (commit SHA + diff stat + raw test output) prevents the Devin "3 of 20 tasks done" hallucinated-completion pattern | F3; R2 (mode #2); R5 §5 (trust signals); Eval §4 | Clause C3 |
| D4 | Drift detection via scope manifest + out-of-scope cap + PRD re-read; arXiv 2505.02709 Goal Drift Score is the canonical method | F4; R2 (mode #3); R6 §6; Operator §3 | Clause C4 + per-iteration LLM-judge drift probe |
| D5 | Forbid test weakening as a hard pre-commit gate (no `pytest.skip`, `xfail`, deleted tests, mocked SUT, hardcoded outputs) | F5; R2 (mode #5); Operator §3 | Clause C5 |
| D6 | Externalized PRD/PLAN/STATE triad re-read every iteration beats relying on context summary — compaction-induced fidelity loss (Osmani) accelerates drift | F6; R1 §6 (file-based state); R2 (mode #7); R4 §2 | Clause C6 |
| D7 | Structured handoff with `why_stopped` enum + `resume_command` is universal across Devin/Cursor/Codex/MA but no canonical schema exists — opportunity for build-overnight to prescribe one | F7; R1 §4 (partial-credit gap); R5 §3 (failure handoff); R6 §5 (partial credit) | Clause C7 + `FAILURE.md` template in `morning-review-artifact.md` |
| D8 | Writer/verifier separation (Planner→Worker→Judge) is the converged 2026 shape; same-context self-approval drifts | F8; R1 §7 (converged shape); R6 §7 (Layer 2 judge); CLAUDE.md `<execution_protocols>` | Clause C8 + Layer 2 Sonnet judge in test harness |
| D9 | Tier-1 git-worktree sandbox under `~/overnight-worktrees/<run-id>/` is the minimum-viable isolation; devcontainer is Tier-2 documented but optional in v1 | F23; Safety §5; Operator §6; R2 (mode #11 — Replit $1M DB drop) | Clause C9 + `<write_scope>` + wrapper enforces worktree path |
| D10 | Destructive-command policy (forbid force-push, rm -rf outside worktree, `gh pr merge`, prod-DB writes) prevents the Replit-class incidents | F11; R2 (mode #11); Safety §3; hookify rules in `~/.claude/rules/` | Clauses C10 + C11 + reuses hookify enforcement |
| D11 | PR-as-handoff is the universal morning artifact: `overnight/<run-id>-<slug>` branch, draft state, `[OVERNIGHT]` prefix, `overnight-run` label, never auto-merge | F29; R5 §1, §2; R1 §5 | Clause C11 + `morning-review-artifact.md` PR-body template |
| D12 | Credential scope (scrub `*PROD*`, `AWS_*`, `STRIPE_*`, `SUPABASE_SERVICE_*`) gates the agent from prod blast-radius | F31; Safety §3; project memory (Jordan's stack) | Clauses C12 + C13 |
| D13 | Prompt-cache hygiene (no timestamps in system prompt, no mid-run model swaps, ≥80% hit target) drives 5× cost delta on 8h loops per arXiv 2601.06007v2 | F27; R3 §3 (cache TTL 5min/1h-extended; $50–100 uncached vs $10–19 cached) | Clause C14 + `cost-and-telemetry.md` cache-hit measurement |
| D14 | `.overnight/<run-id>/` directory layout is the converged audit/telemetry surface; `events.jsonl` is audit-only in v1 (NOT resume source per Reconciler 2) | F21; R4 §2; R5 §1; Reconciler 2 §"Proposed resolution" | `audit-trail.md` spec + `bin/build-overnight-run` writes there |

## Runtime landscape (R1, R4, R7)

Three first-class runtimes shipped in v1's `runtime-adaptation.md`:

- **Anthropic Managed Agents** — public beta GA 2026-04-08, $0.08/session-hour + token costs. Session event log, implicit `wake()` on `user.message` to idle session, 30-day container persistence. No native wall-clock cap (gap the prompt MUST teach). Multiagent depth-1, 20-roster, 25 concurrent threads. (R7)
- **OMC ralph** — PRD-driven self-loop with reviewer gate and hardening waves. State persists in `prd.json` + `progress.txt`. Resume via story-level PRD. Zero marginal cost beyond model usage.
- **Continuous Claude / `claude -p` chain** — bash-wrapped iteration with `--max-duration 8h`. Cron/SDK driver. `SHARED_TASK_NOTES.md` bridges iterations.

Three documented as "ralph variant with adjustments": ralphthon (hardening waves), ralph-loop (Stop-hook self-loop), claude-p-chain (sequential pipeline).

## Failure-mode taxonomy (R2 — 15 modes, 54 citations)

Each universal clause maps to one or more documented incident category:

- Cost blowouts → C1, C14 (R2 mode #3: $12K Kubernetes loop, Uber $1.2M, "$400 Overnight Bill")
- Hallucinated completion → C3, C8 (R2 mode #2: Devin 3/20 tasks; ClawForge benchmark; Anthropic 3.7 reward-hacking system card)
- Goal drift → C4, C6 (R2 mode #3; arXiv 2505.02709; Addy Osmani compaction-fidelity)
- Test gaming → C5, C8 (R2 mode #5: EvilGenie + METR; Anthropic 3.7 self-disclosure)
- External-system damage → C9–C13 (R2 mode #11: Replit $1M DB drop; PocketOS/Cursor/Opus 9-second prod wipe; Codex Cloud Windows incident)
- Model degradation mid-run → C14 + monitoring (R2 mode #13: Anthropic Aug–Sep 2025 three-bug postmortem)
- Resume failures → Reconciler 2 → git-tag default (R2 mode #15 — under-reported, Reddit-only; chose conservative path)

## Eval methodology (R6 — METR/SWE-Bench Pro/RE-Bench)

- v1 ships Layer 1 (static + coherence parser, $0/commit) + thin Layer 2 (3 fixtures + Sonnet judge, ~$0.50–1/PR).
- Layer 3 (real-run fixture repos with continuous 0–1 scoring + pass@k/pass^k) deferred to v1.1 as separate `build-overnight-fixtures/` repo.
- 4 rubric dimensions on Layer 2: **Overnight Discipline** (composite of time/checkpoint/termination clause coherence), **Drift Resistance**, **Safety Posture**, **Verifiable Completion**. Each scored 1–5; pass at ≥4.

## Morning-review artifact (R5 — `OVERNIGHT_RUN_REPORT.md`)

Full template in `references/meta/morning-review-artifact.md`. Headline structure:
1. Run header (run-id, category, runtime, budget, actual cost, actual wall-clock)
2. Goal restatement (from PRD.md)
3. What shipped (commit list, files-touched, tests-status, recommendation field: SHIP/REVIEW/REVERT)
4. What did NOT ship (BACKLOG.md, blocked items, ambiguous items)
5. Drift events (out-of-scope edits logged, drift-score curve)
6. Cost burndown (per-iteration cost + cache-hit rate)
7. Trust signals (test output pasted, lint pass, screenshots if UI)
8. Uncertainty signals ([UNVERIFIED] markers, auto-downgrade triggers)
9. Resume command (if `why_stopped != DONE`)

## What the convention chose NOT to adopt for v1

- R4's full idempotency-keyed JSONL durable contract (relegated to opt-in advanced-mode appendix in `overnight-loop-mechanics.md`) — chosen because no documented laptop case of successful JSONL resume was found in the 54-citation R2 corpus.
- R7's "Managed Agents as primary runtime" framing (equal-among-three instead) — chosen because Jordan's documented setup leans local-tool-heavy.
- Eval's Layer 3 real-run fixtures (deferred to v1.1) — chosen because thin Layer 1+2 catches most regressions at ~zero marginal cost; Layer 3 ships once the skill is in real use.
- `dep-upgrade`, `cleanup-deslop`, `data-pipeline-build`, `eval-harness-build` categories (cut from v1, documented in `library/future-work.md`) — chosen because Safety+Operator flagged operational risk too high without more usage data.

All convention deliberations preserved at `~/.claude/plans/jiggly-marinating-parnas-convention/` for re-derivation in v1.1.
