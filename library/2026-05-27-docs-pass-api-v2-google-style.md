---
category: docs-pass-overnight
runtime: ralph
billing_mode: direct-api
budget_hours: 3
cost_ceiling_usd: 15
iteration_cap: 75
capability_profile_match: true
model_target: claude-haiku-4-5-20251001
variables: [PRD_PATH, REPO_ROOT, TARGET_DIR]
created_at: 2026-05-27T05:04:00-04:00
source_input: "add google-style docstrings with examples to every public function in src/api/v2, 3h"
---

You are running `docs-pass-overnight` to add Google-style docstrings with examples to every public function in `{{TARGET_DIR}}` (default: `src/api/v2/`). PRD at `{{PRD_PATH}}`.

**Iteration 1 protocol:**
1. Read 5 random existing doc files in the repo. Extract: heading style, parameter format, example format, tone register.
2. Write `STYLE.md` describing the inferred convention.
3. Verify every targeted function's signature by grep; assemble PLAN.md with one row per public function.

**Subsequent iterations:** process functions in PLAN.md order; every claim links back to source.

<overnight_contract>
  <cost_ceiling_usd><hard_cap>15</hard_cap><soft_cap>12</soft_cap><on_breach>abort</on_breach></cost_ceiling_usd>
  <time_budget><hard_hours>3</hard_hours><soft_hours>2.7</soft_hours><self_extension>forbidden</self_extension></time_budget>
  <progress_proof><required>commit_sha, diff_stat, test_exit_code, diff_hash, docstrings_added_count</required></progress_proof>
  <drift_detection><scope_manifest>src/api/v2/ docstrings only</scope_manifest><out_of_scope_limit>3</out_of_scope_limit><prd_reread_every_n_iterations>10</prd_reread_every_n_iterations></drift_detection>
  <no_test_weakening><forbidden_patterns>pytest.skip, xfail, test_deletion, mock_of_SUT</forbidden_patterns></no_test_weakening>
  <externalized_state><files>PRD.md, PLAN.md, STATE.md, STYLE.md</files><reread_each_iteration>true</reread_each_iteration></externalized_state>
  <partial_credit_handoff><why_stopped_enum>BUDGET|BLOCKED|AMBIGUOUS|RISK|DONE</why_stopped_enum></partial_credit_handoff>
  <worker_judge_separation><verifier_pass>required</verifier_pass><mechanism>in_prompt_second_pass</mechanism></worker_judge_separation>
  <read_only_paths>node_modules, .git/objects, dist, build, tests/</read_only_paths>
  <write_scope>src/api/v2/ docstrings only (no logic changes)</write_scope>
  <destructive_command_policy><forbidden>git_force_push, prod_db_writes, gh_pr_merge, rm_rf_outside_worktree</forbidden></destructive_command_policy>
  <git_remote_policy><branch_pattern>overnight/{run_id}-docs-api-v2</branch_pattern><pr_state>draft</pr_state><pr_title_prefix>[OVERNIGHT]</pr_title_prefix><auto_merge>false</auto_merge></git_remote_policy>
  <credential_scope><scrub_patterns>*PROD*, AWS_*, STRIPE_*, SUPABASE_SERVICE_*</scrub_patterns></credential_scope>
  <secret_scan_gate><pre_commit_scan>required</pre_commit_scan></secret_scan_gate>
  <cache_warming_strategy><cache_hit_target>0.8</cache_hit_target><forbid>timestamps_in_system_prompt, mid_run_tool_swap, mid_run_model_swap</forbid></cache_warming_strategy>
  <iteration_budget><hard_cap>75</hard_cap><soft_cap>60</soft_cap><on_breach>ship_mode_then_abort</on_breach></iteration_budget>
</overnight_contract>

<no_hallucinated_signatures>
  <gate>every documented signature must grep to a real definition in src/api/v2/</gate>
  <enforcement>per_doc_assertion via grep before commit</enforcement>
  <forbid>inventing parameters, inventing return types, inventing exceptions, inventing function names, inventing module paths</forbid>
  <on_violation>abort_iteration, log file:line in FAILURE.md</on_violation>
</no_hallucinated_signatures>

<source_link_requirement>
  <every_claim>"Function X does Y" → link to src/api/v2/<file>:<line>; "Module Z exports A, B, C" → link to grep result; "Error E is raised when..." → link to the raise statement</every_claim>
  <enforcement>pre_commit scan for assertion-without-link patterns</enforcement>
</source_link_requirement>

<existing_style_inference>
  <required_iteration_1>read 5 random existing doc files; extract heading style, parameter format, example format, tone register; write STYLE.md; consult STYLE.md on every subsequent iteration</required_iteration_1>
</existing_style_inference>

<execution>
  You run inside the OMC ralph loop. Each iteration the Stop hook re-invokes you. Read PLAN.md for remaining functions; document one at a time; commit per function or per file (your choice for cache hygiene).
</execution>

<persistence>
  `.overnight/<run-id>/` + git tags. STATE.md tracks: PUBLIC_FUNCTIONS_TOTAL, DOCUMENTED_COUNT, STYLE_DEVIATIONS_FOUND.
</persistence>

<output_format>
  <stop_rules>
    Stop when: (a) every public function in `{{TARGET_DIR}}` has a docstring matching STYLE.md AND grep verifies zero hallucinated signatures AND PR opened; (b) soft cap (2.7h or $12); (c) drift (e.g. started touching src/api/v1/); (d) ambiguity (e.g. function does multiple things, can't summarize without misleading). Never: invent signatures; never document non-existent code; never modify code to make docs accurate (that's feature-build).
  </stop_rules>

  <morning_review_artifact>
    Write `.overnight/<run-id>/FINAL_REPORT.md` with: total functions, docstrings added, STYLE.md inline, sample of 3 documented functions, grep-verification log proving no hallucinated signatures, drift events.
  </morning_review_artifact>
</output_format>

## Assumptions

- Budget: 3h [user]
- Billing mode: direct-api [user; ANTHROPIC_API_KEY set]
- Cost ceiling: $15 [default for docs-pass — smallest of all categories]
- Iteration cap: 75 [default; ~25 iter/hr × 3h]
- Runtime: ralph [user]
- Target: `src/api/v2/` public functions only [user]
- Style: Google-style with examples [user]
- STYLE.md generated from 5 existing doc files [default]
- Tests stay green (docs-only changes shouldn't touch behavior) [default]
- Model: Haiku 4.5 [default for docs — well within capability, cheapest]
