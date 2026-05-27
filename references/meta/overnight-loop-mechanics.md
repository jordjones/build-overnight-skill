# Overnight loop mechanics

How autonomous unattended LLM agent loops actually work. Read before drafting any prompt that the user plans to leave running for hours.

## The brain / hands / session decoupling

The 2026 industry consensus (R1 across Devin, Cursor Background Agents, Anthropic Managed Agents, Google ADK) is that a long-running agent has three orthogonal concerns:

- **Brain** — the LLM that decides what to do next. Stateless between calls. Always re-derives intent from inputs.
- **Hands** — the tool layer that actually mutates the world (files, git, shell, network). Runs in a sandbox controlled by the runtime, not the brain.
- **Session** — the durable record of what happened. Persists across crashes, sleeps, model swaps. Sourced from the audit trail (`.overnight/<run-id>/`), git history, and the runtime's own session storage.

Build-overnight prompts must NEVER assume any of the three has memory the others don't see. The PRD.md / PLAN.md / STATE.md triad (clause C6) is the shared ground truth that survives all three layers.

## The 6 runtimes we target

| Runtime | Brain | Hands | Session | When to choose |
|---|---|---|---|---|
| **managed-agents** | Anthropic-hosted Claude, billed at $0.08/session-hour + tokens | Native session container, 30-day persistence | Anthropic-managed session store; implicit `wake()` on `user.message` to idle session | Cross-iteration memory needed, long idle periods OK, OK paying per session-hour |
| **ralph** (OMC) | Local Claude Code; self-loop via Stop-hook | Local shell/file via Claude Code permissions | `prd.json` + `progress.txt` + git tags + `.overnight/` | Default for laptop; PRD-driven; reviewer-gated |
| **continuous-claude** | Local Claude Code with `--max-duration` | Local shell/file | `SHARED_TASK_NOTES.md` bridge + `.overnight/` | Time-bounded sequential pipelines; explicit wall-clock cap |
| ralphthon (variant of ralph) | Local | Local + tmux orchestrator | Phase JSON + hardening waves | Hackathon-style: interview → execution → hardening → complete |
| ralph-loop (plugin) | Local | Local via Stop hook | Git history + filesystem; iteration-bounded | Lightest self-loop primitive; one prompt, magic-keyword stop |
| claude-p-chain | Local `claude -p` chain | Local shell/file | `SHARED_TASK_NOTES.md` between calls | Simplest case: N pre-scripted iterations, no LLM in the driver loop |

The default runtime when capability-profile match is ambiguous: **ralph** (per Phase 0.6 Q5).

See `runtime-adaptation.md` for the 3×4 clause-variant table.

## Wall-clock budgeting (clause C2)

No runtime as of 2026-05-27 exposes a wall-clock budget natively in a way the prompt can rely on. Even continuous-claude's `--max-duration` is enforced by the bash wrapper, not the model. So the prompt MUST teach the agent to track its own wall-clock and enter graceful ship-mode at the soft cap.

**Math the prompt must encode:**

```
hard_hours = user-supplied (default 8)
soft_hours = 0.9 * hard_hours      # 7.2h default
ship_mode_at = soft_hours          # at this point, stop new work; commit and PR what's done
force_kill_at = hard_hours         # at this point, bin/build-overnight-run sends SIGTERM
```

**Soft-cap behavior** (the agent itself enforces this):
1. Commit current work-in-progress as `WIP: <story>`.
2. Append to `BACKLOG.md` everything not done.
3. Generate `OVERNIGHT_RUN_REPORT.md` with `why_stopped: BUDGET`.
4. Push branch, open draft PR with `[OVERNIGHT]` prefix.
5. Exit cleanly.

**Hard-cap backup** (`bin/build-overnight-run` enforces this):
- `caffeinate -w $$` keeps the laptop awake.
- An external `at` job (optional) sends SIGTERM to the agent at `start + hard_hours`.
- The audit trail is still committed because the soft-cap should have fired first.

## Checkpoint cadence (drives clause C3 progress proof)

Every iteration that ends in a coherent state should:
1. `git add -A && git commit -m "checkpoint: <iteration N> <one-line>"`
2. `git tag overnight/<run-id>/ckpt-h<N>` (where N is elapsed hours, rounded).
3. Append a JSONL row to `.overnight/<run-id>/events.jsonl` with `kind="checkpoint"`, `commit_sha`, `diff_stat`, `test_exit_code`.
4. If wall-clock has crossed a 30-min boundary since the last full report, regenerate `STATE.md`.

The tag is the resume target if the run crashes. See "Resume model" below.

## Resume model (per Reconciler 2)

**Default for laptop runtimes (ralph, continuous-claude, ralphthon, ralph-loop, claude-p-chain):** git-tag restart.

On resume:
```
git reset --hard overnight/<run-id>/ckpt-h<latest>
# Replay PLAN.md forward from the last checkpoint's story-marker.
# Read STATE.md to reconstruct context (PRD.md never changes).
```

**For Managed Agents:** defer entirely to the runtime. Send any `user.message` to the idle session; container state (filesystem, packages, conversation) is preserved up to 30 days from last activity. The prompt records the session ID in `state.json` for provenance only — does NOT maintain a parallel state.

**For advanced opt-in (Temporal / Inngest / Cloudflare Workflows):** see Appendix A below for R4's full idempotency-keyed JSONL contract. Not v1 default.

**Non-git destructive side effects** (webhooks fired, `gh pr create` already ran, external API mutations): trigger stop-and-ask, NOT automated compensation in v1. The agent appends a `<requires_human_compensation>` block to FAILURE.md and exits.

## Stop rules (composes with build-prompt's standard `<stop_rules>`)

Every overnight prompt's `<stop_rules>` block must cover all four:

| Trigger | Behavior |
|---|---|
| Goal met (per acceptance criteria in PRD.md) | Commit, PR `[OVERNIGHT]` with `why_stopped: DONE`, exit |
| Soft time/cost cap hit | Ship-mode (see above), `why_stopped: BUDGET`, exit |
| Hard time/cost cap hit | `bin/build-overnight-run` kills; trap writes `why_stopped: FORCE_KILL` stub |
| Drift limit hit (clause C4) | Commit WIP, `why_stopped: AMBIGUOUS` or `RISK`, exit |
| Ambiguity that requires human judgment | Stop, `why_stopped: BLOCKED`, exit |
| Unverifiable claim or refused destructive op | `why_stopped: RISK`, exit |

## What the prompt must NEVER include

- Instructions to auto-merge or force-push (forbidden by clause C10).
- "Best effort" or "approximate" language without a concrete acceptance criterion.
- Instructions to disable tests, skip tests, or mock the system-under-test (clause C5).
- Self-modifying budget extensions (clause C2 `self_extension=forbidden`).
- "If stuck, try harder" loops without an oscillation detector.
- Hardcoded API keys, paths to `.env`, or any value matching `<credential_scope>` scrub patterns (clauses C12, C13).

---

## Appendix A — R4's full idempotency-keyed JSONL durable contract (opt-in advanced mode)

For users running on Temporal, Inngest, Cloudflare Workflows V2, Restate, DBOS, Trigger.dev, or AWS Step Functions — not the v1 default.

```
.overnight/<run-id>/
├── events.jsonl        # append-only journal, source of truth
├── state.json          # atomic-rewrite snapshot
├── PLAN.md             # static plan with step-kind tags
├── SCOREBOARD.md       # regenerated each iteration
├── COMPENSATORS.md     # destructive → inverse map
└── artifacts/
```

**Idempotency key:** `sha256(run_id || iteration || step_id || action_type || canonical_args)`.

**Iteration-1 resume prelude:**
```
state = read(state.json)
if state.in_flight_step is not None:
    step = state.in_flight_step
    if step.kind in {"read_only", "pure"}:
        redo(step)
    elif step.kind == "mutating" and step.idempotency_key:
        if side_effect_exists(step.idempotency_key):
            skip(step)
        else:
            redo(step)
    elif step.kind == "destructive" and not step.has_compensator:
        STOP_AND_ASK
```

This is documented for posterity; v1 build-overnight does NOT emit prompt clauses for these patterns unless the user explicitly invokes advanced mode in the interview.
