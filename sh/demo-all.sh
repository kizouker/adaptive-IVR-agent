#!/usr/bin/env bash
# Full demo in one command: speaking call, keywords, queue, explorer,
# routing, plus graphic snapshots. Part of T-044 (#46).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

OUT="/tmp/holdmate-demo"
mkdir -p "$OUT"

say_step() { echo; echo "===== $1 ====="; }

say_step "1/6 speaking persona call (Oskar + Alva)"
sh sh/demo-call.sh ny-arbetslos

say_step "2/6 keywords used and why"
sh sh/show-call.sh sjukskriven

say_step "3/6 queue numbers + countdown"
sh sh/find-queue.sh

say_step "4/6 explorer grows the map"
sh sh/explore-demo.sh smabarnsforalder

say_step "5/6 routes without loops"
sh sh/route-demo.sh

say_step "6/6 graphic snapshots"
PYTHONPATH=src python3 -c "
from adaptive_ivr_agent.menu_map import MenuMap
sv = MenuMap.af_agda()
for s in ['example_words', 'yes_no', 'transfer']:
    sv.move_to(s)
sv.render_image('/tmp/holdmate-demo/swedish.svg')
en = MenuMap.english_branch()
en.move_to('officer')
en.render_image('/tmp/holdmate-demo/english.svg')
print('snapshots written')
"

echo
echo "Open the graphics:"
echo "  $OUT/swedish.svg"
echo "  $OUT/english.svg"
echo "Or the web board: https://kizouker.github.io/adaptive-IVR-agent/"
echo "Done."
