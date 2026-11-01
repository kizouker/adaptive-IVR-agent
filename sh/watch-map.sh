#!/usr/bin/env bash
# Live graphical call map: walks the chain and re-renders /tmp/karta-live.svg.
# Open /tmp/karta-live.html in a browser; it reloads every 2 s and the red
# box moves left to right as the call progresses. Usage: watch-map.sh [swedish|english]
# Part of T-005 (#7). Run from anywhere.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$SCRIPT_DIR/../src"
MAP="${1:-swedish}"
STEP_SECONDS=4
SVG="/tmp/karta-live.svg"
HTML="/tmp/karta-live.html"

cat > "$HTML" <<EOF
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta http-equiv="refresh" content="2">
<title>AF Agda live map</title></head>
<body><img src="karta-live.svg" alt="live call map"></body></html>
EOF
echo "Open $HTML in a browser."

COUNT=$(PYTHONPATH="$SRC" python3 -c "
import sys
from adaptive_ivr_agent.menu_map import MenuMap
name = sys.argv[1]
shown = MenuMap.english_branch() if name == 'english' else MenuMap.af_agda()
print(len(shown.states))
" "$MAP")

i=1
while [ "$i" -le "$COUNT" ]; do
  PYTHONPATH="$SRC" python3 -c "
import sys
from adaptive_ivr_agent.menu_map import MenuMap
name, at, svg = sys.argv[1], int(sys.argv[2]), sys.argv[3]
shown = MenuMap.english_branch() if name == 'english' else MenuMap.af_agda()
ids = [s.id for s in shown.states]
shown.move_to(ids[at - 1])
shown.render_image(svg)
print(f'position {at}/{len(ids)}: {shown.current}')
" "$MAP" "$i" "$SVG"
  sleep "$STEP_SECONDS"
  i=$((i + 1))
done
echo "Call ended."
