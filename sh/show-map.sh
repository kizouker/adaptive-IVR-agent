#!/usr/bin/env bash
# Show the menu map with the position marker (*). Usage: show-map.sh [swedish|english] [position]
# Examples: show-map.sh swedish 2 / show-map.sh english 3. Part of T-005 (#7).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

MAP="${1:-swedish}"
AT="${2:-1}"

PYTHONPATH=src python3 -c "
import sys
from adaptive_ivr_agent.menu_map import MenuMap
name, at = sys.argv[1], int(sys.argv[2])
shown = MenuMap.english_branch() if name == 'english' else MenuMap.af_agda()
ids = [s.id for s in shown.states]
if at < 1 or at > len(ids):
    raise SystemExit(f'position must be 1-{len(ids)}')
shown.move_to(ids[at - 1])
print(f'--- {name} map at position {at} ({shown.current}) ---')
print(shown.render_ascii())
" "$MAP" "$AT"
