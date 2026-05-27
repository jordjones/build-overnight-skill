---
category: bug-hunt-overnight
runtime: ralph
budget_hours: 6
cost_ceiling_usd: 30
capability_profile_match: true
model_target: claude-opus-4-7
variables: [PRD_PATH, REPO_ROOT, FAILING_TEST]
created_at: 2026-05-27T05:01:00-04:00
source_input: "test_pro_rated_refund is failing intermittently in CI, looks like a race condition, ralph 6h"
---

You are running `bug-hunt-overnight` on `{{FAILING_TEST}}` (default: `tests/billing/test_invoice.py::test_pro_rated_refund`). The user hypothesizes a race condition; treat that as a hypothesis to test, not as a conclusion. PRD at `{{PRD_PATH}}`; read on iteration 1 and every 10 iterations thereafter.

Goal: the named test passes **50 consecutive times** AND the broader `pytest tests/billing/` suite stays green AND `ROOT_CAUSE.md` is written with the five required sections.

<overnight_contract>
  <cost_ceiling_usd><hard_cap>30</hard_cap><soft_cap>24</soft_cap><on_breach>abort</on_breach></cost_ceiling_usd>
  <time_budget><hard_hours>6</hard_hours><soft_hours>5.4</soft_hours><self_extension>forbidden</self_extension></time_budget>
  <progress_proof><required>commit_sha, diff_stat, test_exit_code, diff_hash, consecutive_pass_count</required></progress_proof>
  <drift_detection><scope_manifest>tests/billing/, src/billing/ (callers only), ROOT_CAUSE.md</scope_manifest><out_of_scope_limit>3</out_of_scope_limit><prd_reread_every_n_iterations>10</prd_reread_every_n_iterations></drift_detection>
  <no_test_weakening><forbidden_patterns>pytest.skip, xfail, test_deletion, mock_of_billing_SUT, hardcoded_expected_outputs, removed_assertions</forbidden_patterns></no_test_weakening>
  <externalized_state><files>PRD.md, PLAN.md, STATE.md, ROOT_CAUSE.md</files><reread_each_iteration>true</reread_each_iteration></externalized_state>
  <partial_credit_handoff><why_stopped_enum>BUDGET|BLOCKED|AMBIGUOUS|RISK|DONE</why_stopped_enum></partial_credit_handoff>
  <worker_judge_separation><verifier_pass>required</verifier_pass><mechanism>in_prompt_second_pass</mechanism></worker_judge_separation>
  <read_only_paths>node_modules, .git/objects, dist, build</read_only_paths>
  <write_scope>src/billing/, tests/billing/, ROOT_CAUSE.md</write_scope>
  <destructive_command_policy><forbidden>git_force_push, prod_db_writes, gh_pr_merge, rm_rf_outside_worktree</forbidden></destructive_command_policy>
  <git_remote_policy><branch_pattern>overnight/{run_id}-bug-hunt-refund-flake</branch_pattern><pr_state>draft</pr_state><pr_title_prefix>[OVERNIGHT]</pr_title_prefix><auto_merge>false</auto_merge></git_remote_policy>
  <credential_scope><scrub_patterns>*PROD*, AWS_*, STRIPE_*, SUPABASE_SERVICE_*</scrub_patterns></credential_scope>
  <secret_scan_gate><pre_commit_scan>required</pre_commit_scan></secret_scan_gate>
  <cache_warming_strategy><cache_hit_target>0.8</cache_hit_target><forbid>timestamps_in_system_prompt, mid_run_tool_swap, mid_run_model_swap</forbid></cache_warming_strategy>
</overnight_contract>

<oscillation_detector>
  <signal>two_consecutive_iterations_produce_diff_hash_X_then_Y_then_X</signal>
  <window>4_iterations</window>
  <on_detection>log oscillation_detected event; write OSCILLATION.md with both diffs; stop_and_handoff with why_stopped=AMBIGUOUS</on_detection>
</oscillation_detector>

<root_cause_tracking>
  <required_artifact>ROOT_CAUSE.md</required_artifact>
  <required_sections>Symptom, Reproduction, Root cause (mechanism, not "added try/except"), Why the test caught it (what guard was missing), What still won't be caught (honest limitation)</required_sections>
  <forbid>fix_without_root_cause_explanation, "this seems to work", "the flake is gone"</forbid>
</root_cause_tracking>

<no_symptom_masking>
  <forbid>mocking the failing module, try/except that swallows the original error, changing the test expectation to match buggy behavior, removing the assertion that catches the bug</forbid>
  <enforcement>pre_commit_diff_scan</enforcement>
</no_symptom_masking>

<execution>
  You run inside the OMC ralph loop. Each iteration the Stop hook re-invokes you with the same PRD. Read STATE.md to determine which hypothesis to test next.
</execution>

<persistence>
  `.overnight/<run-id>/` + git tags. Track in STATE.md:
    HYPOTHESES_OPEN: [...]
    HYPOTHESES_RULED_OUT: [...]
    EVIDENCE_FOR: {hypothesis_id: evidence}
    EVIDENCE_AGAINST: {hypothesis_id: evidence}
    NEXT_PROBE: <one line>
    CONSECUTIVE_PASS_COUNT: <int>
</persistence>

<output_format>
  <stop_rules>
    Stop when: (a) `{{FAILING_TEST}}` passes 50/50 consecutive AND `pytest tests/billing/` exit 0 AND ROOT_CAUSE.md complete AND PR opened; (b) soft cap (5.4h or $24); (c) oscillation detected; (d) drift limit; (e) ambiguity (e.g. fix needs schema migration → RISK, kick to human). Never: mock billing; never wrap in try/except to silence; never change the assertion to "pass for now".
  </stop_rules>

  <morning_review_artifact>
    Write `.overnight/<run-id>/FINAL_REPORT.md` with: ROOT_CAUSE.md inline, hypothesis-elimination log, raw 50-pass test output, before/after stack trace, drift events, cumulative cost.
  </morning_review_artifact>
</output_format>

## Assumptions

- Budget: 6h [user]
- Cost ceiling: $30 [default for bug-hunt]
- Runtime: ralph [user]
- Failing test: `tests/billing/test_invoice.py::test_pro_rated_refund` [user]
- Hypothesis: race condition is a *hypothesis* not a conclusion [reframed]
- Success: 50 consecutive passes + ROOT_CAUSE.md [default]
- Sandbox: Tier-1 worktree [default]
