#!/bin/sh
# validate_index.sh — verifies that SKILL.md's dispatch table and
# references/categories/ filesystem are in sync.
#
# Usage:
#   validate_index.sh
#
# Run from any directory. The script resolves paths relative to its own
# location: one level up from scripts/ is the skill root.
#
# Checks performed:
#   1. Every .md file in references/categories/ appears in SKILL.md's
#      dispatch table (as "references/categories/<name>.md").
#   2. Every dispatch-table reference in SKILL.md points to a real file.
#
# Exit codes:
#   0  — in sync
#   1  — out of sync (diff printed to stdout)
#   2  — environment error (SKILL.md or categories directory missing)
#
# Dependencies: POSIX sh, grep, find, sort, comm, basename, sed, mktemp.

set -eu

# Resolve skill root: parent of the directory containing this script.
script_dir="$(cd "$(dirname "$0")" && pwd)"
skill_root="$(cd "$script_dir/.." && pwd)"

skill_md="$skill_root/SKILL.md"
categories_dir="$skill_root/references/categories"

# Preflight.
if [ ! -f "$skill_md" ]; then
  echo "validate_index.sh: SKILL.md not found at $skill_md" >&2
  exit 2
fi
if [ ! -d "$categories_dir" ]; then
  echo "validate_index.sh: categories directory not found at $categories_dir" >&2
  exit 2
fi

# Work in temp files for POSIX-safe set comparison.
tmp_fs="$(mktemp)"
tmp_skill="$(mktemp)"
trap 'rm -f "$tmp_fs" "$tmp_skill"' EXIT INT TERM

# Category names from filesystem.
find "$categories_dir" -maxdepth 1 -type f -name '*.md' \
  -exec basename {} .md \; 2>/dev/null \
| sort -u > "$tmp_fs"

# Category names from SKILL.md dispatch table.
grep -oE 'references/categories/[a-z0-9][a-z0-9-]*\.md' "$skill_md" \
| sed -E 's|references/categories/||; s|\.md$||' \
| sort -u > "$tmp_skill"

# Compute set differences.
only_in_fs="$(comm -23 "$tmp_fs" "$tmp_skill")"
only_in_skill="$(comm -13 "$tmp_fs" "$tmp_skill")"

mismatch=0

if [ -n "$only_in_fs" ]; then
  mismatch=1
  echo "Categories present on disk but MISSING from SKILL.md dispatch table:"
  echo "$only_in_fs" | sed 's/^/  - /'
  echo ""
fi

if [ -n "$only_in_skill" ]; then
  mismatch=1
  echo "Categories referenced in SKILL.md but MISSING from disk:"
  echo "$only_in_skill" | sed 's/^/  - /'
  echo ""
fi

if [ "$mismatch" -eq 0 ]; then
  count="$(wc -l < "$tmp_fs" | tr -d ' ')"
  echo "OK: $count categories in sync between SKILL.md and references/categories/."
  exit 0
fi

echo "Dispatch table and filesystem are out of sync. Fix above and re-run." >&2
exit 1
