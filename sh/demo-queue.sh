#!/bin/bash
# Demo queue on all screens: run one quick lesson round to the queue,
# bake the board, and show the queue places the iPhone/Watch/widget display.
# Runs on: Rickard's Mac (M4). Modes: run (default) | check.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"

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
ok "inputs present"

[ "$MODE" = "check" ] && {
  title "Check only: nothing changed"
  info "would run: lessons --depth 0 --board-out board-state.json + bake lines"
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

step "Show queue"
what "Print the queue places the devices now display."
PLACES="$(python3 -c "
import json
d = json.load(open('$BOARD'))
out = [(c.get('persona'), t.get('queue_place'))
       for c in d.get('calls', []) for t in c.get('turns', [])
       if t.get('queue_place') is not None]
print(', '.join(f'{p}={q}' for p, q in out[-4:]) or 'none')
")"
[ "$PLACES" != "none" ] || fail "no queue places on the board"
ok "queue: $PLACES"

title "Done — look at the iPhone + Watch + widget"
