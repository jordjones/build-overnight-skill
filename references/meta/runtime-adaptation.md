# Runtime adaptation

How the universal scaffold's 14 clauses adapt per runtime. Source: R7 + Reconciler 3.

## 3 first-class runtime variants

| Runtime | When to use | Default? |
|---|---|---|
| `ralph` | Default for laptop; PRD-driven self-loop; zero marginal cost | **Yes (v1 default per Q5)** |
| `managed-agents` | Long idle periods OK, cross-iteration memory critical, OK paying $0.08/session-hour | No (opt-in via interview) |
| `continuous-claude` | Time-bounded sequential pipelines, explicit `--max-duration` wrapper | No (opt-in) |

## 3 documented as "ralph variant with adjustments"

| Runtime | Differs from ralph by |
|---|---|
| `ralphthon` | Adds hardening waves (phase machine: interview → execution → hardening → complete); ralphthon-prd.json state |
| `ralph-loop` | Lightest primitive (Stop-hook self-loop); iteration-bounded only; no PRD discipline |
| `claude-p-chain` | Pure bash chain of `claude -p` calls; no LLM in the driver loop; SHARED_TASK_NOTES.md bridge |

## Universal clauses (C1–C14) emit unchanged across all runtimes

All 14 mandatory clauses from `references/scaffold/universal.md` are emitted verbatim regardless of runtime. Defaults bound to user-confirmed values (8h, $40, etc.).

The runtime variance is concentrated in exactly **4 slots**.

## 4 varying clause slots

| Slot | What it controls | Why it varies |
|---|---|---|
| `<execution>` | How the agent's run-loop is invoked and iterated | Each runtime has a different "outer loop" |
| `<persistence>` | Where session state lives across iterations and across crashes | Native session vs filesystem |
| `<completion>` | How the agent signals "done" | Different completion conventions |
| `<parallelism>` | Whether sub-agents are available, depth limits | Native multiagent vs single-loop |

## The 3×4 variant table

### `<execution>` slot

| Runtime | Rendered text in prompt |
|---|---|
| `managed-agents` | "You run as a session inside Anthropic's Managed Agents runtime. Each `user.message` event wakes you. Stay focused — your container persists between wakes (30-day retention). To pause, ensure your last assistant turn ends with `stop_reason: end_turn` so the session becomes `idle`." |
| `ralph` | "You run inside the OMC ralph loop. Each iteration the Stop hook re-invokes you with the same PRD. Read `STATE.md` first to determine which story to pick up. Use `prd.json` to mark story status. End iteration with `echo RALPH_DONE` once all stories pass." |
| `continuous-claude` | "You are driven by `continuous-claude --max-duration <H>h`. Each iteration is one `claude -p` call. The driver loop checks the timer between iterations. Append your work to `SHARED_TASK_NOTES.md` so the next iteration sees it. Use `STATE.md` for canonical state." |

### `<persistence>` slot

| Runtime | Rendered text in prompt |
|---|---|
| `managed-agents` | "Use the Managed Agents native memory store. Write to memory at every checkpoint with key `checkpoint-h<N>`. The container filesystem persists across wakes — `.overnight/<run-id>/` lives there. DO NOT duplicate state in `state.json`; defer to the session's event log." |
| `ralph` | "`.overnight/<run-id>/` is ground truth, alongside git tags. Write `STATE.md` at each checkpoint. Commit + tag (`overnight/<run-id>/ckpt-h<N>`) at every iteration boundary. On crash, the next ralph invocation reads `STATE.md` and the latest tag." |
| `continuous-claude` | "`.overnight/<run-id>/` + `SHARED_TASK_NOTES.md` are ground truth. Git tags at each iteration boundary. Treat `events.jsonl` as audit-only. On `--max-duration` timeout, the driver kills you; the trap in `bin/build-overnight-run` writes `FAILURE.md`." |

### `<completion>` slot

| Runtime | Rendered text in prompt |
|---|---|
| `managed-agents` | "Signal completion by ending your final assistant turn with `stop_reason: end_turn`. The session transitions to `idle`. The `session.status_idled` webhook fires; do NOT long-poll. Write `FINAL_REPORT.md` and open the PR BEFORE the final turn." |
| `ralph` | "Signal completion by emitting `echo RALPH_DONE` AFTER you have: (1) written `FINAL_REPORT.md`, (2) committed and tagged the last good state, (3) pushed the branch, (4) opened the draft PR. The Stop hook will not re-invoke you once it sees the sentinel." |
| `continuous-claude` | "Signal completion by writing `STATUS=DONE` to `.overnight/<run-id>/status.txt` AFTER you have: (1) written `FINAL_REPORT.md`, (2) committed and tagged, (3) pushed, (4) opened the draft PR. The driver loop checks `status.txt` between iterations and exits cleanly when it sees DONE." |

### `<parallelism>` slot

| Runtime | Rendered text in prompt |
|---|---|
| `managed-agents` | "You may spawn child sub-agents via the native multiagent API (depth-1, max 20-roster, max 25 concurrent threads). Use sub-agents for: parallel test runs, parallel docs generation, parallel research subqueries. DO NOT use them to amplify a task that should be sequential. Cost attribution flows to your parent session." |
| `ralph` | "You run as a single sequential loop. Spawn sub-agents only via the OMC `ultrawork` skill, and only for explicit fan-out tasks (e.g., 'run these 5 fixture tests in parallel'). Default: sequential." |
| `continuous-claude` | "You run as a single sequential `claude -p` call per iteration. No sub-agents within a call. If parallelism is genuinely needed, restructure the work into multiple sequential iterations." |

## Suppression rule for Managed Agents (F33)

When `runtime=managed-agents`, the universal scaffold's clauses C6 and parts of C7 are partially redundant with the native session store. v1 still emits them verbatim (per Conflict #6 resolution: "equal-among-N with capability-profile-driven default"). v1.1 may auto-suppress.

## Capability-profile → runtime suggestion

The SKILL.md interview Step 5 asks the user for the runtime. To suggest a default, match the category's `capability_profile` block:

| capability_profile field | If TRUE → suggest |
|---|---|
| `needs_cross_iteration_memory: true` | `managed-agents` |
| `expected_idle_periods: long` (>30 min) | `managed-agents` |
| `needs_parallel_subagents: true` | `managed-agents` |
| `budget_hours_typical: <= 2` | `continuous-claude` |
| `destructive_operations: rare` AND none of the above | `ralph` (v1 default) |
| all else | `ralph` (v1 default per Q5) |

The interview question:

```
Step 5 — Which runtime?
   1. ralph (default; zero marginal cost, local Claude Code self-loop)
   2. managed-agents (Anthropic hosted, $0.08/session-hour, native memory + resume)
   3. continuous-claude (time-bounded with --max-duration)
   4. other (ralphthon / ralph-loop / claude-p-chain — adapt from ralph)
Default: <suggestion from capability_profile>
```

## What to do if the user picks "other"

Render with the ralph variant text, plus an appendix note:

```
> Note: you selected <ralphthon|ralph-loop|claude-p-chain>. This variant
> adapts from `ralph` with these adjustments:
> - <ralphthon: phase machine, hardening waves>
> - <ralph-loop: Stop-hook only, iteration cap, no PRD>
> - <claude-p-chain: no LLM in driver, SHARED_TASK_NOTES bridge>
> See `references/meta/overnight-loop-mechanics.md` for the runtime details.
```
