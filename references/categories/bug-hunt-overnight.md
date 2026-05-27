---
category: bug-hunt-overnight
capability_profile:
  needs_cross_iteration_memory: true
  needs_parallel_subagents: false
  expected_idle_periods: short
  destructive_operations: rare
  budget_hours_typical: 6
  state_volume: medium
suggested_runtime: ralph
suggested_budget_hours: 6
suggested_budget:
  direct_api_usd: 30
  oauth_iterations: 150
---

# bug-hunt-overnight

Drive a failing test, stack trace, or reproducible regression to green. Includes root-cause tracking, A↔B oscillation detection, and a forbid-masking-via-mock invariant.

## When to use

**Signals:** there is a specific failure (failing test, error message, repro steps), the user wants the root cause AND the fix (not a workaround), the failure is reproducible.

**Counter-signals:** "the app feels slow" (too vague — refuse, ask for a measurable regression), "this MIGHT be broken" (no repro — refuse), the user wants ONLY the symptom suppressed (refuse — C5 forbids test weakening / silent skips).

**Routes elsewhere:**
- "Add tests to catch this kind of bug in the future" → `test-coverage-overnight` after the fix lands
- "Make this thing faster" without a regression target → not an overnight category; do it sync
- "Find ALL bugs in this module" → too unbounded; pick one symptom

## Question bank (≤5 questions, ranked by leverage)

1. **What's the failing test or repro command?** Required. Refuse without a runnable failure. *Example: "`pytest tests/billing/test_invoice.py::test_pro_rated_refund -x`"*
2. **What does success look like?** The named test goes green AND `pytest tests/billing/ -x` stays green AND the root cause is documented in `ROOT_CAUSE.md`.
3. **Where should the agent look first?** Optional. If the user has a hypothesis, set the scope manifest accordingly. Default: agent crawls from the test file.
4. **What's off-limits?** Any modules where a fix would require human approval (auth, payments, migrations). Default: agent may touch the failing module + its direct callees.
5. **Runtime?** Required. Default: `ralph` (needs PRD discipline + reviewer gates for root-cause vs symptom).

## Default assumptions

- `<write_scope>`: `src/` + `tests/` for the affected slice
- `<time_budget>`: `hard_hours=6, soft_hours=5.4`
- `<cost_ceiling_usd>`: `hard=30, soft=24`
- `ROOT_CAUSE.md` is a required artifact (not optional)
- Model: `claude-opus-4-7` (root-cause analysis benefits from Opus)

## Category-specific mitigation clauses

In addition to the universal `<overnight_contract>` (C1–C14):

```xml
<oscillation_detector>
  <signal>two_consecutive_iterations_produce_diff_hash_X_then_Y_then_X</signal>
  <window>4_iterations</window>
  <on_detection>
    log oscillation_detected event;
    write OSCILLATION.md with both diffs;
    stop_and_handoff with why_stopped=AMBIGUOUS
  </on_detection>
</oscillation_detector>

<root_cause_tracking>
  <required_artifact>ROOT_CAUSE.md</required_artifact>
  <required_sections>
    - "Symptom" (what the user observes)
    - "Reproduction" (deterministic command)
    - "Root cause" (the actual mechanism, not "added a try/except")
    - "Why the test caught it" (what guard was missing)
    - "What still won't be caught" (honest limitation)
  </required_sections>
  <forbid>fix_without_root_cause_explanation, "this seems to work"</forbid>
</root_cause_tracking>

<no_symptom_masking>
  <forbid>
    - mocking the failing module
    - try/except that swallows the original error
    - changing the test expectation to match buggy behavior
    - removing the assertion that catches the bug
  </forbid>
  <enforcement>pre_commit_diff_scan</enforcement>
</no_symptom_masking>
```

## Template scaffold reference

Extends universal. Adds the three clauses above. Also: the prompt's `STATE.md` tracks hypothesis-elimination as an explicit list (which hypotheses ruled out, which still open).

## Worked example

User input: *"test_pro_rated_refund is failing intermittently in CI, looks like a race condition, ralph 6h"*

Drafted prompt skeleton:

```
You are running bug-hunt-overnight on tests/billing/test_invoice.py::test_pro_rated_refund.
PRD.md sets the goal: the named test passes 50 consecutive times AND the broader
billing suite stays green AND ROOT_CAUSE.md is written.

<overnight_contract>... (14 universal clauses with budget=6h, ceiling=$30)</overnight_contract>
<oscillation_detector>... (see above)</oscillation_detector>
<root_cause_tracking>... (require ROOT_CAUSE.md before any commit claims success)</root_cause_tracking>
<no_symptom_masking>... (forbid mocking, try/except swallow, etc.)</no_symptom_masking>

<execution>... (ralph)</execution>

Investigation protocol (record in STATE.md each iteration):
  HYPOTHESES_OPEN: [...]
  HYPOTHESES_RULED_OUT: [...]
  EVIDENCE_FOR: {...}
  EVIDENCE_AGAINST: {...}
  NEXT_PROBE: ...

<output_format>
  <stop_rules>
    Stop when: (a) test passes 50/50 in a row AND root cause documented,
    (b) soft cap, (c) drift limit, (d) oscillation detected, (e) ambiguity
    needs human (e.g. fix would require schema migration).
  </stop_rules>
</output_format>
```

## Failure modes addressed

- A↔B oscillation (oscillation_detector)
- Symptom-masking via mocks, try/except, weakened assertions (no_symptom_masking + C5)
- Fix-without-understanding (root_cause_tracking)
- Goal drift toward "fix all the things" (C4 + scope manifest)
- Hallucinated completion claiming root cause without evidence (C3 + ROOT_CAUSE.md required)
