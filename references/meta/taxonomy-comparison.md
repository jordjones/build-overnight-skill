# Taxonomy comparison — build-prompt vs competing prompt-builder libraries

Reference for understanding where the build-prompt 36-category functional taxonomy fits in the 2026 landscape and where it deliberately differs.

## Why this exists

When users compare build-prompt against PromptHero, SurePrompts, PromptHub, etc., they expect to find prompts organized by-model or by-use-case. build-prompt is organized by-function — a third axis. Knowing the trade-off helps users and contributors avoid forcing build-prompt to mimic the competitor axis. Source: https://promptbuilder.cc/blog/best-prompt-builder-tools-2026

## Three competing taxonomies

| Axis | Examples | Strength | Weakness |
|---|---|---|---|
| **By-model** | PromptHero, SurePrompts, PromptHub organize by Claude / Gemini / Grok / ChatGPT / Llama / Mistral / DeepSeek | Easy to filter for your model | Same task shows up 7 times with model-specific variants |
| **By-function** | build-prompt's 36 categories (bug-fix, research-report, etc.) | One template per deliverable shape | Model-specific variants buried in `model_target` field |
| **By-use-case** | "SEO," "writing," "image generation," "image-to-text" | Marketing-friendly buckets | Conflates very different deliverable shapes (a SEO blog brief vs SEO meta-description) |

## How build-prompt uses both axes

build-prompt's library frontmatter carries both `category` (by-function, one of 36) and `model_target` (by-model). The skill's classification step picks `category`; the model recommendation step at the end of each category file picks `model_target`. So a user can filter the library along either axis post-hoc:

- "Show me all `bug-fix` prompts" → by-function filter
- "Show me all prompts targeting Opus 4.7" → by-model filter
- "Show me `bug-fix` prompts for Opus 4.7" → both

## When users ask about other tools

- **"Why don't you organize by model?"** → because by-model duplicates the same template per model. The `model_target` frontmatter field gives the same filtering ability without duplication.
- **"Why don't you have a SEO category?"** → "SEO" is a use-case, not a deliverable shape. SEO needs split across `business-writing` (briefs), `creative-writing` (copy), `data-extraction` (keyword pulls). The taxonomy splits by deliverable, not by industry.
- **"Should I use PromptHero instead?"** → PromptHero is better for browsing existing community prompts by-model. build-prompt is better for authoring a new prompt with a disciplined interview loop.

## When this applies

- Documentation context (README.md, contributor docs).
- Cross-references: `SKILL.md` library-save section (mentions both axes), `references/INDEX.md` (the by-function index).

## Sources

- https://promptbuilder.cc/blog/best-prompt-builder-tools-2026
