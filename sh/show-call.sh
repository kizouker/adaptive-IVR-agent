#!/usr/bin/env bash
# Demo call: one persona phones AF Roksolana, tries 3 keywords, robot answers.
# Prints every turn, the used keywords with why (errand), and the map.
# Usage: show-call.sh [persona-id] (default ny-arbetslos). Part of T-044 (#46).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

PERSONA="${1:-ny-arbetslos}"

PYTHONPATH=src python3 -c "
import json
from adaptive_ivr_agent.menu_map import MenuMap
from adaptive_ivr_agent.reactive import ReactiveRobot

persona_id = '$PERSONA'
roles = json.load(open('data/role-phrasebooks.json', encoding='utf-8'))['roles']
persona = next(r for r in roles if r['id'] == persona_id)
robot = ReactiveRobot.from_phrasebooks('data/role-phrasebooks.json')
shown = MenuMap.af_roksolana()
walk = ['open_question', 'example_words', 'yes_no']

print(f\"Caller: {persona['label']} -- errand: {persona['errand']}\")
used = []
for word, state in zip(persona['vocabulary'][:3], walk):
    shown.move_to(state)
    reply, matched = robot.respond(word)
    mark = 'OK' if matched else '--'
    used.append((word, matched is not None))
    print(f'  caller says: {word}')
    print(f'  robot [{mark}]: {reply}')
print('Keywords used and why:')
for word, ok in used:
    print(f'  {word} ->', 'routed to errand' if ok else 'not understood')
print(f'--- map at position {shown.position()} ---')
print(shown.render_ascii())
shown.render_image('/tmp/karta-samtal.svg')
print('Snapshot: /tmp/karta-samtal.svg')
"
