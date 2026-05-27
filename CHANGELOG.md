# Changelog

All notable changes to `build-overnight` will be documented here.

## [v1.0.0-rc1] — 2026-05-27

Release candidate. Final `v1.0.0` tag pending **one successful real overnight run** through the skill (per Reconciler #1 compromise: "compromise between immediate-tag and 5-real-runs").

### Test status
- Layer 1 (static + coherence): **19/19 pass** (`$0`).
- Layer 2 classification: **3/3 pass**; Sonnet judge opt-in via `--layer2` + valid `ANTHROPIC_API_KEY`.
- Layer 3 (real-run fixture repos): deferred to v1.1.

### Added — v1.0.0 scope
- `SKILL.md` adapted from `build-prompt`: 7-step interview loop, runtime question at Step 5, dispatch table for 6 overnight categories.
- 6 category files at `references/categories/`: `test-coverage`, `bug-hunt`, `feature-build`, `refactor-sweep`, `docs-pass`, `research-deep` (each declares a `capability_profile` instead of a hard-coded runtime).
- 15 build-prompt meta-files hard-copied verbatim into `references/meta/` (per user decision Q1).
- 7 new overnight-specific meta-files: `overnight-loop-mechanics`, `safety-policy`, `sandbox-and-environment`, `cost-and-telemetry`, `audit-trail`, `morning-review-artifact`, `runtime-adaptation`.
- Universal scaffold at `references/scaffold/universal.md` enforcing 14 mandatory clauses (C1–C14) on every drafted prompt.
- `bin/build-overnight-run` wrapper: preflight (caffeinate, AC check, gh auth, disk, model pin), lockfile, telemetry sink.
- `references/research-distilled.md` distilling the convention substrate (11 reports, 35 convergent findings).
- `library/future-work.md` documenting 4 cut categories.
- Layer 1 + thin Layer 2 test harness at `build-overnight-research/test_skill.py` (Layer 3 deferred to v1.1).

### Defaults (user-confirmed via Phase 0.6)
- Wall-clock budget: 8h hard / 7.2h soft.
- Cost ceiling: $40 hard / $32 soft.
- Sandbox: Tier-1 worktree under `~/overnight-worktrees/<run-id>/` mandatory.
- Default runtime when ambiguous: `ralph`.
- Resume model: git-tag for laptop runtimes; defer to native on Managed Agents; JSONL idempotency contract is opt-in advanced mode only.

### Provenance
- Built on top of [`build-prompt`](https://github.com/jordjones/build-prompt-skill) v2 (2026-05-26 refresh).
- Plan, convention reports, and synthesis at `~/.claude/plans/jiggly-marinating-parnas{.md,-convention/}`.
