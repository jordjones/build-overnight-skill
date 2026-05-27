# Sandbox and environment

The environment an overnight run executes in. v1 default: Tier-1 worktree (mandatory) + `bin/build-overnight-run` wrapper (handles preflight, caffeinate, lockfile, telemetry). Tier-2 (devcontainer) documented but optional.

## Tier-1 — git-worktree sandbox (mandatory in v1)

Every overnight run executes in a dedicated git worktree under `~/overnight-worktrees/<run-id>/`. This is enforced by `bin/build-overnight-run` at preflight.

**Setup pattern:**

```bash
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-$(uuidgen | cut -d- -f1)"
REPO=~/Documents/GitHub/myproject
git -C "$REPO" worktree add "$HOME/overnight-worktrees/$RUN_ID" -b "overnight/$RUN_ID-bug-hunt"
cd "$HOME/overnight-worktrees/$RUN_ID"
bin/build-overnight-run "$RUN_ID" ralph
```

The worktree gives:
- A clean checkout the agent can mutate freely without touching the main checkout.
- A dedicated branch (`overnight/<run-id>-<slug>`) for the PR (clause C11).
- Trivial cleanup: `git worktree remove` after the morning review.
- Isolation from concurrent overnight runs on the same repo.

**Cleanup after the morning review:**

```bash
# After you've decided to ship/revert via the PR:
git -C "$REPO" worktree remove "$HOME/overnight-worktrees/$RUN_ID"
git -C "$REPO" branch -D "overnight/$RUN_ID-bug-hunt" 2>/dev/null  # if not merged
rm -rf "$HOME/overnight-worktrees/$RUN_ID/.overnight"             # if not needed for audit
```

## Tier-2 — devcontainer (documented, optional)

For runs targeting HIGH-risk categories (feature-build, refactor-sweep on critical paths) or for users who want stronger isolation:

- Run the agent inside a devcontainer with limited network egress and no host filesystem access outside the worktree.
- Mount the worktree read-write; nothing else.
- Mount a scrubbed env file (see "Environment scrubbing" below).
- Exit policy: container stops on goal-met or budget-cap; results are extracted via `git push` (the only allowed network op).

`devcontainer.json` template is **not shipped in v1**. If the user opts in to Tier-2, the skill emits a stub `devcontainer.json` in the worktree and asks the user to wire it up before launch.

## Environment scrubbing

Before launching the agent, scrub these env vars (whether via the wrapper or the devcontainer):

```bash
unset $(env | grep -Ei '^(AWS_|STRIPE_|SUPABASE_SERVICE|.*PROD|.*PRIVATE_KEY|.*SECRET|.*PASSWORD|.*TOKEN)' | cut -d= -f1)
# Plus any project-specific patterns from the user's interview answer.
```

The wrapper does this in v1. Document any project-specific additions to the `<credential_scope>` clause at draft-time.

## Preflight checks (enforced by `bin/build-overnight-run`)

The wrapper refuses to launch if any of these fail:

| Check | Refusal |
|---|---|
| Not under `~/overnight-worktrees/<run-id>/` | "refuse to run outside ~/overnight-worktrees/..." |
| `caffeinate` not installed (macOS only) | "Install or skip with --dry-run." |
| `gh` CLI not installed | "Install GitHub CLI before overnight runs." |
| `gh auth status` fails | "Run: gh auth login" |
| Not on AC power (macOS) | "refuse to launch on battery." |
| `$HOME` disk < 5GB free | "free disk in $HOME is XGB; need >= 5GB." |
| Working tree dirty | "refuse to run with a dirty tree. Commit or stash first." |

## Caffeinate / power

macOS App Nap kills long-running shell scripts. The wrapper uses `caffeinate -dimsu -w $$` to:
- Prevent display sleep (`-d`)
- Prevent idle sleep (`-i`)
- Prevent disk sleep (`-m`)
- Prevent system sleep (`-s`)
- Prevent user sleep (`-u`)
- Tie lifetime to the wrapper PID (`-w $$`)

When the wrapper exits, caffeinate dies. The user must keep the lid open OR use clamshell mode (external monitor + power).

## Lockfile

`~/overnight-worktrees/.locks/<repo-path-encoded>.lock` is acquired by the wrapper. Prevents two overnight runs targeting the same repo concurrently — which would race on git state and trip the audit-trail directory.

Stale lockfile recovery: if the wrapper crashed and left a lockfile, delete it manually:

```bash
ls ~/overnight-worktrees/.locks/
rm ~/overnight-worktrees/.locks/<the-stale-one>.lock
```

## Telemetry sink

The wrapper writes a JSONL event stream to `.overnight/<run-id>/events.jsonl`:

```json
{"ts":"2026-05-27T08:00:00.000Z","run_id":"...","kind":"run_started","runtime":"ralph","repo":"/Users/..."}
{"ts":"2026-05-27T08:05:00.123Z","run_id":"...","kind":"iteration_complete","iteration":1,"commit_sha":"...","cost_usd":"0.12"}
{"ts":"2026-05-27T08:10:00.456Z","run_id":"...","kind":"checkpoint","tag":"overnight/<run-id>/ckpt-h0"}
{"ts":"2026-05-27T15:55:00.789Z","run_id":"...","kind":"ship_mode_entered","reason":"soft_cap"}
{"ts":"2026-05-27T15:58:00.012Z","run_id":"...","kind":"run_completed","why":"DONE"}
```

The agent itself writes most events (via shell-out from inside the loop); the wrapper writes `run_started`, `awaiting_completion`, `dry_run_exit`, and the trap-fired exit event.

In v1 this file is **audit-only** — never consulted on resume (per Reconciler 2). Resume always replays from the latest git-tag.

## Model alias pinning

The wrapper cannot enforce server-side model pinning (the API picks the model based on alias). The prompt should reference a specific model ID (e.g., `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`) per `<cache_warming_strategy>` C14 ("no mid-run model swaps"). If the user supplies `claude-opus-latest` and the alias rolls mid-run, cache-hit rate will drop and cost can spike 5×.

**Recommendation:** the interview asks the user to confirm a model ID (not an alias) for any run with a `<cost_ceiling_usd>` > $20.
