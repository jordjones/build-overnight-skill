# Cost and telemetry

How `build-overnight` enforces cost discipline (clause C1) and measures cache discipline (clause C14). Source: R3.

## Realistic cost ranges (R3 §4)

For an 8-hour Opus-led loop on a real repo:

| Cache state | Cost range | Notes |
|---|---|---|
| Well-cached (≥80% hit) | $10–19 | Achievable with C14 disciplines |
| Uncached (0% hit) | $50–100 | Common when timestamps in system prompt or mid-run model swaps |
| Worst case (compaction storms + retries) | $100–400+ | "$400 Overnight Bill" / $12K Kubernetes loop / Uber $1.2M |

Default cost ceiling: **$40 hard / $32 soft** (Phase 0.6 Q3). Sized for a typical well-cached overnight run plus headroom.

## Anthropic prompt-cache mechanics (2026)

- Default TTL: **5 minutes** (resets on each hit).
- Paid extended TTL: **1 hour** (GA on Bedrock 2026-01-26, in beta on direct Anthropic API).
- Cache read price: **10% of base input price**.
- Cache write price: **125% of base input price**.
- Break-even: **2 cache hits** make the write worth it.

If the loop is active (≥1 LLM call every ~4 minutes), cache stays warm forever. Long pauses (>5 min) lose the cache and pay cold-write surcharge on next call.

## Cache hygiene (clause C14)

The prompt MUST forbid:
- **Timestamps in system prompt** — invalidates the entire cached prefix on every call.
- **Mid-run tool changes** — adding/removing tools breaks the cache breakpoint above them.
- **Mid-run model changes** — different model = different cache space.
- **Mid-run system-prompt edits** — invalidates the prefix.

The prompt MUST prefer:
- **Static breakpoint above tools** — system prompt + cache breakpoint + tools (above) cached together.
- **Append-only message history** — never edit prior messages.

## Cost accumulator pattern

The agent reads `response.usage` from every API call and writes a JSONL row to `.overnight/<run-id>/events.jsonl`:

```json
{"ts":"...","kind":"llm_call","iteration":42,"model":"claude-opus-4-7","input_tokens":12453,"cache_read_input_tokens":11200,"cache_creation_input_tokens":0,"output_tokens":850,"cost_usd":0.18,"cache_hit_rate":0.90}
```

After each iteration, the agent computes cumulative cost:

```
total_cost = sum(event.cost_usd for event in events.jsonl where event.kind == "llm_call")
```

If `total_cost >= soft_cap (e.g. $32)`, enter ship-mode. If `total_cost >= hard_cap (e.g. $40)`, abort.

**Three independent layers of cost enforcement** (per R3):
1. **In-process accumulator** — the agent self-monitors via `response.usage` and `sys.exit(2)` at 100%.
2. **Proxy hard cap** — LiteLLM's `max_budget_per_session` or Helicone cost-window header returns 429 if (1) misfires.
3. **External cron `pkill`** — final backstop 1h after planned end.

Layer 2 requires a proxy setup (Helicone free tier or self-hosted LiteLLM). v1 prompt teaches Layer 1; documents Layers 2 and 3 in this file.

## LiteLLM `max_budget_per_session` gotcha (R3)

LiteLLM has a known enforcement-bypass bug in v1.82.3 (GH issue #26672). Pin to a known-good version (≥1.83.0 or ≤1.82.2). The audit trail's COST.json is the ground truth; trust the in-process accumulator over the proxy in v1.

## Cache-hit measurement

Cache hit rate per iteration:

```
cache_hit_rate = cache_read_input_tokens / (cache_read_input_tokens + cache_creation_input_tokens + non_cached_input_tokens)
```

Target: ≥ 0.80 by iteration 5 (cache should be warm by then for any non-trivial loop).

If iteration N shows cache_hit_rate < 0.50 unexpectedly:
- Check for timestamps in system prompt (most common cause).
- Check for tool or model swap.
- Check for system-prompt edit (e.g., changed via PRD.md re-read incorrectly).

Append a `cache_anomaly` event when this fires:

```json
{"ts":"...","kind":"cache_anomaly","iteration":12,"cache_hit_rate":0.31,"prior_hit_rate":0.87,"hypothesis":"system_prompt_changed_unexpectedly"}
```

The morning report surfaces these.

## Anthropic Workbench observability (2026)

Workbench dashboard shows per-API-key usage, per-day cost, recent traces. Useful for postmortem but NOT real-time during a run (data is batched). For real-time:
- The agent's own JSONL log (always available, $0).
- Helicone free tier (proxy, ~real-time dashboard).
- LiteLLM with the `/v1/spend/logs` endpoint.

v1 ships the JSONL log only. Helicone/LiteLLM documented here, not auto-installed.

## Cost-per-task benchmark seed

Initial benchmarks from convention research + community reports. These will rotate into `library/cost-benchmarks.md` once real runs accumulate.

| Category | Typical cost (well-cached, 4–8h) | High-end (uncached / retry storm) |
|---|---|---|
| test-coverage | $5–15 | $30–60 |
| bug-hunt | $8–20 | $50–100 |
| feature-build | $15–40 | $80–200 |
| refactor-sweep | $10–25 | $50–120 |
| docs-pass | $3–10 | $20–50 |
| research-deep | $5–15 + Firecrawl/Tavily/Exa burn | $25–80 |

Set the per-category cost ceiling at ~1.5× typical to leave headroom for cache misses while still tripping on anomalies.

## Kill-switch protocol summary

```
1. soft_cap_hit (in-process):
     log "ship_mode_entered"
     commit WIP
     write OVERNIGHT_RUN_REPORT.md with why_stopped=BUDGET
     push branch, open draft PR
     exit 0
2. hard_cap_hit (in-process):
     log "hard_cap_breached"
     sys.exit(2)
3. proxy_429 (LiteLLM/Helicone):
     agent observes 429, treats as hard cap, falls through to step 2
4. external_cron (optional backstop):
     pkill -f "<agent process>"
     wrapper trap writes FAILURE.md stub
```

Never rely solely on `max_tokens` — it caps per-call, not per-run.
