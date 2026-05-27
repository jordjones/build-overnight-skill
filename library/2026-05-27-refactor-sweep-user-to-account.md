---
category: refactor-sweep-overnight
runtime: ralph
billing_mode: oauth-subscription
budget_hours: 6
cost_ceiling_usd: null
iteration_cap: 150
capability_profile_match: true
model_target: claude-sonnet-4-6
variables: [PRD_PATH, REPO_ROOT, TEST_CMD, OLD_NAME, NEW_NAME]
created_at: 2026-05-27T05:03:00-04:00
source_input: "rename UserService to AccountService across src/, keep tests green, 6h ralph"
---

You are running `refactor-sweep-overnight` to rename `{{OLD_NAME}}` (default: `UserService`) → `{{NEW_NAME}}` (default: `AccountService`) across `src/`. PRD at `{{PRD_PATH}}`; behavior must be preserved — `{{TEST_CMD}}` (default: `pytest -q`) must exit 0 at every checkpoint.

<overnight_contract>
  <cost_ceiling_usd mode="subscription_disabled"><reason>Claude Code OAuth subscription; no per-call USD to enforce</reason><surface_phantom_usd_in_report>false</surface_phantom_usd_in_report><primary_budget_gate>C15 iteration_budget</primary_budget_gate></cost_ceiling_usd>
  <time_budget><hard_hours>6</hard_hours><soft_hours>5.4</soft_hours><self_extension>forbidden</self_extension></time_budget>
  <progress_proof><required>commit_sha, diff_stat, test_exit_code, diff_hash, remaining_old_name_count</required></progress_proof>
  <drift_detection><scope_manifest>src/, tests/</scope_manifest><out_of_scope_limit>3</out_of_scope_limit><prd_reread_every_n_iterations>10</prd_reread_every_n_iterations></drift_detection>
  <no_test_weakening><forbidden_patterns>pytest.skip, xfail, test_deletion, mock_of_SUT, hardcoded_expected_outputs</forbidden_patterns></no_test_weakening>
  <externalized_state><files>PRD.md, PLAN.md, STATE.md</files><reread_each_iteration>true</reread_each_iteration></externalized_state>
  <partial_credit_handoff><why_stopped_enum>BUDGET|BLOCKED|AMBIGUOUS|RISK|DONE</why_stopped_enum></partial_credit_handoff>
  <worker_judge_separation><verifier_pass>required</verifier_pass><mechanism>in_prompt_second_pass</mechanism></worker_judge_separation>
  <read_only_paths>node_modules, .git/objects, dist, build, migrations/</read_only_paths>
  <write_scope>src/, tests/</write_scope>
  <destructive_command_policy><forbidden>git_force_push, prod_db_writes, gh_pr_merge, rm_rf_outside_worktree, schema_migration</forbidden></destructive_command_policy>
  <git_remote_policy><branch_pattern>overnight/{run_id}-rename-userservice</branch_pattern><pr_state>draft</pr_state><pr_title_prefix>[OVERNIGHT]</pr_title_prefix><auto_merge>false</auto_merge></git_remote_policy>
  <credential_scope><scrub_patterns>*PROD*, AWS_*, STRIPE_*, SUPABASE_SERVICE_*</scrub_patterns></credential_scope>
  <secret_scan_gate><pre_commit_scan>required</pre_commit_scan></secret_scan_gate>
  <cache_warming_strategy><cache_hit_target>0.8</cache_hit_target><forbid>timestamps_in_system_prompt, mid_run_tool_swap, mid_run_model_swap</forbid></cache_warming_strategy>
  <iteration_budget><hard_cap>150</hard_cap><soft_cap>120</soft_cap><on_breach>ship_mode_then_abort</on_breach></iteration_budget>
</overnight_contract>

<behavior_preservation_invariant>
  <required_test_command>{{TEST_CMD}}</required_test_command>
  <gate>tests pass before commit AND after commit AND every iteration</gate>
  <forbid>new public API surface, removed public API surface, changed function signatures (excepting renames within scope), new dependencies, semantic changes</forbid>
  <on_violation>abort_iteration, rollback (git reset --hard ckpt-h{N-1}), log_to_FAILURE.md</on_violation>
</behavior_preservation_invariant>

<tests_green_per_checkpoint>
  <cadence>every iteration</cadence>
  <gate>{{TEST_CMD}} exit 0</gate>
  <on_failure>rollback iteration; re-attempt with narrower change; if 3 consecutive failures, abort and log to FAILURE.md</on_failure>
</tests_green_per_checkpoint>

<no_silent_api_change>
  <signal>diff includes class/def/export/pub declarations or removals</signal>
  <on_detection>refuse iteration UNLESS: (a) the change matches the rename pattern from PRD.md, OR (b) the change is internal-only (private, _underscore, file-local)</on_detection>
</no_silent_api_change>

<execution>
  You run inside the OMC ralph loop. Each iteration the Stop hook re-invokes you. Read STATE.md for remaining files; pick the next file to touch; rename; run {{TEST_CMD}}; commit + tag if green; rollback if not.
</execution>

<persistence>
  `.overnight/<run-id>/` + git tags. STATE.md tracks:
    REMAINING_REFS: count from `grep -rn "{{OLD_NAME}}" src/ | wc -l`
    FILES_TOUCHED: list
    ROLLBACKS: count + reason
</persistence>

<output_format>
  <stop_rules>
    Stop when: (a) `grep -rn "{{OLD_NAME}}" src/` returns zero AND `{{TEST_CMD}}` exit 0 AND PR opened; (b) soft cap; (c) any iteration fails tests 3x in a row; (d) drift; (e) silent API change attempted. Never: change behavior; never break a test instead of finding the real call site; never widen scope to "while I'm here".
  </stop_rules>

  <morning_review_artifact>
    Write `.overnight/<run-id>/FINAL_REPORT.md` with: rename diff stat, files touched, rollback log, before/after `{{TEST_CMD}}` output, remaining refs (should be 0), drift events.
  </morning_review_artifact>
</output_format>

## Assumptions

- Budget: 6h [user]
- Billing mode: oauth-subscription [user; ANTHROPIC_API_KEY unset; using Claude Code OAuth]
- Cost ceiling: N/A under subscription
- Iteration cap: 150 [default; ~25 iter/hr × 6h]
- Runtime: ralph [user]
- Old name: `UserService` [user]
- New name: `AccountService` [user]
- Test command: `pytest -q` [default; user confirms in interview]
- Scope: `src/` and `tests/` only [user; matches default for behavior-preserving refactor]
- No schema migrations [refused at draft-time]
