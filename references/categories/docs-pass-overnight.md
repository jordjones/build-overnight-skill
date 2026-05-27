---
category: docs-pass-overnight
capability_profile:
  needs_cross_iteration_memory: false
  needs_parallel_subagents: false
  expected_idle_periods: short
  destructive_operations: rare
  budget_hours_typical: 3
  state_volume: low
suggested_runtime: ralph
suggested_budget_hours: 3
suggested_budget:
  direct_api_usd: 15
  oauth_iterations: 75
---

# docs-pass-overnight

Generate or refresh documentation for an existing codebase area. **Refuses to draft for hallucinated API signatures** — every documented signature must be sourced from the actual code.

## When to use

**Signals:** there is undocumented or stale documentation, the code is stable (not changing in parallel), there's a doc target (README section, API reference, runbook), the user can verbalize success ("every public function in `src/api/` has a docstring with examples").

**Counter-signals:** "write a tutorial about how the system works" (too vague — refuse, ask for a target audience and scope), the code is in flux (parallel changes will conflict), docs require live system access (out of overnight scope).

**Routes elsewhere:**
- "Document a NEW feature I'm about to build" → `feature-build-overnight` includes doc obligation
- "Refactor and document" → `refactor-sweep-overnight` first, then this
- "Rewrite the docs to be better" → too vague; ask for a measurable target

## Question bank (≤5 questions, ranked by leverage)

1. **What's the doc target?** Required, concrete. *Example: "every public function in `src/api/v2/` gets a Google-style docstring with at least one usage example"*
2. **Where do docs live?** Inline docstrings, `docs/` folder, README sections, or all of the above? Default: matches existing convention.
3. **What's the source-link requirement?** Every claim must link back to a source-of-truth. Default: every documented function signature must `grep` to a real definition in `src/`.
4. **Tone and audience?** Internal devs, public API consumers, both? Default: matches existing doc tone.
5. **Runtime?** Required. Default: `ralph` (sequential, low state).

## Default assumptions

- `<write_scope>`: docstrings in `src/` + `docs/` + README.md
- `<time_budget>`: `hard_hours=3, soft_hours=2.7`
- `<cost_ceiling_usd>`: `hard=15, soft=12` (smallest of all categories — docs are cheap)
- Existing doc style is preserved (the agent reads 5 existing docs first to infer convention)
- Model: `claude-haiku-4-5-20251001` (docs are well within Haiku's capability)

## Category-specific mitigation clauses

In addition to the universal `<overnight_contract>` (C1–C14):

```xml
<no_hallucinated_signatures>
  <gate>every documented signature must grep to a real definition in $WRITE_SCOPE</gate>
  <enforcement>per_doc_assertion via grep before commit</enforcement>
  <forbid>
    - inventing parameters that don't exist
    - inventing return types not actually returned
    - inventing exceptions not actually raised
    - inventing function names not in the codebase
    - inventing module paths
  </forbid>
  <on_violation>abort_iteration, log file+line in FAILURE.md</on_violation>
</no_hallucinated_signatures>

<source_link_requirement>
  <every_claim>
    - "Function X does Y" → link to src/<file>:<line>
    - "Module Z exports A, B, C" → link to grep result
    - "Error E is raised when..." → link to the raise statement
  </every_claim>
  <enforcement>pre_commit scan for assertion-without-link patterns</enforcement>
</source_link_requirement>

<existing_style_inference>
  <required_iteration_1>
    read 5 random existing doc files;
    extract: heading style, parameter format, example format, tone register;
    write STYLE.md describing the inferred convention;
    write all new docs to match
  </required_iteration_1>
</existing_style_inference>
```

## Template scaffold reference

Extends universal. Adds the three clauses above. STYLE.md (output of iteration 1) is consulted on every subsequent iteration.

## Worked example

User input: *"add google-style docstrings with examples to every public function in src/api/v2, 3h"*

Drafted prompt skeleton:

```
You are running docs-pass-overnight to add Google-style docstrings with examples
to every public function in src/api/v2/.
PRD.md: every `def <name>` not starting with `_` in src/api/v2/**/*.py has
a docstring with Args, Returns, Raises (if applicable), and ≥1 Example block.

<overnight_contract>... (14 universal clauses with docs budget=3h, ceiling=$15)</overnight_contract>
<no_hallucinated_signatures>... grep-verify per assertion</no_hallucinated_signatures>
<source_link_requirement>... link every claim to src/api/v2/...</source_link_requirement>
<existing_style_inference>... iteration 1 writes STYLE.md from existing docs</existing_style_inference>

<execution>... (ralph)</execution>

<output_format>
  <stop_rules>
    Stop when: (a) every public function in src/api/v2/ has a docstring matching
    STYLE.md AND grep verifies no hallucinated signatures AND PR opened;
    (b) soft cap; (c) drift (e.g. doc-writing started touching src/api/v1/);
    (d) ambiguity. Never: invent signatures; never document what doesn't exist
    in code; never modify code to make docs accurate (that's a feature-build).
  </stop_rules>
</output_format>
```

## Failure modes addressed

- Hallucinated API signatures (no_hallucinated_signatures + per-assertion grep)
- "This documents what I wish the code did" (source_link_requirement + grep verification)
- Style drift across N functions (existing_style_inference iteration 1 + STYLE.md re-read)
- Scope creep into modifying code (C4 + write_scope explicitly docs-only)
- Tutorial-style sprawl (PRD scope keeps it bounded to existing functions)
