# Quality Rubric: Shared 5-Dimension Scoring

This rubric is the **external scorer** for the critique-and-revise step (SKILL.md Step 6). A single self-refine turn without an external rubric drifts; pair every revision with explicit dimension scores. The rubric is the scoring sheet, not advice. Source: https://www.geekwire.com/2026/ai-best-practices-if-at-first-you-dont-succeed-prompt-prompt-again/

The skill self-scores every draft along five dimensions before presenting it to the user. Scoring is a judgment, not a calculation — you don't output numbers to the user, you use them internally to catch weak drafts and revise before showing them.

Each dimension scores **1 (poor) to 5 (strong)**. If any dimension scores **≤2**, revise before presenting. Target is **all dimensions ≥4** for a production-ready draft.

Category files layer a category-specific rubric on top of this shared one. This file covers universal checks; the category file covers "does this specific kind of prompt have what it needs?"

---

## Dimension 1 — Clarity

Is the task stated unambiguously? Would a competent Claude instance reading the refined prompt know exactly what to do without guessing?

- **5** — Task is one sentence, unambiguous, action-verb-led. Scope is explicit. No reasonable reader would interpret it two different ways.
- **4** — Task is clear on first read; minor ambiguity only on edge cases that the success criteria resolve.
- **3** — Task is understandable but requires re-reading. Some words could be interpreted narrowly or broadly.
- **2** — Multiple valid interpretations. The refiner had to guess what the user meant.
- **1** — Task is not actually stated. The prompt describes context without ever saying what Claude should do.

**Auto-fail on Clarity:** any ALL-CAPS emphasis, shouted MUST/NEVER, or "EXTREMELY IMPORTANT"-style scaffolding in the drafted prompt. On Claude 4.x and GPT-5.5 these now over-trigger or get auto-corrected. Rewrite as a positive directive sentence. Source: https://mrprompts.substack.com/p/how-to-prompt-in-2026

## Dimension 2 — Specificity

Are constraints, formats, and success criteria concrete? Does the prompt tell Claude what "done" looks like?

- **5** — Every constraint is quantified or enumerated. Success criteria are checkable. Output format is specified. Non-goals are listed where they matter.
- **4** — Most constraints are concrete. At least one success criterion is present. Minor looseness on output format.
- **3** — Constraints exist but are vague ("keep it short," "make it good"). Success criteria are implied, not stated.
- **2** — "Do a good job" territory. No checkable done-condition.
- **1** — Completely unconstrained. Any output could plausibly satisfy the prompt.

## Dimension 3 — Context

Is the situational and background information sufficient? Does Claude have what it needs to ground the task in reality?

- **5** — Relevant context is present and well-structured (audience, environment, prior work, constraints). Long content placed before instructions. No irrelevant context padding the prompt.
- **4** — Key context is there. Some minor background is missing but can be inferred.
- **3** — Basic context is present but thin. Claude would ask a clarifying question if it could.
- **2** — Context is a keyword dump, not usable grounding. Claude has to guess at situation.
- **1** — No context. The prompt is abstract, floating, detached from any real use.

## Dimension 4 — Completeness

Are all required slots from the category's question bank filled — by user, inference, or default — and is every non-user-provided slot surfaced in the assumptions list?

- **5** — Every slot filled. Every inferred and defaulted slot surfaced in the assumptions list with the correct label. No `{{PLACEHOLDER}}` tokens remain.
- **4** — All required slots filled. One or two optional slots empty but not material.
- **3** — Required slots filled but one assumption is un-surfaced in the assumptions list.
- **2** — A required slot is empty or left as a literal `{{PLACEHOLDER}}` in the draft.
- **1** — Multiple required slots empty. Draft is a skeleton.

**Auto-fail on Completeness:** any drafted prompt missing a `<stop_rules>` clause for an agentic, retrieval-augmented, tool-using, or open-ended category scores ≤2 on Completeness and must be revised. OpenAI's official GPT-5.5 guide treats stop/ask/retry/abstain rules as first-class template fields, not style advice. Source: https://kingy.ai/ai/gpt-5-5-prompting-guide-write-for-outcomes-not-ritual/

## Dimension 5 — Structure

Is the XML / markdown / section layout appropriate for the target? Does the structure serve the model executing the prompt, or is it ornamental?

- **5** — XML tags used consistently and purposefully. Section order matches output target conventions. Long inputs placed before instructions. Output-format block present and specific.
- **4** — Structure is sound. Minor inconsistencies in tag naming or section order.
- **3** — Structured, but some sections feel like filler or out-of-place for the target.
- **2** — Over-structured (every sentence wrapped in a tag) or under-structured (prose blob with no sections).
- **1** — Structure actively hurts readability or contradicts the output target (e.g., heavy XML for a Cursor rules file).

---

## Worked before/after example

**Raw input (dictated):** *"write me something about the nba's load management thing"*

### Before — score of the raw input as if it were the refined prompt

| Dim | Score | Why |
|---|---|---|
| Clarity | 1 | "Something" is not a task. No deliverable shape named. |
| Specificity | 1 | No constraints, no format, no success criteria. |
| Context | 1 | No audience, no purpose, no recency window. |
| Completeness | 1 | No required slots filled for any plausible category. |
| Structure | 1 | No structure at all. |

Total **5/25**. Revise — this is exactly the case the skill exists to solve.

### After — refined prompt (research-report category, analyst-memo depth, sports-industry audience)

```xml
<role>
You are a senior research analyst producing a structured, evidence-grounded report on a sports-industry topic. You inform; you do not advocate.
</role>

<research_question>
What is the current state of NBA load management — its prevalence across the 2024–25 and 2025–26 seasons, the league's policy response, the empirical evidence on its effect on injury rates and player availability, and the commercial and fan-experience consequences for broadcasters and season-ticket holders?
</research_question>

<decision_context>
The user writes a sports-analytics newsletter aimed at industry professionals (team analysts, broadcasters, sports-business readers). This report is input to an upcoming issue on roster management trends.
</decision_context>

<audience_and_depth>
- Audience: sports-industry professionals, informed generalists on NBA operations
- Depth: analyst-memo depth with data points and specific citations
- Target length: 1,500–2,000 words
</audience_and_depth>

<source_constraints>
- Recency: primarily last 24 months; older for policy history
- Preferred: NBA press releases and policy documents, peer-reviewed sports-medicine journals, ESPN / The Athletic / Sports Illustrated with original reporting, official player-tracking data
- Avoid: aggregator takes, Twitter hot-take chains without original reporting
- Paywall posture: okay to cite paywalled, flagged as such
</source_constraints>

<sub_questions>
- How widespread is load management across the league today, and how is it measured?
- What is the empirical evidence on its effect on injury rates and career longevity?
- How has the NBA's policy (Player Participation Policy and successors) evolved, and what has been the compliance response?
- What are the commercial consequences for national broadcasters, local RSNs, and in-arena revenue?
- What do coaches, GMs, and players actually say about the tradeoffs, in on-record quotes?
</sub_questions>

<constraints>
- Every load-bearing claim cited with a verifiable URL.
- Confidence labels on findings: established / emerging / contested.
- No fabricated quotes. If you cannot verify a quote, remove it or paraphrase and cite the paraphrase.
- 2,000 words is a ceiling, not a target.
</constraints>

<output_format>
Markdown report with sections: Executive summary (2–4 sentences), Background, Findings (organized by sub-question with inline citations), Evidence and sources, Open questions, Industry takeaways. Inline numbered citations `[1]` linked to the bibliography.
</output_format>
```

### After — score of the refined prompt

| Dim | Score | Why |
|---|---|---|
| Clarity | 5 | Task is one sentence, scope and deliverable are unambiguous. |
| Specificity | 5 | Word ceiling, confidence labels, citation format, source constraints, sub-questions all concrete. |
| Context | 5 | Audience, decision context, recency window, preferred source types all present. |
| Completeness | 4 | All required research-report slots filled. Some optional slots (specific named domains to prioritize) defaulted — surfaced in assumptions. |
| Structure | 5 | XML tags used purposefully, output format explicit, success/constraints separated. |

Total **24/25**. Ship.

---

## When scoring catches a revise condition

If clarity or specificity scores ≤2, the interview left required slots unfilled — check the answered-slot tracker and either surface the gap as an assumption with `[default]` or ask one more targeted question if a round is still available.

If completeness scores ≤2, a `{{PLACEHOLDER}}` survived into the draft. Find it and fill it from the category's default assumptions or the user's raw input.

If structure scores ≤2, the output target was probably missed — check whether the user named a target (Cursor rules, eval harness, ChatGPT) and consult `references/meta/output-targets.md` for the correct adjustments.

Context is the one dimension where **over-scoring** is a failure mode. A refined prompt with three paragraphs of backstory and one line of task is 5 on context and 2 on clarity. Keep context proportional to task weight.

---

## Interaction with category-specific rubric

This rubric is necessary but not sufficient. Each category file adds 3–5 category-specific checks — the `bug-fix` category requires a regression test, the `research-report` category forbids fabricated citations, the `migration` category requires an explicit rollback path. A draft can score 5 across all five shared dimensions and still fail a category rubric. Run both before finalizing.
