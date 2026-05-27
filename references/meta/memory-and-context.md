# Memory and context persistence

Cross-cutting reference for prompts that interact with persistent memory — Anthropic Claude Managed Agents Memory (CMA Memory, public beta 2026-04-23), OpenAI memory, or third-party memory layers.

## Why this exists

Memory exposes a separately-permissioned, auditable artifact layer in addition to the in-session context. CMA Memory in particular is a file system the agent reads and writes through normal file tools — not a bespoke memory tool — with read-only org files plus read-write user files, and every write logged to the Claude Console as a session event. Prompts that assume "this just lives in context" silently fail when the artifact actually lives in memory and is mutated across sessions. Source: https://www.techzine.eu/news/devops/140836/anthropic-adds-memory-to-claude-managed-agents/

## Practical rules

- **Memory is files, not magic.** CMA Memory is read/listed/written/deleted with the same file tools the agent uses for repo files. The prompt should reference memory paths the same way it references file paths.
- **Two-tier permission layer.**
  - Org files: read-only. Treat as authoritative context; never instruct the model to attempt a write.
  - User files: read-write. Every write is logged as a Claude Console session event, exportable via API. If the prompt writes, name what gets written and why.
- **Cache eligibility under memory reads.** Whether memory file reads count against prompt-cache eligibility is implementation-defined; do not assume cache hits on memory-augmented prompts. Test with the Anthropic SDK's cache-read metrics before claiming a cache strategy.
- **Auditable writes are a feature, not a bug.** When the prompt is designed to update memory (e.g., updating a user-preference file), include the rationale inline so the audit log is useful: "Update `prefs.md` because user said they switched to vim."
- **No bare "remember this" prompts.** "Remember that I prefer vim" is meaningless without a target path. Either the prompt names a memory file or it does not interact with memory.

## When this applies

- Prompts running inside Claude Code with the memory tool enabled.
- Prompts targeting CMA Memory in the Anthropic API.
- Any prompt instructing the model to "remember" or "save" preferences across sessions.
- Cross-references: `references/meta/managed-agents.md` (permission policy), `references/meta/output-targets.md` (Claude API row).

## Sources

- https://www.techzine.eu/news/devops/140836/anthropic-adds-memory-to-claude-managed-agents/
