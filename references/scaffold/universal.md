# Universal scaffold — 15 mandatory overnight clauses (C1–C15)

Every prompt drafted by `/build-overnight` MUST emit all 15 clauses below as a `<overnight_contract>` block, in addition to category-specific mitigation clauses and the standard `<stop_rules>` mandated by build-prompt.

Defaults shown are the v1 baseline (user-confirmed in convention Phase 0.6). The interview may override them per run; the contract always emits *some* value.

**Billing-mode awareness (rc2):** Clause C1 (`<cost_ceiling_usd>`) is **conditional on billing mode**. The skill asks the user in Step 4 for `billing_mode ∈ {direct-api, oauth-subscription}` and emits the appropriate variant. Under `oauth-subscription`, USD costs are NOT enforceable from inside the loop (flat-rate subscription; no per-call cost surfaces reliably to the agent), so C1 is emitted as a `subscription_disabled` marker and C15 `<iteration_budget>` becomes the primary stop-on-budget gate.

```xml
<overnight_contract>

  <!-- C1: cost discipline (direct-api variant) -->
  <cost_ceiling_usd>
    <hard_cap>40</hard_cap>
    <soft_cap>32</soft_cap>
    <on_breach>abort</on_breach>
    <on_soft_breach>enter_ship_mode</on_soft_breach>
    <accumulator>read response.usage; cumulate cost_usd_iter from list prices</accumulator>
  </cost_ceiling_usd>

  <!-- C1: cost discipline (oauth-subscription variant; emitted INSTEAD of the above) -->
  <!--
  <cost_ceiling_usd mode="subscription_disabled">
    <reason>flat-rate Claude Code Pro/Max subscription; no per-call USD to enforce</reason>
    <surface_phantom_usd_in_report>false</surface_phantom_usd_in_report>
    <primary_budget_gate>C15 iteration_budget</primary_budget_gate>
  </cost_ceiling_usd>
  -->

  <!-- C2: wall-clock discipline -->
  <time_budget>
    <hard_hours>8</hard_hours>
    <soft_hours>7.2</soft_hours>
    <self_extension>forbidden</self_extension>
    <on_soft_breach>enter_ship_mode</on_soft_breach>
    <on_hard_breach>graceful_shutdown_then_force_kill</on_hard_breach>
  </time_budget>

  <!-- C3: verifiable progress -->
  <progress_proof>
    <required>commit_sha, diff_stat, test_exit_code, diff_hash</required>
    <forbid>summary_only_status, fabricated_test_output, DONE_without_evidence</forbid>
  </progress_proof>

  <!-- C4: drift detection -->
  <drift_detection>
    <scope_manifest required="true"/>
    <out_of_scope_edits>append_to_BACKLOG.md</out_of_scope_edits>
    <out_of_scope_limit>3</out_of_scope_limit>
    <on_limit_breach>abort_with_BACKLOG_handoff</on_limit_breach>
    <prd_reread_every_n_iterations>10</prd_reread_every_n_iterations>
  </drift_detection>

  <!-- C5: integrity of the test suite -->
  <no_test_weakening>
    <forbidden_patterns>pytest.skip, xfail, @unittest.skip, test_*deleted, mock_of_SUT, hardcoded_expected_outputs</forbidden_patterns>
    <enforcement>pre_commit_scan</enforcement>
  </no_test_weakening>

  <!-- C6: externalized state, no summary lineage -->
  <externalized_state>
    <files>PRD.md, PLAN.md, STATE.md</files>
    <reread_each_iteration>true</reread_each_iteration>
    <forbid>relying_on_context_summary_for_goal</forbid>
  </externalized_state>

  <!-- C7: structured handoff on any stop -->
  <partial_credit_handoff>
    <why_stopped_enum>BUDGET | BLOCKED | AMBIGUOUS | RISK | DONE</why_stopped_enum>
    <required>files_dirty_list, last_good_checkpoint_tag, resume_command, recommended_next_action</required>
  </partial_credit_handoff>

  <!-- C8: writer/verifier separation -->
  <worker_judge_separation>
    <verifier_pass>required</verifier_pass>
    <mechanism>in_prompt_second_pass | dispatched_sub_agent | managed_agents_outcomes_grader</mechanism>
    <forbid>self_approval_in_same_active_context</forbid>
  </worker_judge_separation>

  <!-- C9: filesystem scope -->
  <read_only_paths>node_modules, .git/objects, dist, build, vendor, .venv, target</read_only_paths>
  <write_scope>src/, tests/</write_scope>

  <!-- C10: blast radius -->
  <destructive_command_policy>
    <forbidden>git_force_push, prod_db_writes, gh_pr_merge, rm_rf_outside_worktree, drop_table, truncate</forbidden>
    <on_violation>refuse_and_log</on_violation>
  </destructive_command_policy>

  <!-- C11: git remote policy -->
  <git_remote_policy>
    <branch_pattern>overnight/{run_id}-{slug}</branch_pattern>
    <pr_state>draft</pr_state>
    <pr_title_prefix>[OVERNIGHT]</pr_title_prefix>
    <pr_label>overnight-run</pr_label>
    <auto_merge>false</auto_merge>
    <force_push>forbidden</force_push>
  </git_remote_policy>

  <!-- C12: credential scope -->
  <credential_scope>
    <scrub_patterns>*PROD*, AWS_*, STRIPE_*, SUPABASE_SERVICE_*, *_PRIVATE_KEY, *_SECRET</scrub_patterns>
    <on_detected_prod_creds>refuse_to_draft</on_detected_prod_creds>
  </credential_scope>

  <!-- C13: leak prevention -->
  <secret_scan_gate>
    <pre_commit_scan>required</pre_commit_scan>
    <tool>gitleaks_or_trufflehog</tool>
    <on_match>abort_commit</on_match>
  </secret_scan_gate>

  <!-- C14: cache hygiene (cost AND latency discipline; mode-agnostic) -->
  <cache_warming_strategy>
    <cache_hit_target>0.8</cache_hit_target>
    <forbid>timestamps_in_system_prompt, mid_run_tool_swap, mid_run_model_swap</forbid>
    <prefer>static_breakpoint_above_tools, append_only_message_history</prefer>
    <note>Latency and cache savings apply under both billing modes. Under subscription, the user does not see USD savings but does see faster iteration.</note>
  </cache_warming_strategy>

  <!-- C15: iteration cap (rc2; primary budget gate under subscription, secondary under direct-api) -->
  <iteration_budget>
    <hard_cap>200</hard_cap>
    <soft_cap>160</soft_cap>
    <on_breach>ship_mode_then_abort</on_breach>
    <on_soft_breach>enter_ship_mode</on_soft_breach>
    <rationale>Sized at ~25 iter/hr × 8h. User-overridable per category and per run. Under oauth-subscription this is the primary stop-on-budget gate.</rationale>
  </iteration_budget>

</overnight_contract>
```

## Cross-references

- Runtime-specific variants for clauses C2 (`<time_budget>`), C6 (`<externalized_state>`), C7 (`<partial_credit_handoff>`), C8 (`<worker_judge_separation>`) live in `references/meta/runtime-adaptation.md`. On `runtime=managed-agents`, defer the persistence and completion clauses to native session primitives (suppress redundant laptop scaffolding per F33).
- Category-specific mitigation clauses are added by each category file at `references/categories/*.md` (e.g., `<oscillation_detector>` for bug-hunt, `<behavior_preservation_invariant>` for refactor-sweep).
- Standard build-prompt `<stop_rules>` clause is still mandatory and lives alongside this contract.

## Why every clause is universal (not optional)

The convention's CONVERGENT_FINDINGS.md (F1–F14, F27, F29, F31) shows 3+ independent voices agreed each of these is necessary. Source attribution for each clause is in `references/research-distilled.md`. C15 (`<iteration_budget>`) was added in rc2 to gate budget under subscription billing where USD enforcement is structurally unavailable; see `references/meta/budget-and-telemetry.md` for the mode-conditional kill-switch layering and `~/.claude/plans/jiggly-marinating-parnas-rc2-audit.md` for the audit that drove the change.
