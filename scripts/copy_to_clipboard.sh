#!/bin/sh
# copy_to_clipboard.sh — cross-platform clipboard copy with fallback chain.
#
# Usage:
#   echo "text" | copy_to_clipboard.sh
#   copy_to_clipboard.sh "text"
#   copy_to_clipboard.sh < file.txt
#
# Fallback order:
#   1. pbcopy           (macOS)
#   2. xclip            (X11 Linux)
#   3. wl-copy          (Wayland Linux)
#   4. stdout           (no clipboard tool available; prints to stdout)
#
# Exit codes:
#   0  — copied successfully, OR no clipboard tool found but content printed to stdout
#   1  — usage error (e.g., stdin empty AND no argument given)
#
# Status messages are written to stderr so they don't pollute stdout.

set -eu

# Read input: prefer argument, fall back to stdin.
if [ "$#" -ge 1 ]; then
  input="$1"
elif [ ! -t 0 ]; then
  input="$(cat)"
else
  echo "copy_to_clipboard.sh: no input (stdin empty and no argument)" >&2
  exit 1
fi

# Try clipboard tools in order.
if command -v pbcopy >/dev/null 2>&1; then
  printf '%s' "$input" | pbcopy
  echo "Copied via pbcopy (macOS)." >&2
  exit 0
fi

if command -v xclip >/dev/null 2>&1; then
  printf '%s' "$input" | xclip -selection clipboard
  echo "Copied via xclip (X11)." >&2
  exit 0
fi

if command -v wl-copy >/dev/null 2>&1; then
  printf '%s' "$input" | wl-copy
  echo "Copied via wl-copy (Wayland)." >&2
  exit 0
fi

# Final fallback: print to stdout.
echo "No clipboard tool found (pbcopy, xclip, wl-copy). Printing to stdout:" >&2
printf '%s\n' "$input"
exit 0
