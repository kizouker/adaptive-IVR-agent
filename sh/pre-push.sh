#!/usr/bin/env bash
# Local gate before pushing: req coverage, shell syntax/lint, tests if present.
set -euo pipefail
cd "$(dirname "$0")/.."

./sh/check-reqs.sh

for f in sh/*.sh; do bash -n "$f" && echo "syntax OK: $f"; done

if command -v shellcheck >/dev/null; then
  shellcheck -S warning sh/*.sh
else
  echo "shellcheck not installed, skipped (brew install shellcheck)"
fi

if [ -d tests ]; then
  uv run --with pytest pytest -q
else
  echo "no tests/ dir yet, skipped"
fi

echo "Pre-push checks passed."
