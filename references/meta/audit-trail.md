# Audit trail

The `.overnight/<run-id>/` directory specification. Every overnight run produces one. Audit-only in v1 (NOT consulted on resume per Reconciler 2).

## Directory layout

```
.overnight/
└── <run-id>/                           # e.g. 20260527T080000Z-a3f2c1
    ├── MANIFEST.json                   # run metadata (wrapper writes at start)
    ├── PROMPT.md                       # verbatim dispatched prompt (skill writes at draft-deliver)
    ├── PRD.md                          # frozen goal (copied from interview)
    ├── PLAN.md                         # initial decomposition
    ├── STATE.md                        # latest state snapshot (agent rewrites each checkpoint)
    ├── BACKLOG.md                      # out-of-scope and deferred items (agent appends)
    ├── events.jsonl                    # append-only event journal
    ├── state.json                      # thin metadata: run_id, latest_checkpoint_tag, MA session ID
    ├── COST.json                       # cumulative cost + cache-hit rates
    ├── FINAL_REPORT.md                 # OVERNIGHT_RUN_REPORT.md when why_stopped=DONE
    ├── FAILURE.md                      # written when why_stopped != DONE
    ├── git-reflog-snapshot.txt         # entry-point recovery
    └── artifacts/                      # screenshots, diffs, etc.
```

## MANIFEST.json schema

Written once at run start by `bin/build-overnight-run`:

```json
{
  "run_id": "20260527T080000Z-a3f2c1",
  "runtime": "ralph",
  "category": "test-coverage-overnight",
  "started_at": "2026-05-27T08:00:00Z",
  "repo_root": "/Users/.../overnight-worktrees/...",
  "host": "Jordan-MacBook-Pro.local",
  "user": "jordanjones",
  "build_overnight_version": "v1.0.0-rc2",
  "model": "claude-opus-4-7",
  "billing_mode": "direct-api",
  "budget_hours": 8,
  "cost_ceiling_usd": 40,
  "iteration_cap": 200
}
```

**`billing_mode` is one of `direct-api` or `oauth-subscription`** (rc2). Wrapper detects from `ANTHROPIC_API_KEY` presence at preflight; user override per `bin/build-overnight-run` env var `OVERNIGHT_BILLING_MODE`. Under `oauth-subscription`, `cost_ceiling_usd` is recorded as `null` (and **never enforced** by the loop); `iteration_cap` becomes the primary budget gate.

## events.jsonl schema

Append-only, one event per line. Every event has `ts`, `run_id`, `kind`. Per-kind additional fields:

| kind | additional fields |
|---|---|
| `run_started` | `runtime`, `repo` |
| `iteration_complete` | `iteration`, `commit_sha`, `diff_stat`, `test_exit_code`, `cost_usd_iter`, `cost_usd_total` |
| `checkpoint` | `tag`, `commit_sha`, `elapsed_hours` |
| `llm_call` | `iteration`, `model`, `input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `output_tokens`, `cost_usd`, `cache_hit_rate` |
| `tool_call` | `iteration`, `tool`, `duration_ms`, `success` |
| `out_of_scope_edit` | `iteration`, `path`, `reason`, `appended_to_backlog` |
| `drift_probe` | `iteration`, `drift_score` (1-5 from LLM judge), `verdict` |
| `cache_anomaly` | `iteration`, `cache_hit_rate`, `prior_hit_rate`, `hypothesis` |
| `oscillation_detected` | `iteration`, `state_A_sha`, `state_B_sha`, `cycle_count` |
| `ship_mode_entered` | `reason` (soft_cap_time / soft_cap_cost / drift_limit) |
| `hard_cap_breached` | `kind_breached` (time/cost/drift), `value_at_breach` |
| `awaiting_completion` | (no extra fields; wrapper-emitted) |
| `run_completed` | `why_stopped`, `final_cost_usd`, `final_wall_minutes`, `commits`, `pr_url` |
| `run_aborted` | `why_aborted`, `last_good_tag` |
| `dry_run_exit` | (no extra fields) |

Events are written by the agent itself (via shell-out from inside the loop) plus the wrapper for `run_started`, `awaiting_completion`, `dry_run_exit`, and the trap-fired exit event.

## state.json schema

Thin metadata file (NOT resume source-of-truth in v1):

```json
{
  "run_id": "20260527T080000Z-a3f2c1",
  "latest_checkpoint_tag": "overnight/20260527T080000Z-a3f2c1/ckpt-h3",
  "latest_commit_sha": "f1a2b3c4...",
  "iterations_completed": 47,
  "ship_mode_active": false,
  "managed_agents_session_id": null,
  "updated_at": "2026-05-27T11:00:00Z"
}
```

If `runtime=managed-agents`, `managed_agents_session_id` is set to the Anthropic session UUID. Used for provenance and morning-review linking, NOT for resume — resume happens via the Anthropic SDK's implicit `wake()`.

## COST.json schema

Rolling budget summary, regenerated at each checkpoint. **The shape is mode-conditional (rc2)**.

### Direct-api mode

```json
{
  "billing_mode": "direct-api",
  "cumulative_cost_usd": 12.47,
  "cost_ceiling_usd": 40,
  "soft_cap_usd": 32,
  "iterations_costed": 47,
  "iteration_cap": 200,
  "iteration_soft_cap": 160,
  "model_mix": {"claude-opus-4-7": 0.85, "claude-haiku-4-5-20251001": 0.15},
  "cache_hit_rate_overall": 0.83,
  "cache_writes_usd": 2.10,
  "cache_reads_usd": 0.95,
  "net_cache_savings_usd": 24.30,
  "top_5_expensive_iterations": [
    {"iteration": 12, "cost_usd": 1.82, "reason": "context_compaction"}
  ]
}
```

### OAuth-subscription mode

```json
{
  "billing_mode": "oauth-subscription",
  "cumulative_cost_usd": null,
  "cost_ceiling_usd": null,
  "soft_cap_usd": null,
  "iterations_completed": 47,
  "iteration_cap": 200,
  "iteration_soft_cap": 160,
  "wall_clock_elapsed_minutes": 154,
  "wall_clock_soft_cap_minutes": 432,
  "wall_clock_hard_cap_minutes": 480,
  "model_mix": {"claude-opus-4-7": 0.85, "claude-haiku-4-5-20251001": 0.15},
  "cache_hit_rate_overall": 0.83,
  "cache_anomalies_count": 1,
  "top_5_slowest_iterations": [
    {"iteration": 12, "wall_seconds": 187, "reason": "context_compaction"}
  ]
}
```

⚠️ **Phantom-USD warning:** under `oauth-subscription`, ALL `*_usd` fields MUST be `null`. The agent does NOT compute phantom dollars from list prices and `response.usage`. Any tool that surfaces a non-null USD value under subscription mode is wrong and should be reported as a bug. The `<cost_ceiling_usd mode="subscription_disabled">` clause in the drafted prompt forbids the agent from doing this computation; the wrapper enforces it on the telemetry side. See `references/meta/budget-and-telemetry.md` and `~/.claude/plans/jiggly-marinating-parnas-rc2-audit.md` §A.2 for the failure-mode reproduction this prevents.

## Resume-from-tag protocol (default)

On any non-clean exit (`why_stopped != DONE`):

```bash
RUN_ID=...
# Find the latest checkpoint tag for this run.
LAST_TAG=$(git tag --list "overnight/$RUN_ID/ckpt-h*" | sort -V | tail -1)
# Reset the worktree to that tag.
git reset --hard "$LAST_TAG"
# Re-read PRD.md, PLAN.md, STATE.md, BACKLOG.md.
# Replay from the story marker recorded in STATE.md.
```

events.jsonl is NOT consulted; it's audit-only. The reasoning: events.jsonl can be partially written mid-event during a crash; trusting it for replay risks re-executing destructive side-effects whose completion was never logged. git tags are atomic — either the tag exists or it doesn't.

## Privacy and retention

`.overnight/<run-id>/` is gitignored. The user decides per-run what to keep. Default retention pattern (manual, post-morning-review):

```bash
# Keep last 10 runs, discard older
ls -t ~/path/.overnight/ | tail -n +11 | xargs -I{} rm -rf "~/path/.overnight/{}"
```

Cost telemetry that the user wants to aggregate goes into `library/cost-benchmarks.md` (opt-in, populated post-v1).

## What the audit trail is NOT for

- It's NOT a real-time dashboard. Helicone or the agent's own surface is for that.
- It's NOT a substitute for the PR — the PR is the human-facing handoff per F29.
- It's NOT a substitute for git history — the git log + reflog tells the canonical story.
- It's NOT consulted on resume in v1 — git tags are.
