#!/usr/bin/env bash
# Demo: loop-free route to the queue on both maps (T-010).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

PYTHONPATH=src python3 -c "
from adaptive_ivr_agent.menu_map import MenuMap
from adaptive_ivr_agent.route import find_route

for name, shown, target in [('swedish', MenuMap.af_roksolana(), 'queue'),
                            ('english', MenuMap.english_branch(), 'officer')]:
    print(f'{name}:', ' -> '.join(find_route(shown, target)))
"
