# Interview Loop: The Clarification Methodology

This file is the full specification for the interview loop. SKILL.md holds the condensed version; this file is what you re-read when you need to know how to handle an edge case — a vague answer, a domain-floor category, a user who dictates a mid-interview pivot.

The loop's job is to reach a draftable state with the fewest questions that actually move the refined prompt. Over-asking is the #1 failure mode of prior-art interactive refiners (GPT-Engineer pattern). Under-asking on high-stakes categories is the opposite failure. This file specifies how to balance them.

---

## The algorithm in one page

```
1. Capture the raw input.
2. Classify into one of 36 categories. If confidence is mixed, surface top-two; never more.
3. Load the selected category file.
4. For each slot in the category's question bank:
      Can it be inferred from the raw input or conversation context?
        YES → infer silently; surface in assumptions with [inferred].
        NO  → Is there a safe default in the category's Default assumptions?
              YES → use default; surface in assumptions with [default].
              NO  → add to ask-queue.
5. Rank ask-queue by leverage: "which answer would most change the refined prompt?"
6. Round 1: ask the top 1–3 high-leverage questions.
7. Update slots from answers.
8. If ambiguity remains high AND round-cap (2) not hit AND question-cap (5 total) not hit:
      Round 2: ask the top 1–2 remaining high-leverage questions.
9. Any time during 6–8: if the user utters a bail-out phrase, stop asking; fill remaining
   slots with defaults; surface them; proceed to draft.
10. Any time: if the user gives two consecutive vague answers on the same slot, convert
    that slot to default; never rephrase a third time.
11. Draft. Surface assumptions. Enter review loop — score against the 5-dimension rubric in `references/meta/quality-rubric.md` (external scorer; single self-refine drifts without one). Deliver. Save to library.
```

---

## Classification

**Look at deliverable shape, not keywords.** "Tell me about tariffs" with a newsletter context wants `research-report` — not `qa-factual` even though "tell me" reads like a question. A user who says "review this PR" and pastes code wants `code-review`. A user who says "how should I approach migrating to React 19" wants `planning-strategy`, not `migration`.

**When confidence is high, state the pick and move on.** One sentence: *"This looks like `bug-fix` — observable regression after a recent change, specific stack named. Proceeding."* Do not ask the user to confirm the category when confidence is high; that adds a round without moving the refined prompt.

**When confidence is mixed, offer top-two with one-line rationales.** Never more than two. Common ambiguous pairs:

- `bug-fix` vs. `debugging-session` — real bug in production code vs. flaky/failing test
- `research-report` vs. `summarization` — structured investigation vs. overview of published material
- `refactor` vs. `performance-optimization` — behavior-preserving cleanup vs. measured speedup
- `analysis-reasoning` vs. `research-report` — argument construction vs. evidence gathering
- `planning-strategy` vs. `decision-support` — roadmap vs. picking an already-identified option
- `creative-writing` vs. `roleplay-persona` — self-contained artifact vs. durable dialogue persona
- `code-review` vs. `architecture-design` — critique of a diff vs. design feedback on a doc
- `technical-writing` vs. `documentation-generation` — narrative document vs. reference/runbook/API doc
- `data-extraction` vs. `classification` — pull fields vs. assign labels
- `business-writing` vs. `technical-writing` — audience drives the split; same topic can go either way

**Always allow "neither, it's actually X."** If the user overrides, preserve the raw input and re-run loading with the new category. Do not force them to re-type their idea.

---

## Ask vs. infer vs. default — per slot

This is the core decision. Run it once per slot in the category's question bank **before** composing any questions.

**Infer when:** the user's raw input, the conversation history, or obvious context (open project, mentioned files, recent turns) gives you the answer with high confidence. Silent inference with assumption surfacing is free — the user sees what you decided and can correct it in the review round.

**Default when:** the slot has a safe default in the category file's `Default assumptions` section and the user's input doesn't contradict it. The category owners picked defaults that produce a usable prompt even if they're not perfect for every situation. Trust them.

**Ask when:** neither inference nor default applies AND the slot is high-leverage. "High-leverage" means the answer would meaningfully change the refined prompt — swap the audience, change the template's emphasis, flip a required section on or off. If an answer wouldn't move the refined prompt in any direction, don't ask; default and move on.

**Distribution target:** roughly 70% inferred, 20% defaulted with surfacing, 10% asked. Categories with thinner raw inputs shift the mix toward asking; categories with detailed raw inputs shift toward inferring.

---

## Ranking the ask-queue

Within the queue, order by "which answer would most change the refined prompt."

- An answer that flips the `<audience>` from "execs" to "engineers" changes roughly 30% of the template → high leverage.
- An answer that specifies a word count within an already-narrow band changes roughly 5% of the template → low leverage.
- An answer that toggles a high-stakes section on/off (e.g., `<rollback_plan>` in a migration) → very high leverage.

Ask high-leverage first. If the round cap permits only 1–2 questions, you're asking the most important; if low-leverage questions remain, they defer to defaults.

---

## Hard caps

- **≤2 clarification rounds.** Round 3 is forbidden. If you feel the need for a third round, you're interrogating; default the remaining slots and draft.
- **≤5 questions total across rounds.** Any single interview ending at 5 questions asked is already long; most end at 2–3.
- **≤3 questions per round.** More than 3 causes abandonment (Bing MIMICS finding). Most rounds should be 1–2.

These are ceilings, not targets. The skill rewards brevity.

---

## Question formatting

**Prefer multiple-choice when the choice space is finite and named.** *"Audience: (a) exec brief, (b) analyst memo, (c) engineering deep-dive, (d) other?"* is faster to answer than *"what audience?"* Multiple-choice is a two-keystroke reply; open-ended is a sentence.

**Use open-ended when the choice space is genuinely open** (sub-questions for a research report, symptoms of a bug). In those cases, give an example of what a good answer looks like so the user knows the expected granularity.

**One question at a time when the round has only 1–2 questions.** Batching is only faster when questions are independent and fast to answer. If questions chain ("what stack?" → "what version of that stack?"), ask one at a time.

**Include an "other/none" option on multiple-choice.** Leading-question avoidance — the user must be able to decline every listed option without the system re-asking.

---

## Stopping-criteria rubric (first match wins)

Apply these in order at every decision point about whether to ask another question:

1. **Hard cap reached** — ≤2 rounds, ≤5 total, ≤3 per round. If any cap would be violated by the next question, stop.
2. **Bail-out phrase uttered** — "good enough," "just do it," "just build it," "proceed," "skip," "ship it," "your best guess," "whatever," "doesn't matter," "you decide." Stop asking immediately; fill remaining slots with defaults.
3. **Ambiguity judged low** — if your sense is that asking one more question wouldn't meaningfully change the refined prompt, stop and draft.
4. **Trivial-input fast-path** — the raw input already fills ≥80% of required slots AND drafts sampled from the current state wouldn't diverge; skip the interview, draft, and ask a single confirmation.
5. **Draft shown, user edits or approves** — treat the draft as accepted; do not re-open interview questions.
6. **Two-vague-answers on a slot** — convert that slot to default; never rephrase the same question a third time.
7. **Domain floor met** — for high-stakes categories (`security-audit`, `migration`, `architecture-design`, `ml-pipeline`), require at least 2 answered questions before drafting, even when input is specific. These categories have expensive failure modes from under-specification.

---

## Universal stop-rules question

Every category's question bank now carries an implicit universal question — *"When should the model stop, ask a clarifying question, retry, or abstain?"* — that the interview loop asks (or defaults) regardless of category. Default if the user does not specify: "Stop when the deliverable matches the success criteria; ask if input is ambiguous; retry once on transient tool failure; abstain on unverifiable facts." This is a 2026 requirement (OpenAI GPT-5.5 official guide) and applies to every output target. Source: https://kingy.ai/ai/gpt-5-5-prompting-guide-write-for-outcomes-not-ritual/

## Domain floor for high-stakes categories

Four categories carry a domain floor: **`security-audit`, `migration`, `architecture-design`, `ml-pipeline`**. For these, require at least 2 answered questions before drafting, regardless of how specific the raw input is. Reasoning: the cost of a miscalibrated prompt in these domains is high enough that an extra minute of interview is cheap insurance. The trivial-input fast-path does NOT apply to domain-floor categories.

The floor applies only to **asked and answered** questions. Slots that are inferred from raw input still count toward "filled," but the floor requires the user to have actively answered 2 questions. This ensures the user has engaged with the high-stakes specifics before Claude commits to a plan.

---

## Two-vague-answers rule

Track vague answers per slot. Examples of vague: "I dunno," "whatever works," "your call," "doesn't matter," "idk," "something like that."

- First vague answer on a slot → try a narrower or differently-framed question, OR move to a different slot and come back via inference.
- Second vague answer on the same slot → convert to default immediately, surface in assumptions with `[default]`, never rephrase the question a third time.

This is strict. Users who give vague answers are signaling low engagement on that dimension; forcing them further is interrogation.

---

## Trivial-input fast-path

If the raw input already fills ≥80% of required slots AND a draft sampled from current state wouldn't meaningfully diverge from alternative drafts, skip the interview entirely.

Go straight to drafting. Present with a single confirmation: *"Your input covered the essentials. Here's the refined prompt — any changes, or ship it?"*

The user can still edit in the review round. The fast-path preserves all their agency at the end of the flow instead of the beginning.

Exclusions: domain-floor categories do not use the fast-path even if slots appear filled.

---

## Progress cue

If a second round is needed, announce it: *"One more round (≤3 questions) and we'll draft."* Sets expectation and reduces abandonment. The user now knows the commitment is bounded.

Do not announce a first round — just ask. Announcing "I'm going to ask you 3 questions" adds ceremony without value.

---

## State tracking

Maintain these across rounds, implicitly:

- **Answered-slot list** — every slot filled by user answer, inference, or default, tagged with source.
- **Vague-answer count per slot** — so the two-vague-answers rule fires at the right moment.
- **Asked-question list** — so duplicate questions across rounds are avoided.
- **Raw input** — preserved verbatim for any mid-session category switch or re-framing.

Never re-ask a slot that's been answered. Dedupe semantically, not just lexically — "what's the audience?" and "who's this for?" are the same question.

---

## Voice-origin input

By 2026 the dictation landscape has bifurcated. Wispr Flow defaults to cloud "AI cleanup" that rewrites the transcript (removes fillers, adds punctuation, restructures lists, applies a shared dictionary) before it reaches the prompt field. Superwhisper and MacWhisper offer user-selectable modes — some raw, some cleaned. Treat the input accordingly:

- **Detection signals:** run-on sentences with no punctuation, filler words ("um," "uh," "like," "you know"), dictated punctuation phrases ("open quote," "close quote," "new paragraph," "comma"), code identifiers spelled phonetically ("dot ts," "five hundred" for HTTP 500).
- **Pre-cleaned input:** preserve user-intent phrasing; do not re-rewrite cleaned-up dictation. Apply the existing phonetic-dictation rule from SKILL.md (technical form in `<error_output>`, dictated phrase verbatim in `<symptom>`).
- **Raw input:** the same rule applies but the interview may need to disambiguate filler-laden run-ons before classifying. Do not interrogate — extract the deliverable shape and proceed.

Source: https://spokenly.app/blog/wispr-flow-vs-superwhisper-vs-macwhisper

## UX patterns

**Batched numbered questions with per-question skip.** When asking 2–3 questions in one message, number them and tell the user they can skip any with "skip #2" or equivalent. Faster reply, respects user autonomy.

**Progress indicator when round 2 is triggered.** Announce the bounded commitment explicitly.

**Always-visible bail-out affordance.** The user knows at every turn they can say "good enough" and get a draft immediately.

**Assumption surface inline in draft.** Every non-user-provided slot appears labeled. The user can cross-reference against the category's `Default assumptions` section if they want to know what was defaulted.

**Speculative draft even when slots are vague.** Cursor Plan Mode's insight: showing a draft that the user can edit beats asking more questions. A draft is the fastest way to surface what's wrong.

**Confidence labels on inferred vs. defaulted slots.** `[inferred]` means "from your input"; `[default]` means "I picked for you." The distinction matters because users are more likely to correct defaults than inferences.

---

## Anti-patterns specific to the interview

Also see `references/meta/anti-patterns.md` for the complete list. The interview-specific ones:

- **Always-ask (GPT-Engineer pattern)** — gate on ambiguity; skip when input is self-contained.
- **Duplicate questions across rounds** — maintain answered-slot state; dedupe semantically.
- **Asking for trivially-inferable info** — "What language?" when code is pasted, "What audience?" when the user mentioned LPs.
- **Infinite loop on vague answers** — two-vague-answers rule is strict.
- **Over-asking on trivial prompts** — "write a haiku about cats" does not need 5 questions.
- **Leading/loaded questions** — offer open-ended first; multiple-choice needs an "other/none" option.
- **Batching >3 questions** — abandonment rises sharply past 3.
- **Treating every category identically** — the question bank is category-conditioned for a reason.

---

## When the interview is actually good

You'll know the interview worked when:

- The user answered 2–3 questions, you drafted, they approved or edited once, and the whole interaction took under 90 seconds.
- The assumptions list is 3–6 items long — enough to show you thought about the defaults, not so many that the prompt feels auto-generated.
- The user's review-round feedback is substantive ("change the audience to engineers, drop the regression test") rather than confused ("what did you mean by...?"). Confused feedback means you skipped a slot that should have been surfaced.

When you see signs of a good interview, internalize the pattern; when you see signs of a bad one (5 questions asked, user rushed to "just do it," draft needed major edits), check which rule was violated.
