# WORKLOG — build-overnight

## Ongoing Workstreams

*(none)*

## Active Projects

### Ship build-overnight v1.0.0

**Goal:** Publicly release `build-overnight` v1.0.0 — a Claude Code skill that drafts prompts engineered to drive autonomous unattended overnight LLM agent loops with hard cost/time/iteration ceilings, drift detection, and PR-as-handoff morning review.

**Status:** in-progress
**Started:** 2026-05-27
**Last session:** 2026-05-27
**Definition of done:** `v1.0.0` tag (no `-rc`) pushed to `jordjones/build-overnight-skill` main, gated on one successful real overnight run through the skill (per convention Reconciler #1).

**Context:** Built end-to-end from scratch in a single working day. Phase 0 ran a multi-round adversarial + research convention (4 adversarial voices + 7 deep-research agents + 3 reconcilers + 1 synthesis → 35 convergent findings, 10 conflicts resolved, 8 user-confirmed defaults). Phases 1–3 scaffolded the skill, authored 6 categories + 7 overnight meta-files + 14-clause universal scaffold, and shipped Layer 1 + thin Layer 2 test harness. Tagged `v1.0.0-rc1`. Then rc2 fixed a billing-mode correctness bug: rc1's `<cost_ceiling_usd>` clause assumed pay-per-token, which misbehaves under Claude Code OAuth subscription (phantom abort or silent disablement). rc2 split C1 by mode and added new clause C15 `<iteration_budget>` as the primary stop-on-budget gate under subscription. Layer 1 expanded to 20/20 green, both billing modes exercised.

**Next steps:**
- [ ] **Run one empirical overnight on `docs-pass-overnight`** (lowest blast radius, 3h budget) under Claude Code OAuth to discharge the v1.0.0 gate.
- [ ] Inspect the run: `MANIFEST.json:billing_mode == "oauth-subscription"`, no phantom USD in REPORT.md, iteration cap honored, `[OVERNIGHT]` PR opened.
- [ ] If clean: re-tag `v1.0.0` (no `-rc`) and push.
- [ ] After v1.0.0: collect cost-benchmark data from real runs and seed `library/cost-benchmarks.md`.
- [ ] v1.1 candidates: Layer 3 fixture-repo harness; un-cut `dep-upgrade-overnight` (attended-only) if usage justifies; Managed Agents auto-suppression rule for redundant clauses.

**Key files:**
- `SKILL.md` — 7-step interview; runtime + billing-mode questions; review rubric
- `references/scaffold/universal.md` — 15 mandatory clauses C1–C15 (C1 has 2 emission variants; C15 added in rc2)
- `references/categories/*.md` — 6 category files (test-coverage, bug-hunt, feature-build, refactor-sweep, docs-pass, research-deep)
- `references/meta/*.md` — 15 hard-copied from build-prompt + 7 overnight-specific (`overnight-loop-mechanics`, `safety-policy`, `sandbox-and-environment`, `budget-and-telemetry`, `audit-trail`, `morning-review-artifact`, `runtime-adaptation`)
- `references/research-distilled.md` — 14-item substrate distillation from the convention
- `library/2026-05-27-*.md` — 6 worked-example library entries (mix of direct-api + oauth-subscription)
- `library/future-work.md` — 4 cut categories with revive conditions
- `bin/build-overnight-run` — preflight + lockfile + caffeinate + billing-mode detection wrapper
- `build-overnight-research/test_skill.py` — Layer 1 (20 checks, $0) + thin Layer 2 (classification + opt-in Sonnet judge)
- `CHANGELOG.md` — v1.0.0-rc1 and v1.0.0-rc2 entries
- `README.md` — user-facing landing page

**Convention artifacts (off-repo, in user plans dir):**
- `~/.claude/plans/jiggly-marinating-parnas.md` — plan of record (current shape: rc2)
- `~/.claude/plans/jiggly-marinating-parnas-convention/` — 11 reports, CONVERGENT_FINDINGS, CONFLICTS, QUESTIONS, 3 RECONCILER files, SYNTHESIS
- `~/.claude/plans/jiggly-marinating-parnas-rc2-audit.md` — rc2 per-file audit + failure-mode reproduction

**Tags:**
- `v1.0.0-rc1` (2026-05-27) — initial 14-clause scaffold, 6 categories, Layer 1 19/19
- `v1.0.0-rc2` (2026-05-27) — billing-mode correctness, C15 iteration_budget, Layer 1 20/20

## Exploratory

*(none)*

## Completed Workstreams

*(none yet)*

## Parked

*(none)*

## Session Log

### 2026-05-27 — initial build + rc2 billing-mode fix
- Phase 0 convention (11 voices, 3 reconcilers, 1 synthesis, 8 user decisions)
- Phase 1 scaffold v1, Phase 2 categories + library, Phase 3 test harness + tag v1.0.0-rc1
- rc2 audit, billing-mode adaptation across 13 files + 1 rename, Layer 1 20/20, tag v1.0.0-rc2
- Both rc tags pushed to `jordjones/build-overnight-skill`
