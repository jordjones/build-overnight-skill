---
category: test-coverage-overnight
capability_profile:
  needs_cross_iteration_memory: false
  needs_parallel_subagents: false
  expected_idle_periods: short
  destructive_operations: rare
  budget_hours_typical: 4
  state_volume: low
suggested_runtime: ralph
suggested_budget_hours: 4
suggested_budget:
  direct_api_usd: 25
  oauth_iterations: 100
---

# test-coverage-overnight

Raise meaningful test coverage on a target module. Refuses to draft for naive line-coverage targets — gating requires mutation-coverage, branch-coverage, or a held-out behavioral fixture.

## When to use

**Signals:** existing module with low coverage, runnable test command, a coverage target the user can verbalize, no required design decisions.

**Counter-signals:** the user wants to "improve testing in general" (too vague — refuse and ask for a target module), the user wants ≥80% line coverage as the only metric (refuse — line coverage is Goodhart bait; require mutation/branch/fixture gate), the tests are already at the target (no work to do).

**Routes elsewhere:**
- "Fix the failing tests" → `bug-hunt-overnight`
- "Add tests AND refactor the module" → `refactor-sweep-overnight` (then test-coverage on the refactor branch)
- "Add tests for a new feature I haven't built yet" → `feature-build-overnight`

## Question bank (≤5 questions, ranked by leverage)

1. **What module + which test command?** Required. Refuse to draft without both. *Example user answer: "`src/auth/` and `pytest tests/auth -v --tb=short`"*
2. **What's the gate?** Choose: (a) `mutmut` mutation score ≥ X, (b) branch coverage ≥ Y, (c) named behavioral fixtures pass. Refuse plain line-coverage targets. *Example: "branch coverage on `src/auth/oauth.py` ≥ 90%"*
3. **What's off-limits?** Any test files the agent should NOT touch (existing fixtures, integration tests, etc.). Default: agent may add to `tests/` but not modify existing test files.
4. **Time + cost budget?** Default 4h / $25 (tighter than the universal $40 because test-coverage is bounded work).
5. **Runtime?** Required per universal SKILL.md Step 4. Default for this category: `ralph`.

## Default assumptions

- `<write_scope>`: `tests/` only (does not touch `src/` — that's refactor-sweep territory)
- `<time_budget>`: `hard_hours=4, soft_hours=3.6`
- `<cost_ceiling_usd>`: `hard=25, soft=20`
- PRD.md is the gate spec; STATE.md tracks per-test status.
- Model: `claude-sonnet-4-6` (test authoring rarely needs Opus)

## Category-specific mitigation clauses

In addition to the universal `<overnight_contract>` (C1–C14):

```xml
<test_coverage_gate>
  <metric>mutation_score | branch_coverage | named_fixtures_pass</metric>
  <minimum>0.90</minimum>
  <forbid>line_coverage_only, tautological_tests, test_only_imports, test_only_assert_true</forbid>
  <on_gate_fail>retry_with_better_test, do_not_lower_threshold</on_gate_fail>
</test_coverage_gate>

<tautological_refuse>
  <patterns>
    - assert_equal(x, x)
    - assert True / assert 1 == 1
    - try: ... ; except: pass (silent)
    - tests that import the SUT and assert nothing
    - tests that mock the SUT (per C5)
  </patterns>
  <on_detection>abort_iteration, log_to_FAILURE.md</on_detection>
</tautological_refuse>
```

## Template scaffold reference

Extends `references/scaffold/universal.md`. Adds the two clauses above to the prompt's `<output_format>`.

## Worked example

User input: *"add tests for the oauth module overnight, ralph, 4 hours, 90% branch coverage"*

Drafted prompt skeleton:

```
You are running test-coverage-overnight on src/auth/oauth.py.
PRD.md sets the goal: branch coverage ≥ 90% measured by
`pytest --cov=src.auth.oauth --cov-branch --cov-report=term-missing tests/auth/`.

<overnight_contract>
  <cost_ceiling_usd hard=25 soft=20/>
  <time_budget hard_hours=4 soft_hours=3.6/>
  ... (all 14 universal clauses)
</overnight_contract>

<test_coverage_gate metric="branch_coverage" minimum="0.90"/>
<tautological_refuse>... (as above)</tautological_refuse>

<execution>
  (ralph variant text from runtime-adaptation.md)
</execution>

<output_format>
  <stop_rules>
    Stop when branch coverage on src/auth/oauth.py >= 90% per the pytest
    cmd above OR soft cap (3.6h or $20) hit OR drift limit hit OR ambiguity.
    Always: commit, tag overnight/{run-id}/ckpt-h{N}, push branch,
    open draft PR [OVERNIGHT] test-coverage src/auth/oauth.py.
    Never: lower the gate threshold, weaken existing tests, mock oauth itself.
  </stop_rules>
</output_format>
```

## Failure modes addressed

- Tautological tests (D5 + tautological_refuse clause above)
- Naive line-coverage (gate requires mutation/branch/fixture)
- Test weakening (C5 universal clause)
- Goodhart on coverage % (gate is a *floor* not a *target*)
