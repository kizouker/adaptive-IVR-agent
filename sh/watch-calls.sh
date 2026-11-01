#!/usr/bin/env bash
# Live call board: two personas phone in turn by turn; regenerates the board.
# Open /tmp/holdmate-board.html in a browser (reloads every 3 s).
# Usage: watch-calls.sh [persona1] [persona2]. Part of T-045 (#47).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

P1="${1:-ny-arbetslos}"
P2="${2:-sjukskriven}"
OUT="/tmp/holdmate-board.html"
STEP_SECONDS=3

snap() {
  PYTHONPATH=src python3 -c "
import sys
from adaptive_ivr_agent.live_view import build_board, render_live_page
specs = [tuple(s.split(':')) for s in sys.argv[1].split(',')]
specs = [(pid, int(n)) for pid, n in specs]
state = build_board(specs, 'data/role-phrasebooks.json')
open('$OUT', 'w', encoding='utf-8').write(render_live_page(state, 'ui/call-board-template.html'))
print('snapshot:', sys.argv[1])
" "$1"
}

echo "Open $OUT in a browser."
i=1
while [ "$i" -le 3 ]; do snap "$P1:$i"; sleep "$STEP_SECONDS"; i=$((i + 1)); done
i=1
while [ "$i" -le 3 ]; do snap "$P1:3,$P2:$i"; sleep "$STEP_SECONDS"; i=$((i + 1)); done
echo "Board complete."
