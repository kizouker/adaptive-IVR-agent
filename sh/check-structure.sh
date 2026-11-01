#!/usr/bin/env bash
# Check repo structure: required layout, test mirror, hygiene. Fails loudly.
# Part of T-051. CI runs this on every push.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

fail() { echo "STRUCTURE FAIL: $1"; exit 1; }

for dir in src/adaptive_ivr_agent tests data docs openspec/specs features ui/board ui/board/src sh; do
  [ -d "$dir" ] || fail "missing dir $dir"
done

for doc in "docs/01_Vision _Adaptive_IVR_agent.md" "docs/02_The problem _Adaptive_IVR_agent.md" "docs/03_Real stories_Adaptive_IVR_agent.md" "docs/04_Roadmap_Adaptive_IVR_agent.md" "docs/05_Open questions_Adaptive_IVR_agent.md"; do
  [ -f "$doc" ] || fail "missing $doc"
done

[ "$(find openspec/specs -mindepth 1 -maxdepth 1 -type d | wc -l)" -ge 12 ] || fail "fewer than 12 spec dirs"
[ "$(find features -name '*.feature' | wc -l)" -ge 12 ] || fail "fewer than 12 feature files"

for src in src/adaptive_ivr_agent/*.py; do
  name=$(basename "$src" .py)
  [ "$name" = "__init__" ] && continue
  [ -f "tests/test_${name}.py" ] || fail "no tests/test_${name}.py for $src"
done

for script in sh/*.sh; do
  [ -x "$script" ] || fail "not executable: $script"
  bash -n "$script" || fail "syntax error: $script"
done

tracked_junk=$(git ls-files | grep -E "(__pycache__|\.pyc$|\.wav$|/board-state\.json$)" || true)
[ -z "$tracked_junk" ] || fail "junk tracked: $tracked_junk"

echo "OK: structure holds."
