# build-overnight

Interactive skill for Claude Code that builds prompts specifically engineered to run as **overnight goal-mode loops** (default 8 hours).

Sibling skill to [build-prompt](https://github.com/jordjones/build-prompt-skill). Where `build-prompt` produces one-shot polished prompts, `build-overnight` produces prompts engineered to drive an autonomous loop over a fixed time budget — with stop rules, checkpoint cadence, artifact handoffs, and progress accounting tuned for unattended execution.

## Status

Scaffolding only. File structure and library to be ported/adapted from `build-prompt` once the overnight-loop research is complete.

## Planned structure (TBD)

- `SKILL.md` — activation protocol and interview loop
- `library/` — overnight-mode prompt templates by category
- `references/` — research notes on loop architectures, time-budgeting, checkpointing
- `scripts/` — test harness
- `CHANGELOG.md`
