---
category: research-deep-overnight
capability_profile:
  needs_cross_iteration_memory: true
  needs_parallel_subagents: true
  expected_idle_periods: medium
  destructive_operations: never
  budget_hours_typical: 4
  state_volume: high
suggested_runtime: ralph
suggested_budget_hours: 4
suggested_budget:
  direct_api_usd: 20
  oauth_iterations: 100
---

# research-deep-overnight

Long-horizon web/code research synthesis. Tighter $20 cost ceiling because external search APIs (Firecrawl, Tavily, Exa) burn credits independent of LLM cost. **Refuses to draft for source-fabrication patterns** — every cited URL must be retrieved, not invented.

## When to use

**Signals:** the research question is bounded (single topic, defined sub-questions), the deliverable is a structured report (not an open-ended "find interesting things"), the user can name the sources of truth (which corpora, which date ranges).

**Counter-signals:** "find everything about X" (too unbounded), the question requires synthesis the agent cannot verify (e.g., academic claims requiring expert judgment), the answer is in private/paywalled sources.

**Routes elsewhere:**
- "Research and IMPLEMENT" → research first (this), feature-build-overnight after
- "Find me the best library for X" → use `/build-prompt` research-report category (sync, faster)
- "Build a literature review" → use the `deep-research` skill (more rigorous citation tracking)

## Question bank (≤5 questions, ranked by leverage)

1. **What's the research question?** Required, bounded. *Example: "What are the documented 2026 best practices for LLM agent retry policies on rate-limit errors?"*
2. **What does the deliverable look like?** Structured report with sections, comparison table, executive summary, or all? Default: report at `RESEARCH_REPORT.md` with: Question, Method, Findings, Sources, Confidence.
3. **What sources are in/out of scope?** Default in: anthropic.com/news, anthropic.com/engineering, arxiv.org, vendor docs, 2026-dated blog posts. Default out: Twitter/X (low reliability), undated content, paywalled academic.
4. **Cost ceiling?** Default $20 hard / $16 soft (tighter than the universal $40 because of external API burn). Confirm if user wants higher.
5. **Runtime?** Required. Default: `ralph` (sequential, with sub-agent dispatch for parallel sub-queries via `ultrawork` or similar).

## Default assumptions

- `<write_scope>`: research output goes to `.overnight/<run-id>/RESEARCH_REPORT.md` + `artifacts/sources/`
- `<time_budget>`: `hard_hours=4, soft_hours=3.6`
- `<cost_ceiling_usd>`: `hard=20, soft=16`
- External API spend tracked separately in `COST.json` (Firecrawl credits, Tavily credits, Exa credits)
- Model: `claude-sonnet-4-6` for synthesis; `claude-opus-4-7` for the final report draft only

## Category-specific mitigation clauses

In addition to the universal `<overnight_contract>` (C1–C14):

```xml
<no_source_fabrication>
  <gate>every cited URL must have been retrieved (firecrawl_scrape, tavily_extract, or curl with HTTP 200)</gate>
  <enforcement>per_citation_verification before final report</enforcement>
  <forbid>
    - URLs constructed by pattern-matching (e.g. "https://example.com/blog/topic-i-want")
    - quotes attributed to a source not in artifacts/sources/
    - paraphrases without per-claim source link
    - "I recall reading that..."
    - inventing author names or publication dates
  </forbid>
  <on_violation>strip the unverified claim, log to FAILURE.md, do not silently fix</on_violation>
</no_source_fabrication>

<citation_format>
  <inline>
    "<claim>" (Source N: <one-line>)
  </inline>
  <citations_list>
    N. <Author/Org>. "<Title>." <Publication>. <Date>. <URL>. Retrieved <YYYY-MM-DD>.
  </citations_list>
  <required>retrieval date on every citation (sources change)</required>
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
```

## Template scaffold reference

Extends universal. Adds the four clauses above. RESEARCH_REPORT.md is the deliverable; STATE.md tracks per-question status and per-source credit usage.

## Worked example

User input: *"research 2026 best practices for LLM agent retry policies on rate limits, ralph, 4h"*

Drafted prompt skeleton:

```
You are running research-deep-overnight on "2026 LLM agent retry policies for rate limits."
PRD.md: a structured RESEARCH_REPORT.md at .overnight/<run-id>/ with sections
Question, Method, Findings (HIGH/MED/LOW confidence per finding), Comparison Table,
Sources (with retrieval dates).

<overnight_contract>... (14 universal clauses with research budget=4h, ceiling=$20)</overnight_contract>
<no_source_fabrication>... per-citation retrieval verification</no_source_fabrication>
<citation_format>... numbered, with retrieval dates</citation_format>
<external_api_budget>Firecrawl 50, Tavily 30, Exa 20</external_api_budget>
<confidence_marking>HIGH/MEDIUM/LOW required per finding</confidence_marking>

<execution>... (ralph)</execution>

Method (record progress in STATE.md):
  SUB_QUESTIONS_OPEN: [...]
  SUB_QUESTIONS_ANSWERED: [...]
  SOURCES_RETRIEVED: <count and total credits used>
  CONFIDENCE_DISTRIBUTION: {HIGH: N, MED: N, LOW: N}

<output_format>
  <stop_rules>
    Stop when: (a) RESEARCH_REPORT.md complete with all sub-questions covered
    AND every citation verified AND PR opened; (b) soft cap on $ or time;
    (c) external API budget exhausted; (d) ambiguity (e.g. sources contradict
    and require human adjudication). Never: invent sources; never strip confidence
    tags; never claim HIGH on 1 source.
  </stop_rules>
</output_format>
```

## Failure modes addressed

- Source fabrication / invented URLs (no_source_fabrication with per-citation retrieval gate)
- Confident wrongness (confidence_marking + HIGH requires 3+ sources)
- External API cost surprise (external_api_budget; tracks Firecrawl/Tavily/Exa credits separately from LLM cost)
- Scope creep into related-but-different topics (C4 + bounded sub-questions list)
- Hallucinated paraphrases of real sources (every claim links to artifacts/sources/<file>)
