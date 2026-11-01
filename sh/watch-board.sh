#!/usr/bin/env bash
# Feed the React board: two personas phone in turn by turn, writes JSON.
# Start the dev server first (cd ui/board && npm run dev), then run this.
# Board polls ui/board/public/board-state.json every 3 s. Part of T-045 (#47).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

P1="${1:-ny-arbetslos}"
P2="${2:-sjukskriven}"
OUT="ui/board/public/board-state.json"
STEP_SECONDS=3

snap() {
  PYTHONPATH=src python3 -c "
import sys
from adaptive_ivr_agent.live_view import build_board
specs = [(s.split(':')[0], int(s.split(':')[1])) for s in sys.argv[1].split(',')]
state = build_board(specs, 'data/role-phrasebooks.json')
import json
open(sys.argv[2], 'w', encoding='utf-8').write(json.dumps(state, ensure_ascii=False))
print('snapshot:', sys.argv[1])
" "$1" "$OUT"
}

i=1
while [ "$i" -le 3 ]; do snap "$P1:$i"; sleep "$STEP_SECONDS"; i=$((i + 1)); done
i=1
while [ "$i" -le 3 ]; do snap "$P1:3,$P2:$i"; sleep "$STEP_SECONDS"; i=$((i + 1)); done
echo "Feed complete."
