#!/bin/bash
# Replay: self-call against the scripted line + offline intent eval + pytest.
# Runs on: any machine with python3 (Mac or python:3.12-slim container).
# Modes: run (default) | check (preflight only, changes nothing).
# One command: docker compose run --rm replay   |   locally: bash sh/replay.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
ROOT="$(cd "$HERE/.." && pwd)"
MODE="${1:-run}"
cd "$ROOT"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"

if [ -n "${PY:-}" ]; then
  :
elif [ -x "$ROOT/.venv/bin/python" ]; then
  PY="$ROOT/.venv/bin/python"
else
  PY="$(command -v python3 || true)"
fi

title "Replay ($MODE)"

step "Preflight"
what "Check python, data files and eval before running anything."
[ -n "$PY" ] || fail "python3 is missing (install python 3.12+)"
ok "python: $PY"
for f in data/role-phrasebooks.json data/doorkeeper-lines.json eval/llm_intent_eval.py; do
  [ -f "$f" ] || fail "missing file: $f (run from the repo root checkout)"
  ok "file: $f"
done
"$PY" -m pytest --version >/dev/null 2>&1 || fail "pytest missing for $PY (compose installs it; locally: use the repo .venv)"

[ "$MODE" = "check" ] && { title "Check only: nothing changed"; exit 0; }
[ "$MODE" = "run" ] || fail "unknown mode: $MODE (use run or check)"

step "Self-call"
what "Holdmate calls the scripted copy of the line; knowledge goes to /tmp, repo data untouched."
"$PY" -m adaptive_ivr_agent.holdmate \
  --phrasebooks data/role-phrasebooks.json \
  --lines data/doorkeeper-lines.json \
  --knowledge /tmp/replay-knowledge.json \
  --lessons /tmp/replay-lessons.jsonl \
  --fresh --depth 2 || fail "self-call failed (see output above)"
[ -s /tmp/replay-lessons.jsonl ] || fail "self-call wrote no lessons to /tmp/replay-lessons.jsonl"
ok "self-call done, lessons: /tmp/replay-lessons.jsonl"

step "Offline intent eval"
what "Heuristic baseline over labeled misses; no API key, no network."
"$PY" eval/llm_intent_eval.py || fail "offline eval failed (see output above)"
ok "offline eval done"

step "Pytest"
what "Full test suite against the same code the container would run."
"$PY" -m pytest -q || fail "pytest failed (see output above)"
ok "pytest done"

title "Replay: OK (self-call + offline eval + pytest)"
