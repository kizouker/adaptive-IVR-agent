#!/usr/bin/env bash
# Demo: find queue numbers in five sample lines (T-011).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

PYTHONPATH=src python3 -c "
from adaptive_ivr_agent.queue import QueueWatch, find_place

LINES = [
    'Det är 38 samtal före dig',
    'anropare nummer 12',
    'Din plats är: 47',
    'Du har plats 1 i kön',
    'You are number 8 in the queue',
]
for line in LINES:
    print(f'{line}  ->  {find_place(line)}')

print('countdown:')
watch = QueueWatch()
for line in ['Du har plats 13 i kön', 'Tack för att du väntar', 'Du har plats 12 i kön']:
    print(f'  {line}  ->  place={watch.update(line)}')
"
