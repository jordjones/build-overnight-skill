---
category: feature-build-overnight
capability_profile:
  needs_cross_iteration_memory: true
  needs_parallel_subagents: false
  expected_idle_periods: medium
  destructive_operations: occasional
  budget_hours_typical: 8
  state_volume: high
suggested_runtime: ralph
suggested_budget_hours: 8
suggested_cost_ceiling_usd: 40
---

# feature-build-overnight

Implement a feature from a PRD. **Refuses to draft without an explicit PRD** — feature-build without acceptance criteria is the highest-drift category and the convention's preliminary scan flagged it accordingly.

## When to use

**Signals:** there is (or the user can write) a PRD with acceptance criteria, the feature decomposes into ≥3 stories the agent can complete sequentially, the design is settled (no architecture decisions remain).

**Counter-signals:** the user wants the agent to "figure out the design overnight" (refuse — architecture decisions need human judgment), the feature touches user-facing UI without screenshots in scope (UI-overnight is fragile), the feature requires a new database schema (gated on Safety policy — refuse).

**Routes elsewhere:**
- "Refactor X to enable feature Y" → `refactor-sweep-overnight` first
- "Add tests for the feature I built" → `test-coverage-overnight` after
- "Sketch the design for feature X" → not overnight; use `/build-prompt` architecture-design

## Question bank (≤5 questions, ranked by leverage)

1. **Where's the PRD?** Required path. Refuse if missing. Acceptable: `docs/prd-<feature>.md` or inline if the user pastes one. *Example: "use `docs/prd-sso.md`"*
2. **What are the acceptance criteria?** Required (verbatim, ≥3 testable items). If PRD has them, copy them. If not, draft and confirm.
3. **What's the test command for done-ness?** Required. The agent calls this between stories. *Example: "`pytest tests/integration/test_sso.py`"*
4. **Story decomposition: who owns it?** Choose: (a) PRD already has it; (b) the agent decomposes on iteration 1 and writes PLAN.md, then proceeds. Default: (b).
5. **Runtime?** Required. Default: `ralph` (PRD-driven, reviewer-gated). `managed-agents` if cross-iteration memory needed for long-running work.

## Default assumptions

- `<write_scope>`: `src/` + `tests/` for the feature's directory tree
- `<time_budget>`: `hard_hours=8, soft_hours=7.2`
- `<cost_ceiling_usd>`: `hard=40, soft=32` (universal default)
- PLAN.md must enumerate stories with acceptance criteria per story
- Model: `claude-opus-4-7` for the planner role; `claude-sonnet-4-6` for the worker role

## Category-specific mitigation clauses

In addition to the universal `<overnight_contract>` (C1–C14):

```xml
<prd_decomposition_gate>
  <required_artifact>PLAN.md</required_artifact>
  <required_per_story>
    - id (S1, S2, ...)
    - one_line_goal
    - acceptance_criteria (≥1 testable assertion)
    - estimated_iterations (1–5)
    - dependencies (other story IDs)
  </required_per_story>
  <refuse_if>
    - PRD has zero testable acceptance criteria
    - PLAN.md decomposes to zero stories or > 12 stories (decompose finer / coarser)
  </refuse_if>
</prd_decomposition_gate>

<acceptance_criteria_checklist>
  <per_story_required>
    - test_command runs (exit code 0 implies story DONE)
    - no_test_weakening_in_diff (C5 enforcement)
    - PR comment listing files touched by this story
    - update PLAN.md status: PENDING → IN_PROGRESS → DONE | BLOCKED
  </per_story_required>
  <ship_mode_behavior>
    On soft_cap, mark all in-progress stories WIP, commit, append to BACKLOG.md.
    Do NOT attempt to finish a partially-done story past the cap.
  </ship_mode_behavior>
</acceptance_criteria_checklist>

<behavior_preservation_invariant>
  <forbid>
    - changes to APIs not explicitly listed in the PRD
    - breaking changes to public functions/classes
    - schema migrations
    - changes to authentication/authorization paths
  </forbid>
  <on_violation>abort_iteration, log_to_FAILURE.md, why_stopped=RISK</on_violation>
</behavior_preservation_invariant>
```

## Template scaffold reference

Extends universal. Adds the three clauses above. PLAN.md is the source of truth for story status; STATE.md mirrors the current story + intra-story progress.

## Worked example

User input: *"build SSO per docs/prd-sso.md, ralph, 8h"*

Drafted prompt skeleton:

```
You are running feature-build-overnight implementing SSO per docs/prd-sso.md.
On iteration 1: read PRD verbatim, decompose into stories, write PLAN.md.
Then process stories in dependency order.

<overnight_contract>... (14 universal clauses with defaults)</overnight_contract>
<prd_decomposition_gate>...</prd_decomposition_gate>
<acceptance_criteria_checklist>...</acceptance_criteria_checklist>
<behavior_preservation_invariant>...</behavior_preservation_invariant>

<execution>... (ralph)</execution>

<output_format>
  <stop_rules>
    Stop when: (a) all stories in PLAN.md status=DONE AND
    `pytest tests/integration/test_sso.py` exit 0 AND PR opened; (b) soft cap;
    (c) drift; (d) ambiguity (e.g. PRD silent on edge case).
    Always: leave PLAN.md with explicit per-story status, BACKLOG.md with anything
    deferred, ROOT_CAUSE.md absent (this is feature-build, not bug-hunt).
  </stop_rules>
</output_format>
```

## Failure modes addressed

- Architecture-by-agent (refuse without PRD; PRD must have acceptance criteria)
- Scope creep across the codebase (C4 + behavior_preservation_invariant)
- Partial stories shipping as "done" (acceptance_criteria_checklist per-story)
- Hallucinated completion (C3 + per-story test_command exit 0)
- Drift over 8h (PRD re-read every 10 iterations per C4)
