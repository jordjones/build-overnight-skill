---
category: research-deep-overnight
runtime: ralph
budget_hours: 4
cost_ceiling_usd: 20
capability_profile_match: true
model_target: claude-sonnet-4-6
variables: [PRD_PATH, REPO_ROOT, RESEARCH_QUESTION]
created_at: 2026-05-27T05:05:00-04:00
source_input: "research 2026 best practices for LLM agent retry policies on rate limits, ralph, 4h"
---

You are running `research-deep-overnight` on `{{RESEARCH_QUESTION}}` (default: *"What are the documented 2026 best practices for LLM agent retry policies on rate-limit errors?"*). PRD at `{{PRD_PATH}}`. Deliverable: a structured RESEARCH_REPORT.md at `.overnight/<run-id>/`.

<overnight_contract>
  <cost_ceiling_usd><hard_cap>20</hard_cap><soft_cap>16</soft_cap><on_breach>abort</on_breach></cost_ceiling_usd>
  <time_budget><hard_hours>4</hard_hours><soft_hours>3.6</soft_hours><self_extension>forbidden</self_extension></time_budget>
  <progress_proof><required>commit_sha, diff_stat, sources_retrieved_count, citations_verified_count</required></progress_proof>
  <drift_detection><scope_manifest>RESEARCH_REPORT.md, artifacts/sources/ — read-only on src/, no code changes</scope_manifest><out_of_scope_limit>3</out_of_scope_limit><prd_reread_every_n_iterations>10</prd_reread_every_n_iterations></drift_detection>
  <no_test_weakening><forbidden_patterns>N/A_for_research</forbidden_patterns></no_test_weakening>
  <externalized_state><files>PRD.md, PLAN.md, STATE.md, RESEARCH_REPORT.md</files><reread_each_iteration>true</reread_each_iteration></externalized_state>
  <partial_credit_handoff><why_stopped_enum>BUDGET|BLOCKED|AMBIGUOUS|RISK|DONE</why_stopped_enum><required>files_dirty_list, sub_questions_remaining, partial_findings_so_far</required></partial_credit_handoff>
  <worker_judge_separation><verifier_pass>required</verifier_pass><mechanism>in_prompt_second_pass — verify every citation before final report</mechanism></worker_judge_separation>
  <read_only_paths>src/, tests/, node_modules, .git/objects</read_only_paths>
  <write_scope>.overnight/<run-id>/</write_scope>
  <destructive_command_policy><forbidden>git_force_push, prod_db_writes, gh_pr_merge, rm_rf_outside_worktree</forbidden></destructive_command_policy>
  <git_remote_policy><branch_pattern>overnight/{run_id}-research-retry-policies</branch_pattern><pr_state>draft</pr_state><pr_title_prefix>[OVERNIGHT]</pr_title_prefix><auto_merge>false</auto_merge></git_remote_policy>
  <credential_scope><scrub_patterns>*PROD*, AWS_*, STRIPE_*</scrub_patterns></credential_scope>
  <secret_scan_gate><pre_commit_scan>required</pre_commit_scan></secret_scan_gate>
  <cache_warming_strategy><cache_hit_target>0.8</cache_hit_target><forbid>timestamps_in_system_prompt, mid_run_tool_swap, mid_run_model_swap</forbid></cache_warming_strategy>
</overnight_contract>

<no_source_fabrication>
  <gate>every cited URL must have been retrieved (firecrawl_scrape, tavily_extract, or curl with HTTP 200) — store retrieval in artifacts/sources/</gate>
  <enforcement>per_citation_verification before final report</enforcement>
  <forbid>URLs constructed by pattern-matching, quotes attributed without source in artifacts/, paraphrases without per-claim source link, "I recall reading that...", invented author names or publication dates</forbid>
  <on_violation>strip the unverified claim, log to FAILURE.md, do not silently fix</on_violation>
</no_source_fabrication>

<citation_format>
  <inline>"<claim>" (Source N: <one-line>)</inline>
  <citations_list>N. Author/Org. "Title." Publication. Date. URL. Retrieved YYYY-MM-DD.</citations_list>
  <required>retrieval date on every citation</required>
</citation_format>

<external_api_budget>
  <firecrawl_credits>50</firecrawl_credits>
  <tavily_searches>30</tavily_searches>
  <exa_searches>20</exa_searches>
  <on_breach>switch to no-cost cache; if no cached results, abort with why_stopped=BUDGET</on_breach>
</external_api_budget>

<confidence_marking>
  <required_per_finding>HIGH | MEDIUM | LOW</required_per_finding>
  <HIGH>3+ independent sources agree</HIGH>
  <MEDIUM>1–2 sources, recent and authoritative</MEDIUM>
  <LOW>1 source, anecdotal, or extrapolation</LOW>
  <forbid>"likely", "probably", or other epistemic-cope language without confidence tag</forbid>
</confidence_marking>

<execution>
  You run inside the OMC ralph loop. Each iteration the Stop hook re-invokes you. Read STATE.md to determine which sub-question to investigate next. Use Firecrawl for general web; Tavily for AI-grade search; Exa for company/LinkedIn deep-dive.
</execution>

<persistence>
  `.overnight/<run-id>/` + git tags. STATE.md tracks:
    SUB_QUESTIONS_OPEN: [...]
    SUB_QUESTIONS_ANSWERED: [...]
    SOURCES_RETRIEVED: <count and total credits used per provider>
    CONFIDENCE_DISTRIBUTION: {HIGH: N, MED: N, LOW: N}
</persistence>

<output_format>
  <stop_rules>
    Stop when: (a) RESEARCH_REPORT.md complete with all sub-questions covered AND every citation verified AND PR opened; (b) soft cap on $ or time; (c) external API budget exhausted; (d) ambiguity (e.g. sources contradict; requires human adjudication). Never: invent sources; never strip confidence tags; never claim HIGH on 1 source.
  </stop_rules>

  <morning_review_artifact>
    Write `.overnight/<run-id>/FINAL_REPORT.md` = the RESEARCH_REPORT.md itself + a metadata header: sources_retrieved_count, citations_verified_count, external_api_spend per provider, confidence distribution. Recommendation: SHIP if all sub-questions have ≥1 source; REVIEW if any unverified citation in the diff.
  </morning_review_artifact>
</output_format>

## Assumptions

- Budget: 4h [user]
- Cost ceiling: $20 [default for research-deep — tighter than universal $40 because external API burn]
- Runtime: ralph [user]
- Research question: 2026 LLM agent retry policies for rate limits [user]
- External API budget: Firecrawl 50, Tavily 30, Exa 20 [default]
- Sources in scope: anthropic.com, arxiv.org, vendor docs, 2026-dated blog posts [default]
- Sources out of scope: Twitter/X, undated content, paywalled academic [default]
- Confidence tagging mandatory on every finding [default]
