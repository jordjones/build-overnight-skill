# Anti-Patterns: What the Skill Must Never Do

The skill re-reads this file before finalizing any refined prompt. Each anti-pattern has (a) a recognition signal, (b) why it fails, (c) the mitigation. Check every draft against this list before delivery.

These are distilled from the research on prior-art meta-prompting tools (Anthropic's own Prompt Improver, Cursor Plan Mode, GPT-Engineer, ClarifyGPT) and the observed failure modes across 36 categories.

---

## Refinement anti-patterns (during the interview)

**1. Re-asking what the user already answered.** If a user's raw input already contains the language, the framework, or the audience, do not ask again. Check the input and the conversation history before every question. *Mitigation:* maintain an implicit answered-slot list across rounds.

**2. Over-triggering the interview on trivial inputs.** A haiku request does not deserve 5 clarifying questions. A specific bug report with repro and stack trace does not deserve a full interview. *Mitigation:* apply the trivial-input fast-path when the raw input fills ≥80% of required slots.

**3. Asking the user to restate their input after classification.** The user typed their idea once. Do not make them type it again when offering a top-two or switching categories mid-session. *Mitigation:* preserve the raw input in state; reuse it silently.

**4. Leading or loaded clarifying questions.** Do not ask *"Do you want a microservice architecture?"* when a monolith may be right. Do not ask *"Should I add authentication?"* when the user didn't mention it. *Mitigation:* prefer open-ended first, multiple-choice with "other/none" second, leading never.

**5. Batching more than 3 questions per round.** Users abandon interviews at 5+ questions per message. Cap at 3 per round; most rounds should be 1–2. *Mitigation:* hard cap enforced by the interview-loop specification.

**6. Rephrasing a question the user answered vaguely.** "I dunno" is information. Rephrasing to extract a non-answer is interrogation. *Mitigation:* two-vague-answers rule — after the second vague response on any slot, convert to default.

**7. Ignoring bail-out phrases.** When the user says "good enough," "just do it," "ship it," or "your best guess," the interview is over. Do not ask one more question. Do not ask for confirmation of the bail-out. *Mitigation:* explicit bail-out phrase list checked on every user turn.

---

## Drafting anti-patterns

**8. Silent defaults.** If the skill chose `pytest` because the user didn't specify a test framework, the user must see that choice. Defaults hidden from the user are bugs waiting to bite. *Mitigation:* every non-user-provided slot appears in the assumptions surface with `[inferred]` or `[default]` label.

**9. Auto-injecting chain-of-thought or extended-thinking scaffolding.** Anthropic's own Prompt Improver over-adds CoT and it is the top user complaint about that tool. CoT belongs in refined prompts for reasoning-heavy categories (`analysis-reasoning`, `research-report`, `decision-support`, some coding categories) and nowhere else. *Mitigation:* category files specify when CoT applies; the skill does not add it by default.

**10. Sanitizing the user's phrasing into generic paraphrase.** "Flaky on Tuesdays" is a diagnostic clue. "Intermittent test failure" is not. Preserve specific phrasing in the symptom/context sections of the refined prompt. *Mitigation:* when filling user-provided slots, keep the user's words unless dictation introduced pure filler.

**10a. Converting phonetically-dictated values without preserving the original phrasing.** Superwhisper-style dictation often produces "five hundred" for 500, "dot ts" for .ts, "four hundred" for HTTP 400. The technical form is correct for structured/technical sections of the template (status codes, file extensions, version numbers). The dictated phrase is the user's literal utterance and carries context in user-quoted fields — symptom statements, verbatim-input blocks, anything framed as the user's report of the problem. *Mitigation:* use the technical form in `<environment>`, `<status_code>`, `<error_output>`-style fields; preserve the dictated phrase in `<symptom>`, `<repro_steps>`, user-narrative blocks.

**11. Adding persona instructions by default.** Not every refined prompt needs "You are a senior engineer." The role belongs when the category file specifies it. Do not inject roles out of habit. *Mitigation:* category files own role decisions; the skill does not auto-prepend.

**12. Drift into advocacy when the category is investigative.** `research-report` informs a decision; it does not argue one. If advocacy language shows up in a research-report draft ("clearly, the best approach is..."), it leaked from an adjacent category. *Mitigation:* category-specific quality rubric catches this before finalization.

**13. Fabricated citations.** For any research-adjacent category, a citation that cannot be verified at its URL is a blocker, not a nit. *Mitigation:* the research-report and analysis-reasoning templates state this explicitly and require the model using the refined prompt to verify sources or remove the claim.

**14. ALL-CAPS MUSTs in the refined prompt.** Skill-creator's explicit yellow flag. Loud emphasis does not improve compliance; it signals desperation. On Claude 4.5/4.6/4.7 and GPT-5.5 the same scaffolding now over-triggers (unnecessary tool calls) or gets auto-corrected by the model, so the rule tightens from "use sparingly" to "never." *Mitigation:* directive prose. "Do X" is enough. "YOU MUST ALWAYS DO X" is not more effective. Source: https://mrprompts.substack.com/p/how-to-prompt-in-2026

**15. Inventing a category outside the fixed 36.** The taxonomy is closed. If the request genuinely doesn't fit any category, pick the closest match and surface the mismatch in assumptions. *Mitigation:* dispatch table in SKILL.md is the canonical list; no runtime extension.

**16. Under-surfacing assumptions.** If the user can't see what was assumed, they can't correct it. An assumption list with 1 entry when 5 slots were defaulted is worse than no list. *Mitigation:* every non-user-provided slot gets an entry.

**17. Burying a load-bearing fact in the middle of a long-context prompt.** The U-shaped recall curve ("lost in the middle") persists on 1M-context models like Opus 4.7. *Mitigation:* pin highest-signal chunks at the start and immediately before the answer slot; repeat the user's question on its own line right before the assistant turn; chunk-and-summarize before stuffing 200K+ tokens. Source: https://dev.to/gabrielanhaia/lost-in-the-middle-is-still-real-in-2026-even-on-1m-token-models-2ehj

**18. Over-nested XML on short prompts.** Wrapping every sentence of a short prompt in 5+ nested XML tags is expensive on Opus 4.7's tokenizer and signals 2023-era ritualism without improving compliance. *Mitigation:* use XML for `<instructions>` / `<context>` / `<examples>` delimiters on multi-section prompts; pick output format (markdown / HTML / JSON-schema) by category, not blanket-XML. Source: https://simonwillison.net/tags/markdown/

---

## Quick recognition checklist (run this before delivery)

Before showing the draft to the user, scan for these markers:

- Is there a `{{PLACEHOLDER}}` token still in the draft? → revise, either ask or default.
- Did the assumptions list surface every non-user-provided slot? → if not, complete it.
- Does any claim in a research-adjacent draft name a specific source that you can't verify? → remove or replace with a placeholder the user fills.
- Is there ALL-CAPS emphasis anywhere in the refined prompt? → rewrite in plain directive voice.
- Did you add `<thinking>` tags to a category that doesn't warrant CoT? → strip them.
- Did you paraphrase a user's specific phrasing ("flaky on Tuesdays") into generic terms? → restore the original phrasing in the symptom or context section.
- Is the category you picked one of the fixed 36 names? → if you invented a name, pick the closest canonical match and surface the mismatch.
- Did the interview actually stop when the user said "ship it" or "just do it"? → if not, your draft is built on questions the user didn't want to answer.

If any of these flag positive, revise silently before presenting. The user should see a clean draft, not a correction log.

---

## Retired for 2026 reasoning-native models (Opus 4.7 / GPT-5.5 / Gemini 3)

These were valid 2023–2024 patches for under-responsive models. On reasoning-native 2026 models they actively hurt output — they signal ritualism without improving compliance, over-trigger tool calls, get auto-corrected by the model, or prescribe a reasoning path the model already executes internally. The existing 18 anti-patterns above still apply; these are *additional* retirements specific to 2026 model behavior.

**R1. World-class-expert persona priming.** "You are a world-class senior X with 20 years of experience" wastes tokens and biases tone without measurably improving correctness on Opus 4.7 / GPT-5.5. *Mitigation:* drop the persona unless the category specifically warrants one (`roleplay-persona`); state the deliverable shape and audience instead. Source: https://mrprompts.substack.com/p/how-to-prompt-in-2026

**R2. "Think step by step" / "reason carefully" triggers.** Reasoning-native models execute multi-step reasoning internally; adding CoT triggers prescribes a path the model already runs. *Mitigation:* raise the effort/thinking budget instead of prompting for CoT. Source: https://karozieminski.substack.com/p/ai-prompting-techniques-reasoning-models-2026

**R3. "Never hallucinate" / "be accurate" hedges.** These are unenforceable and the model treats them as filler. *Mitigation:* replace with verifiable confidence/gap markers in the output (e.g., require "[not in source]" tags when the evidence base is exhausted) so the model either cites or surfaces the gap. Source: https://mrprompts.substack.com/p/how-to-prompt-in-2026

**R4. Self-verification rituals ("are you sure?", "double-check your answer").** A single self-refine turn drifts without an external scorer. *Mitigation:* the critique-and-revise loop is scored against the 5-dimension rubric in `references/meta/quality-rubric.md` — separate grader, not in-turn self-doubt. Source: https://generativeai.pub/the-self-grading-pattern-how-agents-verify-their-own-work-before-shipping-2714c6417c71

**R5. Few-shot examples for reasoning-class tasks.** Worked examples constrain reasoning models toward the example's path rather than letting them find a better one. *Mitigation:* state the problem and the success criteria; omit few-shot examples for reasoning-heavy categories. Few-shot still helps non-reasoning categories (extraction, classification, translation). Source: https://karozieminski.substack.com/p/ai-prompting-techniques-reasoning-models-2026

**R6. Overprompting with extra constraints "just in case."** Reasoning-native models are MORE sensitive to constraints than older models, not less; piling on belt-and-suspenders rules degrades output. *Mitigation:* state the minimum sufficient constraint set; trust the model on the rest. Source: https://www.mindstudio.ai/blog/how-to-prompt-gpt-5-5-outcome-first-prompting

**R7. Rigid multi-section templates padded to fill every slot.** If a slot doesn't apply, omit it; do not pad with "N/A" or placeholder text. *Mitigation:* templates are skeletons, not checklists; the assumptions surface already disclaims what was defaulted. Source: https://mrprompts.substack.com/p/how-to-prompt-in-2026

**R8. Auto-injected CoT scaffolding (legacy prompt-improver behavior).** Anthropic's own prompt-improver, OpenAI's Optimize button, and ChatGPT-based meta-prompters over-add personas, CoT triggers, and examples by default. *Mitigation:* the build-prompt category files own CoT decisions; do not layer extended-thinking tags on every draft out of habit. Source: https://www.reddit.com/r/ClaudeCode/comments/1tng1fx/am_i_over_complicating_my_prompts/
