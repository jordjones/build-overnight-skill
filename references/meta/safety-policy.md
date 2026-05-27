# Safety policy

What the skill REFUSES, what it WARNS on, what it BLOCKS at draft-time, and what it requires at runtime. v1 defaults; tighten via the interview if the user prefers.

## v1 stance: warn-not-block by default

The skill defaults to permissive **at draft-time** with strong runtime guardrails baked into every prompt. Hard-refusal at draft-time is reserved for unambiguous high-risk patterns (per Phase 0.6 Q4 — cut risky categories instead of trying to defang them).

## Hard-refuse at draft-time

If the user's raw input contains any of these patterns, the skill refuses to draft and explains why:

| Pattern | Example wording | Refusal rationale |
|---|---|---|
| Prod-credential mention | "use the prod DB password", "PRODUCTION_API_KEY" | Cannot ensure credential scope; clauses C12+C13 |
| Force-push intent | "force push", "git push -f", "rewrite history on main" | Hookify rule + R2 mode #11 (Replit-class incident) |
| Auto-merge intent | "auto-merge", "merge to main when done", "gh pr merge --auto" | C11 requires draft PRs, never auto-merge |
| Main-branch checkout | "work directly on main", "no branch", "commit to master" | C11 + Tier-1 sandbox mandate (worktree only) |
| Destructive shell intent | "rm -rf /", "DROP DATABASE", "truncate prod" | C10 unconditional |
| Disable-tests intent | "skip tests", "comment out failing tests", "delete the flaky tests" | C5 forbids test weakening |
| External-msg send intent (no review) | "send a Slack ping when done", "email me at done" | v1 ships macOS local notification only (F34); MCP sends are blocked |

## Warn-don't-block at draft-time

These get a one-line warning surfaced in the assumptions list, but the draft proceeds:

- User mentions a category that was cut from v1 (`dep-upgrade`, `cleanup-deslop`, `data-pipeline-build`, `eval-harness-build`) → suggest the closest shipping category or `library/future-work.md` rationale.
- User specifies a wall-clock budget > 8h → warn about METR time-horizon data and ask to confirm.
- User specifies a cost ceiling > $50 → warn and ask to confirm.
- User wants to overnight on a repo with uncommitted changes → wrapper script will refuse at runtime; warn at draft-time.

## Runtime guardrails enforced by the universal scaffold

These are non-negotiable, emitted in every prompt:

- **C9 + C10** — write scope allowlist + destructive-command policy.
- **C11** — git remote policy: `overnight/<run-id>-<slug>` branch only, draft PR with `[OVERNIGHT]` prefix, never auto-merge.
- **C12** — credential scope: scrub `*PROD*`, `AWS_*`, `STRIPE_*`, `SUPABASE_SERVICE_*`, `*_PRIVATE_KEY`, `*_SECRET` from environment.
- **C13** — pre-commit secret-scan via gitleaks/trufflehog.

## Sandbox tiering (see `sandbox-and-environment.md`)

- **Tier-1 (mandatory in v1):** git-worktree under `~/overnight-worktrees/<run-id>/`, scrubbed env, lockfile.
- **Tier-2 (documented but optional):** devcontainer with limited capabilities.
- **Tier-3 (out of scope for v1):** separate user account / VM.

## Audit-trail mandate

Every overnight run produces `.overnight/<run-id>/`:
- `MANIFEST.json` (run-id, runtime, started_at, repo, host, user, build-overnight version)
- `PROMPT.md` (verbatim dispatched prompt)
- `events.jsonl` (append-only audit; NOT consulted on resume in v1)
- `state.json` (thin metadata: latest_checkpoint_tag, MA session ID if applicable)
- `COST.json` (per-iteration cost + cache-hit rates)
- `FINAL_REPORT.md` (or `FAILURE.md` if `why_stopped != DONE`)
- `git-reflog-snapshot.txt` (entry-point recovery)
- `artifacts/` (anything the agent produces that's not source code)

The wrapper `bin/build-overnight-run` creates this directory and seeds MANIFEST.json + the reflog snapshot before the agent starts.

## Documented incidents this policy mitigates

| Incident | Year | Mitigation in v1 |
|---|---|---|
| Replit Agent deletes $1M SaaS startup prod DB | 2025 | C10 + C12 + Tier-1 worktree |
| PocketOS/Cursor/Opus wipes prod DB in 9 seconds | 2025 | Same |
| Devin completes only 3 of 20 tasks (Answer.AI) | 2025 | C3 + C8 (mandatory verifier pass) |
| Anthropic Aug–Sep 2025 model degradation | 2025 | C14 cache hygiene + monitor docs |
| "$12K Kubernetes infinite loop" | 2026 | C1 + C2 + oscillation detector (bug-hunt category) |
| Uber Claude Code $1.2M / 4-month burn | 2026 | C1 cost ceiling mandatory |
| "$400 overnight bill" (FinOps writeup) | 2025 | Same |

## The "what the prompt cannot prevent" list

Some failure modes require operator action, not prompt clauses:

- **Machine sleep / lid close** — `caffeinate` in `bin/build-overnight-run`; user must keep lid open or use clamshell mode.
- **Network drop** — runtime-specific; if it crashes the loop, resume from last git-tag.
- **gh CLI auth expiry mid-run** — wrapper checks at preflight; cannot detect mid-run.
- **Anthropic outage** — Managed Agents will resume; ralph/etc will fail and need manual resume.

Document these in the morning-review artifact's "known limitations" section, not in the prompt.

## Refuse-to-draft sample

```
User: "/build-overnight upgrade all dependencies on the prod branch and merge to main"

Skill: I can't draft this. Three blocks:
  1. "prod branch" + "merge to main" — auto-merge to main is forbidden (clause C11).
  2. dep-upgrade is a cut category in v1 (see library/future-work.md).
  3. Overnight runs must be on a worktree branch, never main (Tier-1 sandbox).

Try: "/build-overnight test-coverage on auth module on a worktree branch, 4h budget, $20 cap"
```
