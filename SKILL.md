---
name: build-overnight
description: User-invoked slash command ONLY. Runs the interactive `/build-overnight` interview loop — classifies a rough goal into one of 6 overnight categories, asks targeted clarifying questions including the runtime target, drafts an autonomous-loop-ready prompt with mandatory cost/time/safety/drift clauses, and saves it to a versioned library. Invoke ONLY when the user explicitly types `/build-overnight` in their message. Never auto-invoke based on inferred intent like "run this overnight", "make this autonomous", or "let it loop" — those should route to build-prompt or to a runtime-specific skill (ralph/ralphthon/continuous-claude). This skill runs a multi-step interview that must not start without explicit user opt-in.
argument-hint: [optional: rough overnight goal in quotes]
allowed-tools: Read Write EnterPlanMode Bash(pbcopy) Bash(xclip *) Bash(wl-copy *) Bash(cat *) Bash(mkdir *) Bash(date *) Bash(${CLAUDE_SKILL_DIR}/scripts/*) Bash(${CLAUDE_SKILL_DIR}/bin/*)
---

# /build-overnight

This skill turns rough, dictated, or underspecified overnight-loop ideas into prompts that are engineered to drive **autonomous unattended LLM agent loops** over a fixed wall-clock budget (default 8h) with hard cost ceilings (default $40), runtime-appropriate stop rules, structured progress proof, drift detection, and a morning-review artifact handoff.

You — the Claude instance reading this — are the refiner. The user invoked `/build-overnight` and is now waiting for you. Do not ask them what this skill does; proceed with the activation protocol.

This skill is a sibling to [`/build-prompt`](https://github.com/jordjones/build-prompt-skill) and reuses its interview loop, quality rubric, anti-pattern catalog, and 15 shared meta-files. The overnight-specific machinery is concentrated in `references/scaffold/universal.md` (the 14 mandatory clauses), `references/meta/overnight-loop-mechanics.md`, `references/meta/runtime-adaptation.md`, and the 6 category files.

---

## Activation protocol

Follow these steps in order. Do not skip steps. Do not ask the user to confirm the steps themselves — they know they invoked the skill.

**Step 1 — Capture the raw input.** If `$ARGUMENTS` is non-empty, treat it as the raw goal and proceed to step 2. If `$ARGUMENTS` is empty, ask exactly once: *"What's the rough overnight goal? Dictate or type as much or as little as you want — I'll work with whatever you give me."* Accept multi-line, noisy, filler-heavy, dictated input without correction.

**Step 1.5 — Safety preflight.** Before classification, scan the raw input for hard-refuse patterns from `references/meta/safety-policy.md`: prod-credential mention, force-push intent, auto-merge intent, main-branch checkout intent, destructive shell intent, disable-tests intent, external-msg send intent. If any pattern matches, refuse to draft and explain the block. Do not attempt to defang — point to the closest acceptable formulation and stop.

**Step 2 — Classify.** Pick the single best-fit category from the dispatch table below. Base the decision on the *goal type* the user wants (what kind of work the loop will do), not just keywords. If your confidence is high, state the pick in one sentence and move on: *"This looks like `<category>` — <one-line rationale>. Proceeding."* If your confidence is mixed, present the top two candidates with one-line rationales and ask which fits; never list more than two. Always allow the user to override with "neither, it's actually X." If the user's intent maps to a cut category (`dep-upgrade`, `cleanup-deslop`, `data-pipeline-build`, `eval-harness-build`), say so and point to `library/future-work.md`.

**Step 3 — Load the template.** Read the single matching category file at `references/categories/<category-name>.md` using the Read tool. Do not load other category files. Also read `references/scaffold/universal.md` (always) and `references/meta/runtime-adaptation.md` (for the runtime variant table you'll need in Step 5).

**Step 4 — Run the interview.** Apply the question bank from the category file, following the rules in `references/meta/interview-loop.md`. Hard caps: ≤2 rounds, ≤5 questions total, ≤3 questions per round. When the user bails out ("good enough," "just do it," "ship it," "proceed," "skip," "your best guess"), stop asking immediately and proceed to step 5 with defaults filled in. When the trivial-input fast-path applies (the user's raw input already fills ≥80% of the required slots), skip the interview entirely.

**One question is always required regardless of bail-out:** *"Which runtime should this target? (1) ralph — default, zero marginal cost, local Claude Code self-loop. (2) managed-agents — Anthropic hosted, $0.08/session-hour. (3) continuous-claude — time-bounded with `--max-duration`. (4) other (ralphthon / ralph-loop / claude-p-chain — adapts from ralph)."* Suggest a default by matching the category's `capability_profile` against `runtime-adaptation.md`'s table.

**Step 5 — Draft the refined prompt.** Fill the template from the category file. The drafted prompt MUST include:

1. A top-level `<overnight_contract>` block emitting all 14 universal clauses C1–C14 from `references/scaffold/universal.md`, with default values bound to user-confirmed choices (8h budget, $40 cost ceiling, etc.). Override defaults only with values the user supplied in Step 4.
2. The 4 runtime-varying clauses (`<execution>`, `<persistence>`, `<completion>`, `<parallelism>`) rendered for the selected runtime per `runtime-adaptation.md`'s 3×4 table.
3. Category-specific mitigation clauses from the category file (e.g., `<oscillation_detector>` for bug-hunt, `<behavior_preservation_invariant>` for refactor-sweep).
4. The standard build-prompt `<stop_rules>` clause as a sub-section of `<output_format>`. Default text for overnight: *"Stop when goal-met per PRD acceptance criteria OR soft time/cost cap reached (ship-mode) OR drift limit hit OR ambiguity requires human; always commit, tag, push branch, open draft PR with [OVERNIGHT] prefix, write FINAL_REPORT.md or FAILURE.md before exit; never auto-merge, never force-push, never overrun hard cap."*
5. An `OVERNIGHT_RUN_REPORT.md` skeleton instruction referencing `references/meta/morning-review-artifact.md`.

Immediately beneath the draft, surface an "Assumptions" section listing every slot filled by inference or default, labeled `[inferred]` or `[default]`. Always list: `Budget: 8h [default]`, `Cost ceiling: $40 [default]`, `Runtime: <chosen> [user]`, `Sandbox: Tier-1 worktree [default]`, `Resume model: git-tag [default]`. Override any of these only if user-supplied.

**Step 6 — Review loop.** Ask: *"Looks good? Edits, or ship it?"* Accept free-form edits, approval, or a bail-out. Apply edits by updating the draft and re-surfacing assumptions if any defaults changed. The review is scored against `references/meta/quality-rubric.md` (5 dimensions) PLUS the 4 overnight-specific dimensions described in `references/research-distilled.md`: Overnight Discipline (time/checkpoint/termination coherence), Drift Resistance, Safety Posture, Verifiable Completion. One review round is the default; if the user requests more, honor.

**Step 7 — Deliver and save.** Ask: *"Delivery mode? (1) inline — paste here, (2) write to `./PROMPT.md`, (3) copy to clipboard, (4) dispatch — invoke the wrapper `bin/build-overnight-run` and launch the chosen runtime. Default: inline."* Regardless of delivery mode, save the finalized prompt to `~/.claude/skills/build-overnight/library/YYYY-MM-DD-<slug>.md` with YAML frontmatter:

```yaml
---
category: <category-name>
runtime: <ralph|managed-agents|continuous-claude|ralphthon|ralph-loop|claude-p-chain>
budget_hours: 8
cost_ceiling_usd: 40
capability_profile_match: <true|partial|false>
model_target: <claude-opus-4-7|claude-sonnet-4-6|...>
variables: [PRD_PATH, REPO_ROOT, ...]
created_at: <ISO 8601 with TZ>
source_input: "<≤200 chars of user input>"
---
```

…**before** any dispatch begins. Echo the library path. If the user chose dispatch mode (4), additionally instruct them how to:
1. Create a worktree: `git worktree add ~/overnight-worktrees/<run-id> -b overnight/<run-id>-<slug>`.
2. Launch the wrapper: `cd ~/overnight-worktrees/<run-id> && bin/build-overnight-run <run-id> <runtime>`.
3. Dispatch the saved prompt to the chosen runtime.

---

## Dispatch table

Pick one category. 6 categories ship in v1; 4 more (`dep-upgrade`, `cleanup-deslop`, `data-pipeline-build`, `eval-harness-build`) are documented in `library/future-work.md` and refused at draft-time with a pointer.

| Category | When to use | Reference file |
|---|---|---|
| test-coverage-overnight | Raise meaningful coverage on a target module (mutation/branch-gated; refuses on naive line-coverage targets) | references/categories/test-coverage-overnight.md |
| bug-hunt-overnight | Drive a failing test or repro to green with root-cause tracking and oscillation detection | references/categories/bug-hunt-overnight.md |
| feature-build-overnight | Implement a feature from a PRD with acceptance-criteria checklist and behavior-preservation invariants | references/categories/feature-build-overnight.md |
| refactor-sweep-overnight | Mechanical refactor at scale (rename, restructure) with tests-must-stay-green-per-checkpoint | references/categories/refactor-sweep-overnight.md |
| docs-pass-overnight | Documentation generation/pass with hallucinated-API-signature refuse pattern and source-link requirements | references/categories/docs-pass-overnight.md |
| research-deep-overnight | Long-horizon web/code research synthesis with source-fabrication refuse and tighter $20 cost ceiling | references/categories/research-deep-overnight.md |

---

## Classification guidance

- The goal is the discriminator. "Add tests for the auth module" → `test-coverage-overnight`. "The auth tests are flaky, find why" → `bug-hunt-overnight`. "Add SSO to the login flow per PRD.md" → `feature-build-overnight`.
- If the user mentions a *runtime* but not a *goal type* ("run this on ralphthon overnight"), ask the goal first — runtime is Step 4, not Step 2.
- If the user mentions a CUT category ("upgrade the deps overnight"): explain it's cut from v1 per Safety/Operator analysis, point to `library/future-work.md`, suggest the closest shipping alternative (`dep-upgrade` → `bug-hunt-overnight` on the test failures after a manual upgrade).

---

## Interview loop

Follow `references/meta/interview-loop.md` for the generic rules. Overnight-specific notes:

- **Always ask runtime** even if the user bails. The drafted prompt cannot be runtime-agnostic — it emits the variant text per `runtime-adaptation.md`.
- **Always confirm budget** if the user specified > 8h OR > $50. Warn that METR data shows Opus 4.5 50%-time-horizon at 4h 49m.
- **Always confirm scope** for `feature-build-overnight` and `refactor-sweep-overnight` — these categories refuse to draft without an explicit scope manifest.
- **Always confirm verifier setup** for `bug-hunt-overnight` and `test-coverage-overnight` — these refuse to draft without a runnable test command.

---

## Review rubric (overnight-specific additions)

In addition to the 5 standard dimensions from `references/meta/quality-rubric.md` (Clarity, Specificity, Context, Completeness, Structure), every drafted overnight prompt is scored on:

| Dimension | Auto-fail condition |
|---|---|
| Overnight Discipline | `<cost_ceiling_usd>` or `<time_budget>` clause missing; `hard_cap < 2 × checkpoint_cadence`; `soft_cap != 0.9 × hard_cap` |
| Drift Resistance | `<drift_detection>` missing or `scope_manifest` empty; no PRD re-read cadence |
| Safety Posture | `<read_only_paths>`, `<write_scope>`, `<destructive_command_policy>`, `<git_remote_policy>`, `<credential_scope>` not all present |
| Verifiable Completion | `<progress_proof>` missing required fields; `<worker_judge_separation>` absent |

Auto-fail = ≤2 on the 5-point scale; prompt is rejected and Step 6 loops back regardless of user opinion.

---

## File map

- `SKILL.md` — this file
- `references/scaffold/universal.md` — the 14 mandatory clauses C1–C14
- `references/categories/*.md` — 6 category files
- `references/meta/` — 15 shared from build-prompt + 7 new overnight meta-files
- `references/research-distilled.md` — convention substrate distillation
- `library/<dated>.md` — saved drafts (versioned)
- `library/future-work.md` — cut categories with rationale
- `bin/build-overnight-run` — preflight + lockfile + caffeinate + telemetry wrapper
- `scripts/copy_to_clipboard.sh` — clipboard delivery (from build-prompt)
- `scripts/validate_index.sh` — dispatch-sync check (reports 6 categories)
- `build-overnight-research/test_skill.py` — Layer 1 + thin Layer 2 test harness
- `CHANGELOG.md` — version log

## Provenance

- Adapted from [`build-prompt`](https://github.com/jordjones/build-prompt-skill) v2 (2026-05-26 refresh).
- Convention substrate at `~/.claude/plans/jiggly-marinating-parnas-convention/` (11 reports, 35 convergent findings, 3 reconciler resolutions, 1 synthesis).
- Plan of record: `~/.claude/plans/jiggly-marinating-parnas.md`.
