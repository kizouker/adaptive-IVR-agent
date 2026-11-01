#!/usr/bin/env bash
# Demo: explorer tries a persona's words, map grows per call (T-009).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

PERSONA="${1:-programdeltagare}"

PYTHONPATH=src python3 -c "
import json
from adaptive_ivr_agent.explorer import Explorer
from adaptive_ivr_agent.reactive import ReactiveRobot

roles = json.load(open('data/role-phrasebooks.json', encoding='utf-8'))['roles']
persona = next(r for r in roles if r['id'] == '$PERSONA')
explorer = Explorer(persona['vocabulary'], ReactiveRobot.from_phrasebooks('data/role-phrasebooks.json'))
n = 1
while True:
    found = explorer.run(f'run-{n}')
    if found is None:
        break
    mark = 'OK' if found['matched'] else '--'
    print(f\"run-{n}: {found['word']} [{mark}] edges={len(explorer.shown.edges)}\")
    n += 1
print('final map:')
print(explorer.shown.render_ascii())
"
