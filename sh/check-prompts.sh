#!/usr/bin/env bash
# Heuristic prompt-injection self-scan (OWASP LLM01 baseline). Fails loudly.
# Scans agent instruction files for directives that weaken prompt safety,
# such as ignore-the-instructions or reveal-the-prompt. CI runs this on
# every push. Full mapping: docs/security-review.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

fail() { echo "PROMPT SCAN FAIL: $1"; exit 1; }

TARGETS="AGENTS.MD ALL.MD CLAUDE.MD CODEX.MD MUSE.MD COACH.MD BLOCKED.MD"
present=""
for f in $TARGETS; do
  [ -f "$f" ] && present="$present $f"
done

weakening=$(git grep -nEi "ignore (all |your |previous |prior |earlier )*(instructions|rules|constraints|guardrails|safety)|disregard (all |your |previous |prior )*(instructions|safety|policy)|do anything now|DAN mode|jailbreak" -- $present || true)
[ -z "$weakening" ] || fail "instruction-weakening directive: $weakening"

disclosure=$(git grep -nEi "(reveal|disclose|print|output|show|repeat).{0,50}(system prompt|your instructions|your rules)" -- $present || true)
[ -z "$disclosure" ] || fail "prompt-disclosure directive: $disclosure"

echo "OK: prompt self-scan holds."
