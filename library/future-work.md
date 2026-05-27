# Future-work categories (cut from v1)

Four categories were cut from v1 per the convention's Safety and Operator voices (Phase 0.6 Q4). They are documented here for re-evaluation in v1.1 once real-run data accumulates on the 6 shipping categories.

When the skill encounters a user request matching one of these, it surfaces this file and suggests the closest shipping alternative.

---

## dep-upgrade-overnight (CUT)

**Original goal:** multi-package dependency upgrade with test-fix loop.

**Why cut:** Operator §2 flagged this as a "lockfile and peer-dependency minefield." Documented failure patterns:
- Lockfile corruption when the agent runs `npm install` mid-loop and breaks reproducibility for subsequent iterations.
- Peer-dependency conflict cascades that require human design judgment to resolve.
- Silent semver-major upgrades that pass tests but break behavior under load.
- Transitive vulnerability fixes that introduce new transitive vulnerabilities.

**Re-evaluation conditions for v1.1:**
- Reproducible lockfile workflow with the agent operating on a frozen lockfile and only proposing upgrades, not applying them.
- An "attended-only" variant: ≤2h budget, single package per run, user reviews each upgrade individually.
- Mature peer-dep resolution heuristics in the prompt.

**Closest v1 alternative:** Run the dep upgrade manually, then use `bug-hunt-overnight` to fix the resulting test failures.

---

## cleanup-deslop-overnight (CUT)

**Original goal:** codebase hygiene sweep — remove TODOs, dead code, lint debt, unused imports.

**Why cut:** Safety §2 and Operator §5 flagged this as a "canonical foot-gun." Documented failure patterns:
- The agent deletes code that's reflectively-loaded or dynamically-imported (no static reference, but real runtime use).
- The agent removes "unused" type stubs that exist for external consumers.
- The agent deletes `# pragma: no cover` lines without checking why they're there.
- The agent rewrites TODO comments into "fixed!" without actually fixing the underlying issue.

**Re-evaluation conditions for v1.1:**
- A static-analysis gate that proves code is unreachable (not just unimported).
- Mandatory deny-list of files the agent never touches (e.g., `__init__.py` re-exports, plugin entry points).
- Human-in-the-loop review gate per deleted file (defeats the "unattended" framing — may belong in build-prompt, not build-overnight).

**Closest v1 alternative:** Run `ruff --fix` and `eslint --fix` manually for the safe subset; use `refactor-sweep-overnight` for specific cleanups with an explicit scope manifest.

---

## data-pipeline-build-overnight (CUT)

**Original goal:** ETL/ML pipeline scaffold with backtests.

**Why cut:** Safety §2 flagged as "refuse-by-default given Jordan's Supabase/sports DB stacks." Documented failure patterns:
- The agent writes to remote databases without read-only attestation (R2 mode #11: Replit, PocketOS prod-wipe incidents).
- Backtests that silently mutate source data.
- Idempotency gaps that double-count on retry.
- Schema migrations applied without rollback plans.

**Re-evaluation conditions for v1.1:**
- Mandatory `<database_policy>` clause restricting to read replicas + write to fresh tables only.
- Sandboxed compute target (separate user account or container with no prod credentials).
- Held-out fixtures that prove the pipeline is idempotent before any real-data run.

**Closest v1 alternative:** Use `feature-build-overnight` with a PRD that explicitly excludes database writes (agent generates pipeline code; user runs it manually against a sandbox).

---

## eval-harness-build-overnight (CUT)

**Original goal:** Eval suite construction with iterative scoring.

**Why cut:** The eval domain is hot in 2026 and the convention's R6 surfaced too many open questions (which benchmark, which judge, which partial-credit method, position-bias mitigation). Risk of building an eval suite that itself measures the wrong thing. Better to ship the 6 categories first, gather real-run data, and design an eval-harness category against that data in v1.1.

**Re-evaluation conditions for v1.1:**
- 30+ real overnight runs through the v1 categories to anchor what's worth measuring.
- A stable choice of LLM-judge model + calibration loop (R6 §"Calibration loop").
- Layer 3 fixture repo (`build-overnight-fixtures/`) functional first.

**Closest v1 alternative:** Use the build-prompt `eval-harness` category (sync, single-shot prompt) to draft an eval design, then iterate on it manually.

---

## Process for un-cutting a category

When real-run data justifies bringing one back:

1. Open an issue at `jordjones/build-overnight-skill` titled `propose-revive: <category>`.
2. Cite the real-run data (which categories surfaced demand, what failed without it).
3. Draft the category file using the same structure as the 6 shipped categories.
4. Add the mitigation clauses that address its specific failure modes (from this file's "Documented failure patterns" sections).
5. Pass the test harness (Layer 1 + thin Layer 2).
6. Bump minor version to v1.1.

The convention reports (`~/.claude/plans/jiggly-marinating-parnas-convention/`) remain available as substrate.
