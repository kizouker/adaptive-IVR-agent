#!/bin/bash
# Holdmate menu (Python + rich edition). Same workers as sh/holdmate.sh.
# Runs on: Rickard's Mac (M4). Modes: menu (default) | check. Direct: 1-4.
# Picks .venv python, else system python3 with rich, else uv run.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

if [ -x "$ROOT/.venv/bin/python" ] && "$ROOT/.venv/bin/python" -c "import rich" 2>/dev/null; then
  PY="$ROOT/.venv/bin/python"
elif python3 -c "import rich" 2>/dev/null; then
  PY="python3"
elif command -v uv >/dev/null 2>&1; then
  exec uv run --with rich --project "$ROOT" -m adaptive_ivr_agent.menu "$@"
else
  echo "rich is missing: python3 -m pip install --user rich (or brew install uv)"
  exit 1
fi
PYTHONPATH="$ROOT/src" exec "$PY" -m adaptive_ivr_agent.menu "$@"
