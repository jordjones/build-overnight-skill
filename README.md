# build-overnight

User-invoked Claude Code skill that turns rough overnight-loop goals into prompts engineered to drive **autonomous unattended LLM agent loops** over a fixed wall-clock budget (default 8h, default $40 hard cost ceiling).

Sibling skill to [build-prompt](https://github.com/jordjones/build-prompt-skill). Where `build-prompt` produces one-shot polished prompts, `build-overnight` produces prompts engineered for unattended runs — with hard cost ceilings, drift detection, structured progress proof, graceful ship-mode on soft caps, and PR-as-handoff morning review.

## Status

**v1.0.0-rc2** (2026-05-27). rc2 adds billing-mode correctness: clause C1 `<cost_ceiling_usd>` is now mode-conditional; the new C15 `<iteration_budget>` becomes the primary stop-on-budget gate under Claude Code OAuth / Codex CLI subscriptions. Total universal clauses: **15** (was 14). The 20/20 Layer 1 + 3/3 Layer 2 classification suite is green, both modes are exercised. Final `v1.0.0` tag (no `-rc`) still gated on **one successful real overnight run** through the skill.

## Billing modes

- **`direct-api`** — `ANTHROPIC_API_KEY` set; the agent reads `response.usage` and enforces a USD cost ceiling. Default $40 hard / $32 soft.
- **`oauth-subscription`** — Claude Code Pro/Max or Codex CLI; flat-rate billing. USD ceiling is structurally unavailable inside the loop, so the agent uses C15 iteration cap (default 200 hard / 160 soft) + C2 wall-clock (default 8h / 7.2h) instead. No phantom USD surfaces in reports. See `references/meta/budget-and-telemetry.md`.

## Usage

```
/build-overnight <rough overnight goal>
```

Examples:
- `/build-overnight raise branch coverage on src/auth to 90% overnight`
- `/build-overnight hunt the root cause of test_pro_rated_refund flake`
- `/build-overnight build SSO per docs/prd-sso.md, 8h ralph`
- `/build-overnight rename UserService to AccountService across src/`
- `/build-overnight add google-style docstrings to every public function in src/api/v2`
- `/build-overnight research 2026 best practices for LLM agent retry policies`

The skill runs a 7-step interview, classifies the goal into one of 6 categories, asks targeted questions including the runtime (ralph / managed-agents / continuous-claude / …), and drafts a prompt that emits a 14-clause `<overnight_contract>` plus category-specific mitigation clauses.

## Categories (6 in v1)

| Category | Goal |
|---|---|
| `test-coverage-overnight` | Raise meaningful coverage (mutation/branch/fixture gated) |
| `bug-hunt-overnight` | Drive a failing test or repro to green with root-cause tracking |
| `feature-build-overnight` | Implement a feature from a PRD with acceptance criteria |
| `refactor-sweep-overnight` | Mechanical refactor with behavior-preservation invariants |
| `docs-pass-overnight` | Docstrings / docs with no-hallucinated-signatures gate |
| `research-deep-overnight` | Long-horizon research with source-fabrication refuse |

Four more (`dep-upgrade`, `cleanup-deslop`, `data-pipeline-build`, `eval-harness-build`) are cut from v1 — documented in `library/future-work.md` with revive-conditions.

## Runtimes

3 first-class variants in `references/meta/runtime-adaptation.md`:
- **ralph** (default; zero marginal cost; local Claude Code self-loop)
- **managed-agents** (Anthropic hosted, $0.08/session-hour)
- **continuous-claude** (time-bounded with `--max-duration`)

3 documented as "ralph variant with adjustments": ralphthon, ralph-loop, claude-p-chain.

## The 14 mandatory universal clauses

Every drafted prompt emits these in an `<overnight_contract>` block regardless of category. See `references/scaffold/universal.md` for the full template.

C1 cost ceiling · C2 time budget · C3 progress proof · C4 drift detection · C5 no test weakening · C6 externalized state · C7 partial credit handoff · C8 worker/judge separation · C9 read-only/write scope · C10 destructive command policy · C11 git remote policy · C12 credential scope · C13 secret scan gate · C14 cache warming strategy.

## Wrapper script

`bin/build-overnight-run <run-id> <runtime>` does preflight (caffeinate, AC, gh auth, disk, model pin), acquires a lockfile, creates `.overnight/<run-id>/`, and tees JSONL telemetry. Tier-1 worktree mandatory (`~/overnight-worktrees/<run-id>/`).

## Tests

```bash
# Layer 1 (static + coherence, $0):
uv run build-overnight-research/test_skill.py

# Layer 1 + Layer 2 (classification check + opt-in Sonnet judge with ANTHROPIC_API_KEY):
uv run build-overnight-research/test_skill.py --layer2

# Layer 1 + URL liveness:
uv run build-overnight-research/test_skill.py --check-urls
```

Layer 3 (real-run fixture repos) deferred to v1.1 as separate `build-overnight-fixtures/` repo.

## Provenance

- Adapted from [build-prompt](https://github.com/jordjones/build-prompt-skill) v2 (2026-05-26 refresh).
- Designed via a multi-round adversarial + research convention: 4 adversarial voices (Skeptic, Operator, Safety Reviewer, Eval Engineer) + 7 research agents (external ecosystem, real-world failure modes, cost/observability, durable execution, morning-review UX, eval methodology, Anthropic Managed Agents) → 35 convergent findings + 10 resolved conflicts + 3 reconciliations + 1 synthesis.
- Convention artifacts at `~/.claude/plans/jiggly-marinating-parnas-convention/`.
- Plan of record: `~/.claude/plans/jiggly-marinating-parnas.md`.

## License

See [LICENSE](LICENSE).
