# Budget and telemetry

How `build-overnight` enforces budget discipline. The skill supports **two billing modes**; clause C1 (`<cost_ceiling_usd>`) is conditional on mode, while clause C15 (`<iteration_budget>`) and clause C2 (`<time_budget>`) are mandatory under both. Source: convention R3 + rc2 audit at `~/.claude/plans/jiggly-marinating-parnas-rc2-audit.md`.

---

## Mode 1: direct-api (pay-per-token)

User has `ANTHROPIC_API_KEY` set; the agent makes Messages API calls and `response.usage` is the ground truth for cost.

### Realistic cost ranges (R3 §4)

For an 8-hour Opus-led loop on a real repo:

| Cache state | Cost range | Notes |
|---|---|---|
| Well-cached (≥80% hit) | $10–19 | Achievable with C14 disciplines |
| Uncached (0% hit) | $50–100 | Common when timestamps in system prompt or mid-run model swaps |
| Worst case (compaction storms + retries) | $100–400+ | "$400 Overnight Bill" / $12K Kubernetes loop / Uber $1.2M |

Default cost ceiling: **$40 hard / $32 soft** (Phase 0.6 Q3). Sized for a typical well-cached overnight run plus headroom.

### Cost accumulator pattern (direct-api only)

The agent reads `response.usage` from every API call and writes a JSONL row to `.overnight/<run-id>/events.jsonl`:

```json
{"ts":"...","kind":"llm_call","iteration":42,"iteration_n_for_budget":42,"model":"claude-opus-4-7","input_tokens":12453,"cache_read_input_tokens":11200,"cache_creation_input_tokens":0,"output_tokens":850,"cost_usd":0.18,"cache_hit_rate":0.90}
```

After each iteration:

```
total_cost = sum(event.cost_usd for event in events.jsonl where event.kind == "llm_call")
```

If `total_cost >= soft_cap (e.g. $32)`, enter ship-mode. If `total_cost >= hard_cap (e.g. $40)`, abort.

### Three-layer kill-switch (direct-api)

1. **In-process accumulator** — the agent self-monitors via `response.usage` and `sys.exit(2)` at 100% of `<cost_ceiling_usd>` `<hard_cap>`.
2. **Proxy hard cap** — LiteLLM's `max_budget_per_session` or Helicone cost-window header returns 429 if (1) misfires. (Note: pin LiteLLM ≥1.83.0 or ≤1.82.2; GH issue #26672 in 1.82.3 silently bypasses the cap.)
3. **External cron `pkill`** — final backstop 1h after planned end.

Layer 2 requires a proxy setup (Helicone free tier or self-hosted LiteLLM). v1 prompt teaches Layer 1 + 3; documents Layer 2 here.

---

## Mode 2: oauth-subscription (Claude Code Pro/Max, Codex CLI)

User is signed into Claude Code via OAuth (or Codex CLI via subscription). There is no per-call USD billed to the user — the flat monthly fee covers all calls within rate limits. Per-call `response.usage` is not reliably exposed to the agent inside the loop, and even if it were, it does not correspond to the user's actual bill.

**The skill emits clause C1 in `subscription_disabled` form** under this mode:

```xml
<cost_ceiling_usd mode="subscription_disabled">
  <reason>flat-rate Claude Code Pro/Max subscription; no per-call USD to enforce</reason>
  <surface_phantom_usd_in_report>false</surface_phantom_usd_in_report>
  <primary_budget_gate>C15 iteration_budget</primary_budget_gate>
</cost_ceiling_usd>
```

### What replaces the USD gate

- **Primary gate: C15 `<iteration_budget>`** (hard 200, soft 160 default; ~25 iter/hr × 8h).
- **Secondary gate: C2 `<time_budget>`** (hard 8h, soft 7.2h default).
- **No phantom USD computation.** The agent does NOT estimate cost from list prices. REPORT.md surfaces iteration count and wall-clock, never phantom dollars.

### Two-layer kill-switch (oauth-subscription)

Layer 1 (proxy) doesn't apply (no proxy). The remaining two:

1. **In-process iteration counter** — the agent self-monitors via `iteration_n_for_budget` (written by `bin/build-overnight-run` on every `llm_call` event) and exits at C15 `<hard_cap>`.
2. **External cron `pkill`** — final backstop at `start_time + hard_hours + 1h`.

### Cache hygiene still matters (clause C14)

Cache discipline reduces **latency** under subscription, even though it does not save the user dollars. Faster iterations means more work shipped within both C15 and C2 caps. Same C14 rules apply: no timestamps in system prompt, no mid-run model swaps, etc.

### What we still log under subscription

- `iteration` count
- `iteration_n_for_budget` (== iteration in v1; reserved for future categories with iteration-skip semantics)
- `cache_hit_rate` (informational; useful for latency analysis)
- `wall_clock_elapsed`
- `model` (the agent should still pin a model; aliases rotate and break cache)

What we **don't** log:
- `cost_usd` (would be phantom)
- `cumulative_cost_usd` (same)

### Why `response.usage` is unreliable under Claude Code OAuth (rc2 audit)

The agent inside a ralph / ralphthon / ralph-loop / claude-p-chain loop on a user's Claude Code OAuth session IS Claude Code — it does not call the Messages API as an SDK consumer. Claude Code's session layer does not expose `response.usage` to user-space code in any documented programmatic surface as of 2026-05-27. Even when usage data is available (e.g., via the `/cost` slash-command), it is informational and does not correspond to the user's flat subscription bill. See `~/.claude/plans/jiggly-marinating-parnas-rc2-audit.md` §A.3 for the investigation.

---

## Anthropic prompt-cache mechanics (mode-agnostic)

These apply under BOTH billing modes.

- Default TTL: **5 minutes** (resets on each hit).
- Paid extended TTL: **1 hour** (GA on Bedrock 2026-01-26, beta on direct Anthropic API).
- Cache read price: **10% of base input price** (direct-api only; subscription is fixed-cost).
- Cache write price: **125% of base input price** (direct-api only).
- Break-even: **2 cache hits** make the write worth it (direct-api).

If the loop is active (≥1 LLM call every ~4 minutes), cache stays warm forever. Long pauses (>5 min) lose the cache.

## Cache hygiene (clause C14, mode-agnostic)

The prompt MUST forbid:
- **Timestamps in system prompt** — invalidates the entire cached prefix.
- **Mid-run tool changes** — adding/removing tools breaks the cache breakpoint above them.
- **Mid-run model changes** — different model = different cache space.
- **Mid-run system-prompt edits** — invalidates the prefix.

The prompt MUST prefer:
- **Static breakpoint above tools** — system prompt + cache breakpoint + tools cached together.
- **Append-only message history** — never edit prior messages.

---

## Anomaly detection (mode-agnostic)

Append a `cache_anomaly` event when cache hit rate drops unexpectedly:

```json
{"ts":"...","kind":"cache_anomaly","iteration":12,"cache_hit_rate":0.31,"prior_hit_rate":0.87,"hypothesis":"system_prompt_changed_unexpectedly"}
```

Under direct-api this signals **future cost spike**. Under subscription this signals **latency degradation** — iterations will be slower, fewer of them will fit in the wall-clock cap.

The morning report surfaces these regardless of mode.

---

## Cost-per-task benchmark seed (direct-api only)

| Category | Typical cost (well-cached, 4–8h, direct-api) | High-end (uncached / retry storm) |
|---|---|---|
| test-coverage | $5–15 | $30–60 |
| bug-hunt | $8–20 | $50–100 |
| feature-build | $15–40 | $80–200 |
| refactor-sweep | $10–25 | $50–120 |
| docs-pass | $3–10 | $20–50 |
| research-deep | $5–15 + Firecrawl/Tavily/Exa burn | $25–80 |

Set the per-category cost ceiling at ~1.5× typical to leave headroom for cache misses.

**Under subscription, these are not applicable.** The relevant benchmark instead is **iterations to goal-met** — to be populated from real runs in v1.1.

---

## Kill-switch protocol summary

### Direct-api

```
1. soft_cap_usd_hit (in-process):
     log "ship_mode_entered" reason=soft_cap_cost
     commit WIP; write OVERNIGHT_RUN_REPORT.md with why_stopped=BUDGET
     push branch; open draft PR; exit 0
2. hard_cap_usd_hit (in-process):
     log "hard_cap_breached" kind=cost; sys.exit(2)
3. proxy_429 (LiteLLM/Helicone):
     agent observes 429, treats as hard cap, falls through to step 2
4. external_cron (backstop):
     pkill -f "<agent process>"; wrapper trap writes FAILURE.md stub
```

### OAuth-subscription

```
1. soft_iter_hit (in-process):
     log "ship_mode_entered" reason=soft_cap_iter
     commit WIP; write OVERNIGHT_RUN_REPORT.md with why_stopped=BUDGET
     push branch; open draft PR; exit 0
2. hard_iter_hit (in-process):
     log "hard_cap_breached" kind=iter; sys.exit(2)
3. soft_time_hit (in-process; usually fires before #2):
     same as soft_iter_hit but reason=soft_cap_time
4. hard_time_hit (in-process):
     log "hard_cap_breached" kind=time; sys.exit(2)
5. external_cron (backstop):
     pkill -f "<agent process>"; wrapper trap writes FAILURE.md stub
```

Never rely solely on `max_tokens` — it caps per-call, not per-run.
