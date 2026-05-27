# Output Targets: Per-Target Formatting Rules

The refined prompt's format depends on where it will be pasted. A prompt optimized for Claude.ai's XML-fluent interpreter reads poorly in Cursor's rules file; a prompt optimized for an eval harness with rigid output schemas reads as over-constrained in a ChatGPT conversation. When the user specifies a target, adjust accordingly. When they don't, use the unspecified default.

**Detection.** If the user's raw input names the target directly ("for my Cursor rules," "paste into ChatGPT," "going into our eval harness"), treat it as specified — do not ask. If ambiguous, ask once at the start of the interview: *"Where will you paste this? Claude.ai, Claude API, ChatGPT, Cursor rules, eval harness, or somewhere else?"* If the user declines to specify, use the unspecified default.

**Surface in assumptions.** Always surface the output target in the assumptions list: *"Output target: Claude.ai [inferred]"* or *"Output target: unspecified [default — Anthropic-flavored]"*.

---

## Target-by-target formatting

### Claude.ai chat

- **XML tag density:** heavy. Claude 3/4 were fine-tuned on XML; tags actively help the model parse multi-section prompts.
- **Placement:** long inputs (documents, code, data) go BEFORE instructions; task/query goes at the bottom. Anthropic reports up to 30% quality lift from this ordering on long-context prompts. The U-shaped recall curve from Liu et al. 2023 ("lost in the middle") still holds on Opus 4.7's 1M context and on every long-context model tested in RULER as of 2026. Three sub-rules: (a) pin the highest-signal chunk first and the second-highest immediately before the answer slot; (b) repeat the user's question on its own line right before the assistant turn; (c) chunk-and-summarize before stuffing 200K+ tokens — do not rely on the model to find a load-bearing fact in the middle of an unstructured dump. Source: https://dev.to/gabrielanhaia/lost-in-the-middle-is-still-real-in-2026-even-on-1m-token-models-2ehj
- **Voice:** conversational prose is fine around the XML-structured content; mix is expected.
- **Role:** explicit `<role>` block when the category benefits from it (bug-fix, research-report, creative-writing). Not mandatory.
- **CoT:** `<thinking>` and `<answer>` tags when the category file specifies CoT; not by default.
- **Length:** no hard ceiling. Claude.ai handles long prompts well. Aim for "as long as needed, no longer."
- **Adjustments from unspecified default:** none. Claude.ai is the default for the default.

### Claude API (programmatic)

- **XML tag density:** heavy. Same as Claude.ai.
- **System vs. user split:** explicit. Persona, global rules, output schema → system. Variable payload (document, question, input text) → user. Most refined prompts split naturally into "the template" (system) and "the placeholder contents" (user).
- **Template variables:** surface `{{PLACEHOLDER}}` tokens explicitly so the user can wire them into their code. Suggest variable names in the surface/assumptions list.
- **Output format:** if the user is parsing the response programmatically, prefer structured outputs (`output_config.format` with JSON schema) over prose. Note this in the refined prompt if the category is extraction or classification.
- **Prefill:** on pre-4.6 models only. On Opus 4.6+, prefill is deprecated; use structured outputs instead. Default assumption: 4.6+ unless user specifies older.
- **Length:** no hard ceiling; watch `max_tokens` headroom for reasoning-heavy categories, especially on Opus 4.7 (new tokenizer, ~35% more tokens per identical text).

### ChatGPT (GPT-4, GPT-5 family)

- **XML tag density:** light. GPT models parse XML but respond better to markdown sections and numbered instructions.
- **Section headers:** use `## Context`, `## Task`, `## Constraints`, `## Output format` as markdown headers instead of XML tags.
- **Role prefix:** "You are..." at the top is the convention. GPT models expect it.
- **Reasoning:** for reasoning models (o1 family), omit explicit CoT scaffolding — the model reasons internally. For standard models, "Think step by step before answering" works.
- **Length:** shorter than Claude-targeted prompts. GPT attention drops off on long prompts more quickly than Claude's.
- **Structured outputs:** GPT supports JSON schema strict mode; flag in the refined prompt if output parsing is needed.

### Cursor system prompt / rules

- **XML tag density:** minimal. Cursor rules files (`.cursorrules` or `.cursor/rules/*.mdc`) are terse imperative directives. XML tags feel heavy.
- **Voice:** imperative, short bullets. "Use Tailwind for styling." "Prefer functional components." "Never commit to main."
- **Project-scope framing:** the rule applies to the repo, not to a single session. Avoid referencing "this task" or "the current request."
- **Length:** short. 20–60 lines typical. If the refined prompt runs longer, the user is over-specifying — suggest trimming.
- **No role block:** Cursor already sets the agent's role; adding "You are a senior engineer" is redundant and wastes tokens in every turn.
- **No output format block:** Cursor manages output; the rules influence behavior, not response shape.

### Claude Code or OpenAI Codex CLI (AGENTS.md / CLAUDE.md)

- **XML tag density:** minimal, same as Cursor.
- **Structure:** follow the AGENTS.md/CLAUDE.md conventions — `## Commands`, `## Architecture`, `## Conventions`, `## Key files`, `## Gotchas`, `## Don't touch`.
- **Length:** under 60 lines. Research shows instruction-following degrades above this threshold.
- **No personality instructions.** "Be a senior engineer" wastes tokens per session.
- **No linter-enforceable rules.** If a formatter or linter catches it, let the tool catch it; don't duplicate in prose.

### Eval harness (Inspect, Promptfoo, Braintrust, LangSmith, DeepEval, custom)

**Vendor alignment (May 2026):** flag which harness is aligned with which vendor when recommending. Promptfoo → acquired by OpenAI (announced 2026-03-09, still closing). LangSmith → LangChain. Braintrust → vendor-neutral ($80M Series B Feb 2026). Inspect AI → UK AISI, governance/safety-grade. DeepEval → neutral. A user planning multi-vendor evals should prefer the neutral harnesses; vendor-aligned ones are fine for single-vendor pipelines. Source: https://www.augmentcode.com/tools/best-ai-agent-evaluation-tools


- **XML tag density:** heavy but minimal ornamentation. Tags exist for parsing, not for flavor.
- **Deterministic format:** no chatty preamble, no hedging, no "Let me think about this." Direct to the output format.
- **Explicit output schema:** the prompt must constrain the response shape so the harness can score it. JSON, a regex, or an enum; not prose.
- **No conversational wrapper.** "I'll help with that" is garbage in an eval response. The prompt should forbid it.
- **Variable extraction:** `{{INPUT}}`, `{{EXPECTED_OUTPUT}}`, etc., so the harness can substitute per-row.
- **Reasoning:** if the eval measures reasoning, include explicit CoT tags; if it measures final-answer correctness, suppress CoT so the response is just the answer.

### GPT-5.5 (outcome-first)

GPT-5.5 (released 2026-04-23) is a new model family that must not be treated as a drop-in for GPT-5.2/5.4. OpenAI's own guidance: start migration from a fresh baseline, do not carry over older prompt stacks.

- **XML tag density:** minimal. GPT-5.5 rewards markdown bullets and outcome-spec structure over XML.
- **Voice:** outcome-first. Name the artifact you want, not the process.
- **Required four fields:** `output_artifact` (what should exist when done), `audience_context` (who it is for, where used), `quality_criteria` (what makes it good or bad), `hard_constraints` (what is off-limits). No process steps.
- **System slots (optional):** `personality`, `collaboration_style`.
- **Stop rules:** explicitly required (see SKILL.md Step 5 — outcome-first prompts mandate a stop/abstain clause).
- **Acknowledgement-before-tool-call micro-pattern:** for agentic flows, instruct the model to acknowledge the tool call intent before invoking.
- **Length:** shorter than Claude-targeted prompts. GPT-5.5 punishes overprompting.
- **CoT scaffolding:** do not add. GPT-5.5 reasons internally; "step by step" triggers are noise.
- Source: https://developers.openai.com/api/docs/guides/prompt-guidance?model=gpt-5.5 and https://www.mindstudio.ai/blog/how-to-prompt-gpt-5-5-outcome-first-prompting/

### AGENTS.md (cross-tool universal)

Open format stewarded by the Linux Foundation; 60,000+ public repos as of 2026; read natively by Codex CLI (primary), Cursor, Continue.dev, Aider, OpenHands, and Claude Code (fallback when CLAUDE.md is absent).

- **XML tag density:** none.
- **Voice:** terse, developer-written, imperative.
- **What goes in:** information NOT discoverable from the repo (package manager preference, deploy invariants, project-specific gotchas).
- **What does NOT go in:** auto-generated codebase overviews, directory maps, linter-enforceable rules, persona instructions. LLM-generated AGENTS.md / CLAUDE.md context files reduce coding-agent task success by ~3% and raise inference cost ~20% on SWE-Bench Lite per Upsun research.
- **Length:** under 60 lines. Stricter than CLAUDE.md.
- **Local overrides:** use a gitignored `AGENTS.override.md` rather than editing the canonical file per-machine.
- Source: https://www.deployhq.com/blog/ai-coding-config-files-guide and https://developer.upsun.com/posts/ai/agents-md-less-is-more

### Gemini 3 (Pro / Flash / Flash 3.5)

Gemini 3 family replaces the integer `thinking_budget` parameter with a string enum `thinking_level` having values `{minimal, low, medium (default), high}`.

- **XML tag density:** light to moderate. Markdown sections preferred for body.
- **Thinking control:** `thinking_level` enum (not a token count). If you previously used chain-of-thought prompting, drop the prompt-side CoT and raise `thinking_level` instead — Gemini 3's internal reasoning supersedes prompted CoT.
- **Section markers:** markdown H2 / H3 headers.
- **Output format:** structured outputs via response schema are first-class.
- **Length:** moderate. Gemini 3 Flash punishes very long prompts more than Pro does.
- Source: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-flash

### Open-weights (Llama 4 / Qwen 3.x / DeepSeek V4)

Three distinct conventions; do NOT treat them as one target.

- **Llama 4:** uses a structured system-prompt template (Meta-published). Persona/role in `<<SYS>>`. No interleaved thinking.
- **Qwen 3.x:** runtime flag `enable_thinking` (chat-template kwarg) plus an in-prompt directive `Reasoning effort is set to xhigh` for the reasoning variants — hybrid prompt-plus-config control.
- **DeepSeek V4 / R2:** default-on visible chain-of-thought (CoT in the response, not hidden). Do not suppress; tag it for downstream parsing.
- **Anti-pattern:** do not reuse a Claude-shaped prompt verbatim on these models without per-family adjustment.
- Source: https://qwen.ai/blog?id=qwen3.7

### Unspecified (Anthropic-flavored default)

When the user hasn't named a target, use these defaults:

- XML tags for multi-section prompts.
- Long inputs before instructions.
- `<role>` block when the category file specifies one, not otherwise.
- CoT (`<thinking>` / `<answer>`) when the category is reasoning-heavy (research-report, analysis-reasoning, decision-support, debugging-session, some others); not otherwise.
- Inline numbered citations for research-adjacent categories.
- `<output_format>` block at the end — always.
- Placeholder style: `{{UPPER_SNAKE_CASE}}`.

This default is optimized for pasting into Claude.ai or Claude API without modification.

---

## Quick lookup table

| Target | XML density | Role block | Section markers | Length ceiling | Special |
|---|---|---|---|---|---|
| Claude.ai chat | Heavy | Yes (when warranted) | XML tags | Flexible | Long content before instructions |
| Claude API | Heavy | In system prompt | XML tags | Flexible | Explicit system/user split; structured outputs ready |
| ChatGPT | Light | "You are..." | Markdown headers | Shorter | Numbered instructions; o1 suppresses CoT |
| GPT-5.5 (outcome-first) | Minimal | Optional system slots | Markdown bullets | Shorter | 4 fields: output/audience/quality/constraints; stop_rules required |
| Cursor rules | Minimal | Never | Short bullets | 20–60 lines | Project-scope, imperative |
| AGENTS.md (cross-tool) | None | Never | Conventional H2s | <60 lines | Linux Foundation format; no auto-generated overviews |
| CLAUDE.md (Claude Code) | Minimal | Never | Conventional H2s | <60 lines | No linter-enforceable rules, no persona |
| Gemini 3 | Light–moderate | Optional | Markdown headers | Moderate | `thinking_level` enum, not budget tokens |
| Open-weights (Llama 4 / Qwen 3.x / DeepSeek V4) | Varies | Per-family | Per-family | Per-family | Three distinct conventions; do not unify |
| Eval harness | Heavy but lean | Depends on test | XML tags | Tight | Deterministic output; no preamble |
| Unspecified | Heavy | When warranted | XML tags | Flexible | Anthropic-flavored default |

---

## Common adjustments when target changes mid-session

If the user switches targets after the draft is shown (*"actually I'm putting this in Cursor, not Claude.ai"*), do not re-interview. Adjust the draft in place:

- **Claude → Cursor:** strip XML tags, convert to short imperative bullets, drop role block, cap at ~40 lines.
- **Claude → ChatGPT:** convert XML tags to markdown headers, add "You are..." role prefix, trim length by 20–30%.
- **Claude → eval harness:** enforce deterministic output format, suppress conversational wrapping, add explicit JSON/regex schema block.
- **Unspecified → any:** apply the target-specific rules above as a delta.

Surface the adjustment in the assumptions list: *"Output target switched to Cursor rules; XML tags removed, length trimmed to 38 lines."*

---

## What not to do

- Do not ask the target twice. Ask once at the start if ambiguous, then trust the answer.
- Do not silently assume Claude.ai when the user typed "ChatGPT." The target is part of the prompt's design.
- Do not let target-specific defaults override category-specific structural requirements. A `research-report` prompt still needs sub-questions and confidence labels even if the target is Cursor. If the two conflict, suggest the user pick a different category or target.
- Do not apply eval-harness terseness to a creative-writing prompt targeted at Claude.ai. The target adjusts formatting, not voice.
