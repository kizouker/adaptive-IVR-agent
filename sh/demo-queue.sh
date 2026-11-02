#!/bin/bash
# Demo queue on all screens: run one quick lesson round to the queue,
# bake the board, then count the latest queue place down slowly so the
# iPhone/Watch/widget (5s poll) can follow it live to 0.
# Runs on: Rickard's Mac (M4). Modes: run (default) | check.
# Env: QUEUE_START (default 50), QUEUE_DELAY seconds between ticks (default 5).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"
START="${QUEUE_START:-50}"
DELAY="${QUEUE_DELAY:-5}"

LINES="$ROOT/data/doorkeeper-lines.json"
PHRASEBOOKS="$ROOT/data/role-phrasebooks.json"
KNOWLEDGE="$ROOT/data/holdmate-knowledge.json"
LESSONS="$ROOT/data/holdmate-lessons.jsonl"
BOARD="$ROOT/ui/board/public/board-state.json"

title "Demo queue ($MODE)"

step "Preflight"
what "Check input files exist before running anything."
[ -f "$LINES" ] || fail "missing lines: $LINES"
[ -f "$PHRASEBOOKS" ] || fail "missing phrasebooks: $PHRASEBOOKS"
case "$START" in ''|*[!0-9]*) fail "QUEUE_START must be a number (saw $START)";; esac
case "$DELAY" in ''|*[!0-9]*) fail "QUEUE_DELAY must be whole seconds (saw $DELAY)";; esac
ok "inputs present (count $START to 0, tick every ${DELAY}s)"

[ "$MODE" = "check" ] && {
  title "Check only: nothing changed"
  info "would run: lessons --depth 0 --board-out board-state.json + bake lines"
  info "would count: place $START down to 0, one tick per ${DELAY}s"
  exit 0
}

step "Run lessons to queue"
what "One fast round (depth 0, silent); every transfer ends in the queue."
run "holdmate lessons --depth 0 --board-out ui/board/public/board-state.json"
# shellcheck disable=SC2086
PYTHONPATH="$ROOT/src" python3 -m adaptive_ivr_agent.holdmate \
  --phrasebooks "$PHRASEBOOKS" --lines "$LINES" \
  --knowledge "$KNOWLEDGE" --lessons "$LESSONS" \
  --depth 0 --board-out "$BOARD" || fail "lessons failed"
[ -s "$BOARD" ] || fail "board missing: $BOARD"
ok "board: ${BOARD#$ROOT/}"

step "Bake lines"
what "Attach the 43 robot lines so the fake CLI keeps working."
run "bake-board.py --board board-state.json --lines doorkeeper-lines.json"
python3 "$ROOT/sh/bake-board.py" --board "$BOARD" --lines "$LINES" \
  || fail "bake failed"
ok "lines baked"

step "Count down"
what "Rewrite the latest queue place $START to 0, one tick per ${DELAY}s, so screens follow live. Ctrl-C stops early."
PLACE="$START"
stop_early() {
  echo ""
  warn "stopped early at place $PLACE (re-run to start over)"
  exit 0
}
trap stop_early INT
p="$START"
while [ "$p" -ge 0 ]; do
  PLACE="$p"
  python3 - "$BOARD" "$p" <<'EOF' || fail "could not write place $p to the board"
import json, sys
from datetime import datetime, timezone
path, place = sys.argv[1], int(sys.argv[2])
board = json.load(open(path))
calls = board.get("calls") or []
if not calls:
    sys.exit("no calls on the board")
turns = calls[-1].get("turns") or []
target = next((t for t in reversed(turns) if t.get("queue_place") is not None), None)
if target is None:
    sys.exit("no queue turn on the board")
target["queue_place"] = place
board["generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
json.dump(board, open(path, "w"), ensure_ascii=False)
print(f"place {place}")
EOF
  [ "$p" -eq 0 ] && break
  sleep "$DELAY"
  p=$((p - 1))
done
trap - INT
END="$(python3 -c "
import json
d = json.load(open('$BOARD'))
turns = [t for t in d['calls'][-1]['turns'] if t.get('queue_place') is not None]
print(turns[-1]['queue_place'])
")"
[ "$END" = "0" ] || fail "board did not end at 0 (saw $END)"
ok "countdown finished at 0"

title "Done — screens should have blinked YOUR TURN at 0"
