# Managed Agents (Anthropic) — skills, tools, MCP

Cross-cutting reference for any prompt targeting Anthropic Managed Agents (announced at Code with Claude 2026). Skills, agent toolset, and MCP servers compose through a permission-policy layer; the prompt author has to understand which layer enforces what.

## Why this exists

Prior to Managed Agents, a prompt that needed tools had to embed tool definitions inline. Managed Agents shifts the loading model: skills load progressively (the agent pulls the SKILL.md body only when the description matches the task), and tool/MCP permissions are enforced server-side rather than via prompt prose. A `build-prompt` template targeting Managed Agents must (a) write skill descriptions as routers, not summaries; (b) name the permission policy explicitly; (c) keep MCP tool descriptions hygienic enough to be auto-matched. Source: https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/managed-agents-tools.md

## Practical rules

- **SKILL.md description-as-router.** The first line of every skill's description is what the agent matches against the task. Write it as a routing predicate ("Use when the user asks to translate, localize, or convert text between languages"), not a marketing blurb ("Powerful translation skill").
- **Permission policy is a first-class field.** Every tool the prompt invokes carries a permission policy: `auto` (no approval), `approval_required` (gate per call). Prompts that assume `auto` on a tool with `approval_required` will stall. Surface the policy in the assumptions list.
- **MCP tool description hygiene.** MCP tool descriptions are part of the system prompt the agent sees. Keep them under 200 characters each; lead with the verb; do not duplicate parameter docs into the description.
- **Cache order still applies.** Prompt-cache order is `tools → system → messages`; even in Managed Agents, dynamic content (per-call user IDs, retrieved chunks) must live below static tool/system content for cache hits. Cross-ref `references/meta/output-targets.md` Claude API row.
- **Stop rules for agentic flows.** Every Managed-Agents prompt MUST include a `<stop_rules>` clause covering tool-failure retry policy and abstain conditions (cross-ref SKILL.md Step 5).

## When this applies

- Any prompt that ends up in a Claude Code skill, a Claude API agent loop, or a Managed Agents deployment.
- Cross-references: `references/meta/output-targets.md` (Claude API row), `references/meta/memory-and-context.md` (CMA Memory), `references/style-guide.md` (description hygiene), `references/meta/reasoning-model-prompting.md` (effort levels for agentic loops).

## Sources

- https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/managed-agents-tools.md
