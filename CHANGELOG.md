# Changelog

All notable changes to `build-overnight` will be documented here.

## [v1.0.0-rc2] — 2026-05-27

Billing-mode correctness pass. rc1's clause C1 `<cost_ceiling_usd>` assumed pay-per-token billing with a meaningful `response.usage`; under Claude Code OAuth subscription the agent inside the loop has no reliable per-call cost surface and the rc1 cost ceiling caused either phantom aborts (computed from list prices) or silent disablement (no usage → ceiling never trips). rc2 splits C1 by billing mode and introduces C15 `<iteration_budget>` as the primary stop-on-budget gate under subscription.

### Added
- **Clause C15 `<iteration_budget>`** — new mandatory universal clause. Under `oauth-subscription` mode this is the primary stop-on-budget gate; under `direct-api` it is secondary to C1. Total universal clauses: **15** (was 14).
- **Billing-mode awareness** throughout the skill. New SKILL.md interview question; env-sniff default (`ANTHROPIC_API_KEY` set → `direct-api`, else `oauth-subscription`); `OVERNIGHT_BILLING_MODE` env override in the wrapper.
- **`references/meta/budget-and-telemetry.md`** — renamed from `cost-and-telemetry.md` with mode-conditional content. Two top-level sections: "Mode 1: direct-api" and "Mode 2: oauth-subscription". 2-layer kill-switch documented for subscription (was 3-layer for direct-api).
- **Audit-trail MANIFEST.json + COST.json `billing_mode` field.** Under `oauth-subscription`, all `*_usd` fields in COST.json MUST be `null`. Phantom-USD warning added.
- **6 library entries updated** with `billing_mode` frontmatter and conditional XML body. Mix: 3 `direct-api` (test-coverage, feature-build, docs-pass), 3 `oauth-subscription` (bug-hunt, refactor-sweep, research-deep).
- **`bin/build-overnight-run`** preflight detects `ANTHROPIC_API_KEY` and writes `MANIFEST.json:billing_mode`; logs subscription-mode caveats.
- **Test harness** Layer 1 expanded to 20+ checks: `billing_mode` validity (L1.8), C15 clause presence (already covered by C1–C15 array), category `suggested_budget` shape (L1.10), library body XML matches frontmatter mode (L1.11), iteration-coherence (soft = 0.8 × hard for `<iteration_budget>`).

### Changed
- Clause C1 `<cost_ceiling_usd>` now has two emission variants. Under `direct-api`: existing block with `<hard_cap>`/`<soft_cap>` USD values + accumulator note. Under `oauth-subscription`: `<cost_ceiling_usd mode="subscription_disabled">` with no `<hard_cap>` USD value.
- SKILL.md review rubric "Overnight Discipline" auto-fail rule now checks billing-mode-conditional clause presence (C1 USD form under direct-api; subscription_disabled marker + C15 under oauth-subscription).
- SKILL.md Step 5 Assumptions block always lists `Billing mode`. Under subscription, lists `Iteration cap` instead of `Cost ceiling`.
- Category frontmatter `suggested_cost_ceiling_usd: N` → `suggested_budget: {direct_api_usd: N, oauth_iterations: M}` across all 6 categories.
- Morning-review artifact `Cost: $X` row → conditional `Budget: $X` (direct-api) or `Budget: N iterations` (subscription).
- Wrapper MANIFEST.json now reports `build_overnight_version: v1.0.0-rc2`.

### Audit
- See `~/.claude/plans/jiggly-marinating-parnas-rc2-audit.md` for the per-file inventory, the static reproduction of the two failure modes (phantom abort + silent disablement) the rc2 design prevents, and the OAuth-session-usage investigation.

### Test status
- Layer 1 (static + coherence): **20/20 pass** (`$0`). Both billing modes exercised.
- Layer 2 classification: **3/3 pass**; Sonnet judge opt-in via `--layer2` + valid `ANTHROPIC_API_KEY`.
- Layer 3 (real-run fixture repos): deferred to v1.1.
- Wrapper dry-run smoke under `OVERNIGHT_BILLING_MODE= ANTHROPIC_API_KEY=`: correctly sets `billing_mode: oauth-subscription` in MANIFEST.json.

### v1.0.0 tag gate (unchanged)
Final `v1.0.0` tag (without `-rc`) still gated on one successful real overnight run through the skill. Recommended first run: `docs-pass-overnight` under Claude Code OAuth (the rc2 path now properly modeled).

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
