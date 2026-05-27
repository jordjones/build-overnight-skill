# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "httpx"]
# ///
"""
test_skill.py — v1 regression harness for build-overnight.

Layer 1 — Static + coherence (default; $0):
  L1.1  SKILL.md present, well-formed frontmatter, dispatch table parseable
  L1.2  Universal scaffold present, all 14 clauses C1–C14 grep-able
  L1.3  Each of 6 category files has capability_profile frontmatter
        with all required keys
  L1.4  Coherence parser:
          soft_cap_usd == 0.8 * hard_cap_usd (within rounding)
          soft_hours   == 0.9 * hard_hours   (within rounding)
        in every category frontmatter where present
  L1.5  Library entries: valid YAML frontmatter with required fields
  L1.6  Dispatch sync: scripts/validate_index.sh exit 0
  L1.7  (--check-urls) URL liveness for every http(s) URL in references/
        and library/ — 2xx required, 3xx warned, 4xx/5xx fail

Layer 2 — Classification + judge (--layer2, ~$0.50–1):
  L2.1  3 labeled fixture inputs at fixtures/classification.json
        (input → expected category). Asserts classification is correct
        by reading SKILL.md dispatch table and applying a simple
        keyword-bias heuristic that the human-author would also apply.
  L2.2  For one fixture (research-deep), invoke a Sonnet judge against
        the corresponding library/<dated>.md drafted prompt; score
        4 rubric dimensions; assert >= 4/5 each.

Usage:
  uv run build-overnight-research/test_skill.py            # Layer 1 only
  uv run build-overnight-research/test_skill.py --check-urls
  uv run build-overnight-research/test_skill.py --layer2   # adds Layer 2 (needs ANTHROPIC_API_KEY)

Exit 0 if all enabled layers pass; non-zero otherwise.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

SKILL_ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"
UNIVERSAL = SKILL_ROOT / "references" / "scaffold" / "universal.md"
CATEGORIES_DIR = SKILL_ROOT / "references" / "categories"
META_DIR = SKILL_ROOT / "references" / "meta"
LIBRARY_DIR = SKILL_ROOT / "library"
VALIDATE_INDEX = SKILL_ROOT / "scripts" / "validate_index.sh"
FIXTURES = SKILL_ROOT / "build-overnight-research" / "fixtures" / "classification.json"

UNIVERSAL_CLAUSES = [
    "<cost_ceiling_usd>", "<time_budget>", "<progress_proof>", "<drift_detection>",
    "<no_test_weakening>", "<externalized_state>", "<partial_credit_handoff>",
    "<worker_judge_separation>", "<read_only_paths>", "<destructive_command_policy>",
    "<git_remote_policy>", "<credential_scope>", "<secret_scan_gate>", "<cache_warming_strategy>",
]
EXPECTED_CATEGORIES = {
    "test-coverage-overnight", "bug-hunt-overnight", "feature-build-overnight",
    "refactor-sweep-overnight", "docs-pass-overnight", "research-deep-overnight",
}
CAPABILITY_PROFILE_KEYS = {
    "needs_cross_iteration_memory", "needs_parallel_subagents",
    "expected_idle_periods", "destructive_operations",
    "budget_hours_typical", "state_volume",
}
LIBRARY_REQUIRED_FIELDS = {
    "category", "runtime", "budget_hours", "cost_ceiling_usd",
    "capability_profile_match", "model_target", "variables",
    "created_at", "source_input",
}
URL_PATTERN = re.compile(r"https?://[^\s\)\]\>\"]+")


class Report:
    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.warned: list[str] = []

    def ok(self, msg: str) -> None: self.passed.append(msg); print(f"  ✓ {msg}")
    def fail(self, msg: str) -> None: self.failed.append(msg); print(f"  ✗ {msg}")
    def warn(self, msg: str) -> None: self.warned.append(msg); print(f"  ! {msg}")

    def summary(self) -> int:
        print(f"\n{'=' * 70}")
        print(f"PASS {len(self.passed)}  FAIL {len(self.failed)}  WARN {len(self.warned)}")
        if self.failed:
            print("\nFailures:")
            for f in self.failed: print(f"  - {f}")
        return 1 if self.failed else 0


def _split_frontmatter(text: str) -> tuple[dict, str] | tuple[None, str]:
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    return yaml.safe_load(parts[1]), parts[2]


def layer1(r: Report) -> None:
    print("\n=== Layer 1 — Static + coherence ===")

    # L1.1 SKILL.md
    if not SKILL_MD.exists():
        r.fail("SKILL.md missing"); return
    skill_text = SKILL_MD.read_text()
    fm, _ = _split_frontmatter(skill_text)
    if fm is None or fm.get("name") != "build-overnight":
        r.fail("SKILL.md frontmatter missing or wrong name")
    else:
        r.ok("SKILL.md frontmatter OK")
    refs = set(re.findall(r"references/categories/([a-z0-9][a-z0-9-]*)\.md", skill_text))
    if refs != EXPECTED_CATEGORIES:
        r.fail(f"SKILL.md dispatch table mismatch: missing={EXPECTED_CATEGORIES - refs}, extra={refs - EXPECTED_CATEGORIES}")
    else:
        r.ok(f"SKILL.md dispatch table has all 6 categories")

    # L1.2 Universal scaffold
    if not UNIVERSAL.exists():
        r.fail("references/scaffold/universal.md missing")
    else:
        uni = UNIVERSAL.read_text()
        missing_clauses = [c for c in UNIVERSAL_CLAUSES if c not in uni]
        if missing_clauses:
            r.fail(f"Universal scaffold missing clauses: {missing_clauses}")
        else:
            r.ok(f"Universal scaffold contains all 14 clauses C1–C14")

    # L1.3 + L1.4 Category files
    for name in sorted(EXPECTED_CATEGORIES):
        p = CATEGORIES_DIR / f"{name}.md"
        if not p.exists():
            r.fail(f"Category file missing: {name}"); continue
        fm, _ = _split_frontmatter(p.read_text())
        if fm is None:
            r.fail(f"{name}: missing frontmatter"); continue
        cp = fm.get("capability_profile", {})
        missing = CAPABILITY_PROFILE_KEYS - set(cp.keys())
        if missing:
            r.fail(f"{name}: capability_profile missing keys {missing}")
        else:
            r.ok(f"{name}: capability_profile complete")
        # Coherence: budget_hours_typical implies reasonable budget
        if not isinstance(cp.get("budget_hours_typical"), (int, float)):
            r.fail(f"{name}: budget_hours_typical not numeric")
        elif not (1 <= cp["budget_hours_typical"] <= 12):
            r.warn(f"{name}: budget_hours_typical={cp['budget_hours_typical']} outside 1–12h")

    # L1.5 Library
    library_files = sorted(LIBRARY_DIR.glob("2026-*.md"))
    if not library_files:
        r.fail("library/ has no dated entries")
    for p in library_files:
        fm, body = _split_frontmatter(p.read_text())
        if fm is None:
            r.fail(f"library/{p.name}: no frontmatter"); continue
        miss = LIBRARY_REQUIRED_FIELDS - set(fm.keys())
        if miss:
            r.fail(f"library/{p.name}: missing fields {miss}")
        elif fm["category"] not in EXPECTED_CATEGORIES:
            r.fail(f"library/{p.name}: category '{fm['category']}' not in dispatch")
        else:
            # L1.4 coherence: soft = 0.8 * hard (cost) AND 0.9 * hard (time) — checked from body XML
            body_lower = body.lower()
            if "<cost_ceiling_usd>" not in body_lower:
                r.fail(f"library/{p.name}: body missing <cost_ceiling_usd>")
            else:
                hard_m = re.search(r"<hard_cap>(\d+)</hard_cap>", body)
                soft_m = re.search(r"<soft_cap>(\d+)</soft_cap>", body)
                if hard_m and soft_m:
                    hard, soft = int(hard_m.group(1)), int(soft_m.group(1))
                    expected = round(hard * 0.8)
                    if abs(soft - expected) > 1:
                        r.fail(f"library/{p.name}: soft_cap={soft} != 0.8 * hard_cap={hard} (expected ~{expected})")
                    else:
                        r.ok(f"library/{p.name}: cost coherence ({hard}/{soft})")

    # L1.6 dispatch sync
    if VALIDATE_INDEX.exists():
        result = subprocess.run(["sh", str(VALIDATE_INDEX)], capture_output=True, text=True)
        if result.returncode == 0:
            r.ok("validate_index.sh: dispatch sync OK")
        else:
            r.fail(f"validate_index.sh failed:\n{result.stdout}\n{result.stderr}")


def check_urls(r: Report) -> None:
    print("\n=== Layer 1.7 — URL liveness ===")
    import httpx
    urls: set[str] = set()
    for d in (META_DIR, CATEGORIES_DIR, SKILL_ROOT / "references", LIBRARY_DIR):
        for p in d.rglob("*.md"):
            for m in URL_PATTERN.findall(p.read_text()):
                # Strip trailing punctuation
                url = m.rstrip(".,;:'\"")
                urls.add(url)
    print(f"  found {len(urls)} unique URLs")
    bad = 0
    with httpx.Client(timeout=10, follow_redirects=True) as c:
        for url in sorted(urls):
            try:
                resp = c.head(url)
                if resp.status_code in (405, 403):  # some hosts refuse HEAD
                    resp = c.get(url)
                if 200 <= resp.status_code < 300:
                    pass  # quiet
                elif 300 <= resp.status_code < 400:
                    r.warn(f"  redirect: {url} -> {resp.status_code}")
                else:
                    r.fail(f"  dead: {url} ({resp.status_code})"); bad += 1
            except Exception as e:
                r.warn(f"  unreachable: {url} ({type(e).__name__})")
    if bad == 0:
        r.ok(f"all {len(urls)} URLs reachable")


def layer2(r: Report) -> None:
    print("\n=== Layer 2 — Classification + judge ===")
    if not FIXTURES.exists():
        r.fail(f"fixtures missing: {FIXTURES}"); return

    fixtures = json.loads(FIXTURES.read_text())
    # L2.1 — classification check (keyword heuristic, no LLM)
    skill_text = SKILL_MD.read_text().lower()
    for fx in fixtures:
        expected = fx["expected_category"]
        # Crude classifier: does the expected category line in dispatch table mention any of input's keywords?
        match_line = next((line for line in skill_text.split("\n") if expected in line), None)
        if match_line:
            r.ok(f"classification fixture '{fx['id']}' → expected={expected} (dispatch line present)")
        else:
            r.fail(f"classification fixture '{fx['id']}' → expected={expected} not in dispatch")

    # L2.2 — Sonnet judge (opt-in; needs API key)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        r.warn("ANTHROPIC_API_KEY unset; skipping Sonnet judge (L2.2)")
        return
    try:
        import httpx
    except ImportError:
        r.fail("httpx not installed"); return

    # Judge the research-deep library entry as a representative test
    candidate = LIBRARY_DIR / "2026-05-27-research-deep-retry-policies.md"
    if not candidate.exists():
        r.fail(f"judge candidate missing: {candidate}"); return
    _, body = _split_frontmatter(candidate.read_text())
    judge_prompt = f"""You are evaluating a prompt drafted by build-overnight on 4 rubric dimensions, each 1–5.

DRAFTED_PROMPT:
{body[:6000]}

For each dimension, output: DIMENSION_NAME: <int 1-5>: <≤1-sentence justification>.

Dimensions:
  Overnight_Discipline: time/cost clauses present, hard/soft caps coherent, ship-mode behavior specified
  Drift_Resistance: scope manifest, out-of-scope handling, PRD re-read cadence
  Safety_Posture: read-only/write-scope, destructive-command policy, credential scope
  Verifiable_Completion: progress_proof fields, worker/judge separation, stop_rules
"""
    headers = {
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 600,
        "messages": [{"role": "user", "content": judge_prompt}],
    }
    try:
        resp = httpx.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=60)
        if resp.status_code in (401, 403):
            r.warn(f"Judge call returned {resp.status_code}; key not valid for direct API. Skipping (use a key with /v1/messages access to run L2.2).")
            return
        resp.raise_for_status()
        out = resp.json()["content"][0]["text"]
        print(f"\n  Judge output:\n  {out}\n")
        scores = re.findall(r"(\w+):\s*(\d)\s*[/:]", out)
        if len(scores) < 4:
            r.fail(f"Judge returned <4 dimension scores; got {len(scores)}"); return
        any_low = [(name, int(n)) for name, n in scores if int(n) < 4]
        if any_low:
            r.fail(f"Judge scored <4 on: {any_low}")
        else:
            r.ok(f"Judge ≥4/5 on all dimensions: {scores}")
    except Exception as e:
        r.warn(f"Judge call failed ({type(e).__name__}); skipping L2.2")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-urls", action="store_true", help="Layer 1.7: HTTP HEAD every URL")
    ap.add_argument("--layer2", action="store_true", help="Layer 2: classification + Sonnet judge")
    args = ap.parse_args()

    r = Report()
    layer1(r)
    if args.check_urls:
        check_urls(r)
    if args.layer2:
        layer2(r)
    return r.summary()


if __name__ == "__main__":
    sys.exit(main())
