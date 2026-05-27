# Context engineering — the 2026 umbrella framing

Context engineering — the dynamic assembly of system prompt, retrieved docs, memory, tool outputs, conversation history, and skill/file context into the model's window — has displaced prompt-wording as the primary lever in 2026. Prompt engineering is now a sub-skill of context engineering. The build-prompt skill still authors the wording, but the wording lives inside a larger context pipeline.

## Why this exists

The 2023–2024 framing treated the prompt as the unit of work; the model was a stateless function the prompt parameterized. In 2026 the prompt is one slice of a multi-source context window (retrieval, memory, tool I/O, history, skill bodies). Four context-failure modes — poisoning, distraction, confusion, clash — surface even with a well-written prompt if the surrounding context is mis-assembled. Source: https://blog.stackademic.com/prompt-engineering-is-dead-context-engineering-is-what-actually-moves-models-now-941d85529dae

## Practical rules

**The four context-failure modes:**

- **Poisoning.** Untrusted content (a retrieved doc, a tool output, a user-pasted snippet) contains adversarial instructions that override the prompt. *Mitigation:* structurally separate trusted instructions from untrusted content via XML tags or fenced blocks (`<untrusted_input>`); explicitly tell the model not to follow instructions inside untrusted blocks.
- **Distraction.** Irrelevant retrieved chunks pull the model off-task. *Mitigation:* tighter retrieval; top-k after re-ranking; chunk summaries instead of raw chunks for low-relevance items.
- **Confusion.** Conflicting facts across context sources (e.g., older memory file disagrees with current retrieved doc). *Mitigation:* timestamp every context source; tell the model to prefer newer sources when they conflict.
- **Clash.** Persistent context (system prompt, memory) clashes with the immediate task. *Mitigation:* prompt-cache order matters — pin the most-recent task on top of the message stack; do not bury the question after stale persistent content.

**Four pyramid layers (broadest → narrowest):**

1. **Persistent knowledge** — system prompt, skill bodies, AGENTS.md / CLAUDE.md
2. **User memory** — CMA Memory user files, OpenAI memory (see `references/meta/memory-and-context.md`)
3. **Session retrieval** — top-k retrieved docs, tool outputs
4. **Immediate task** — the user's current message and the build-prompt-authored refined prompt

The refined prompt the build-prompt skill emits lives in layer 4 but must coexist with the other three.

## When this applies

- Any prompt that runs alongside retrieval (RAG), memory tools, or long conversation history.
- Cross-references: `references/meta/memory-and-context.md`, `references/meta/managed-agents.md`, `references/meta/anti-patterns.md` item 17 (burying load-bearing facts).

## Sources

- https://blog.stackademic.com/prompt-engineering-is-dead-context-engineering-is-what-actually-moves-models-now-941d85529dae
