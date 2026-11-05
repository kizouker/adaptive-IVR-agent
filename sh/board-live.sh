#!/usr/bin/env bash
# Live Meta-models board in one command: bake telemetry + costs, mirror the
# provenance tail live, serve the web board, open it. Ctrl+C stops all.
# Runs on: Rickard's Mac. Modes: live (default) | check (preflight only).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT" || exit 1

PORT="5173"
HOST="127.0.0.1"
BOARD_DIR="${BOARD_DIR:-$ROOT/ui/board}"
OPEN="1"
MODE="live"
while [ "$#" -gt 0 ]; do
  case "$1" in
    check) MODE="check" ;;
    --no-open) OPEN="0" ;;
    --port=*) PORT="${1#--port=}" ;;
    --port)
      shift
      [ "$#" -gt 0 ] || { echo "usage: board-live.sh [check] [--port N] [--no-open]" >&2; exit 2; }
      PORT="$1"
      ;;
    *) echo "unknown arg: $1 (want check | --port N | --no-open)" >&2; exit 2 ;;
  esac
  shift
done

fail() { echo "FAIL: $1" >&2; exit 1; }
ok() { echo "OK: $1"; }

command -v python3 >/dev/null 2>&1 || fail "python3 missing"
command -v node >/dev/null 2>&1 || fail "node missing (brew install node)"
command -v npm >/dev/null 2>&1 || fail "npm missing (brew install node)"
[ -d "$BOARD_DIR/node_modules" ] || fail "board deps missing (cd ui/board && npm ci)"
[ -f "data/doorkeeper-lines.json" ] || fail "data/doorkeeper-lines.json missing"
ok "preflight: python3, node, npm, board deps, lines"

case "$PORT" in ''|*[!0-9]*) fail "--port needs a number, got '$PORT'" ;; esac
if [ "$MODE" = "check" ]; then
  echo "check only: nothing started (board URL would be http://$HOST:$PORT/)"
  exit 0
fi
if curl -sf -o /dev/null --max-time 2 "http://$HOST:$PORT/" 2>/dev/null; then
  fail "something already answers http://$HOST:$PORT/ (stop it or pick --port=N)"
fi

python3 sh/bake-board.py --board ui/board/public/board-state.json \
  --lines data/doorkeeper-lines.json || fail "bake-board.py failed"

TEL_LOG="/tmp/holdmate-telemetry-live.log"
BOARD_LOG="/tmp/holdmate-board-live.log"
python3 sh/telemetry-live.py --provenance data/provenance.jsonl \
  --out ui/board/public/telemetry.json >"$TEL_LOG" 2>&1 &
TEL_PID="$!"
(cd "$BOARD_DIR" && npm run dev -- --port "$PORT" --host "$HOST") >"$BOARD_LOG" 2>&1 &
BOARD_PID="$!"

cleanup() {
  kill "$TEL_PID" "$BOARD_PID" 2>/dev/null
  wait 2>/dev/null
  echo "stopped (logs: $TEL_LOG $BOARD_LOG)"
  exit 0
}
trap cleanup INT TERM

ready="0"
for _ in $(seq 1 30); do
  if curl -sf -o /dev/null --max-time 2 "http://$HOST:$PORT/" 2>/dev/null; then
    ready="1"
    break
  fi
  sleep 1
done
[ "$ready" = "1" ] || { kill "$TEL_PID" "$BOARD_PID" 2>/dev/null; fail "board never answered (see $BOARD_LOG)"; }
ok "board live: http://$HOST:$PORT/"
[ "$OPEN" = "1" ] && command -v open >/dev/null 2>&1 && open "http://$HOST:$PORT/"
echo "watcher pid $TEL_PID, board pid $BOARD_PID — Ctrl+C stops both"
wait
