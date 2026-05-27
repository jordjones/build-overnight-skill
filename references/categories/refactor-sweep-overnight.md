---
category: refactor-sweep-overnight
capability_profile:
  needs_cross_iteration_memory: false
  needs_parallel_subagents: false
  expected_idle_periods: short
  destructive_operations: occasional
  budget_hours_typical: 6
  state_volume: medium
suggested_runtime: ralph
suggested_budget_hours: 6
suggested_cost_ceiling_usd: 30
---

# refactor-sweep-overnight

Mechanical refactor at scale: rename, restructure, move modules, extract helpers. **Behavior must be preserved** — tests stay green at every checkpoint, no new public API surface, no semantic changes.

## When to use

**Signals:** the refactor is mechanical (rename, move, extract), there's a comprehensive test suite that exercises the affected code, the user can name the success condition (e.g., "all `OldName` → `NewName`, tests still green").

**Counter-signals:** the refactor requires design judgment (refuse — that's architecture, not refactor), the test suite doesn't cover the affected code (refuse — no way to verify behavior preservation), the refactor introduces new abstractions (refuse — that's a feature in disguise).

**Routes elsewhere:**
- "Refactor X AND add feature Y" → split: refactor first (this category), then `feature-build-overnight`
- "Fix the tests after I refactored manually" → `bug-hunt-overnight`
- "Decide whether to refactor X" → not overnight; use `/build-prompt` architecture-design

## Question bank (≤5 questions, ranked by leverage)

1. **What's the refactor?** Required, concrete. *Example: "rename `class UserService` → `class AccountService` across `src/` and update all callers"*
2. **What's the test command for behavior preservation?** Required. Must run at every checkpoint. *Example: "`pytest -q`"*
3. **What's the scope manifest?** Required: list of directories/files in scope. Anything outside is out-of-scope edits.
4. **Are there migrations or schema changes?** If YES → refuse (gated to Safety policy; use `feature-build-overnight` with explicit user attestation).
5. **Runtime?** Required. Default: `ralph` (sequential checkpoints fit the pattern).

## Default assumptions

- `<write_scope>`: explicit list from question 3
- `<time_budget>`: `hard_hours=6, soft_hours=5.4`
- `<cost_ceiling_usd>`: `hard=30, soft=24`
- Test suite MUST be runnable in < 5 min for checkpointing to work
- Model: `claude-sonnet-4-6` (refactor is largely mechanical)

## Category-specific mitigation clauses

In addition to the universal `<overnight_contract>` (C1–C14):

```xml
<behavior_preservation_invariant>
  <required_test_command>$TEST_COMMAND</required_test_command>
  <gate>tests pass before commit AND after commit AND every iteration</gate>
  <forbid>
    - new public API surface (classes, functions, methods)
    - removed public API surface (deprecation requires user approval)
    - changed function signatures (excepting renames within scope)
    - new dependencies (no new imports beyond renames)
    - semantic changes (the same input must produce the same output)
  </forbid>
  <on_violation>abort_iteration, rollback, log_to_FAILURE.md</on_violation>
</behavior_preservation_invariant>

<tests_green_per_checkpoint>
  <cadence>every iteration</cadence>
  <gate>$TEST_COMMAND exit 0</gate>
  <on_failure>
    rollback iteration (git reset --hard to ckpt-h{N-1});
    re-attempt with narrower change;
    if 3 consecutive failures, abort and log to FAILURE.md
  </on_failure>
</tests_green_per_checkpoint>

<no_silent_api_change>
  <signal>diff includes class/def/export/pub declarations or removals</signal>
  <on_detection>
    refuse iteration UNLESS:
      (a) the change matches the rename pattern from PRD.md, OR
      (b) the change is internal-only (private, _underscore, file-local)
  </on_detection>
</no_silent_api_change>
```

## Template scaffold reference

Extends universal. Adds the three clauses above. PRD.md spells out the rename/restructure pattern exactly; STATE.md tracks files-touched count and tests-green-at-each-checkpoint.

## Worked example

User input: *"rename UserService to AccountService across src/, keep tests green, 6h ralph"*

Drafted prompt skeleton:

```
You are running refactor-sweep-overnight to rename `UserService` → `AccountService`.
PRD.md sets the goal: every reference in `src/` updated, tests pass at every checkpoint,
no new or removed public API surface.

<overnight_contract>... (14 universal clauses)</overnight_contract>
<behavior_preservation_invariant>
  required_test_command: "pytest -q"
  ... (full clause)
</behavior_preservation_invariant>
<tests_green_per_checkpoint>... </tests_green_per_checkpoint>
<no_silent_api_change>...</no_silent_api_change>

<execution>... (ralph)</execution>

Approach (record progress in STATE.md):
  ITERATION_N: files touched this iteration, test exit code, cumulative count
  REMAINING: grep -rn "UserService" src/ | wc -l

<output_format>
  <stop_rules>
    Stop when: (a) `grep -rn "UserService" src/` returns zero results
    AND `pytest -q` exit 0 AND PR opened; (b) soft cap; (c) any iteration
    fails tests 3x in a row; (d) drift/ambiguity. Never: silently change
    behavior; never break a test instead of finding the real call site.
  </stop_rules>
</output_format>
```

## Failure modes addressed

- Silent behavior change masquerading as refactor (no_silent_api_change + behavior_preservation_invariant)
- Tests break mid-sweep and never recover (tests_green_per_checkpoint with rollback)
- Scope creep into unrelated files (C4 + explicit write_scope from question 3)
- Surprise migrations (refused at draft-time via question 4)
- "It compiles" mistaken for "it works" (gate is test exit code, not build success)
