#!/usr/bin/env bash
# Speaking demo call: one persona phones AF Roksolana ALOUD, tries 3 keywords.
# Caller words use voice Oskar, robot replies use voice Alva. Mac only.
# Prints every turn, like show-call.sh. Part of T-046 (#48).
# Usage: demo-call.sh [persona-id] (default ny-arbetslos).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

PERSONA="${1:-ny-arbetslos}"

PYTHONPATH=src python3 -c "
import json
import sys

from adaptive_ivr_agent.reactive import ReactiveRobot
from adaptive_ivr_agent.robot import CALLER_VOICE, SAY_VOICE, mac_say

persona_id = sys.argv[1]
roles = json.load(open('data/role-phrasebooks.json', encoding='utf-8'))['roles']
persona = next(r for r in roles if r['id'] == persona_id)
robot = ReactiveRobot.from_phrasebooks('data/role-phrasebooks.json')

print(f\"Caller: {persona['label']} -- errand: {persona['errand']}\")
for word in persona['vocabulary'][:3]:
    print(f'  caller says: {word}')
    mac_say(word, voice=CALLER_VOICE)
    reply, matched = robot.respond(word)
    mark = 'OK' if matched else '--'
    print(f'  robot [{mark}]: {reply}')
    mac_say(reply, voice=SAY_VOICE)
print('Call done.')
" "$PERSONA"
