#!/usr/bin/env bash
# Classify our four lines on the ch.2 axes from transcript evidence (T-048).
# Usage: classify-calls.sh. Evidence is hand-distilled from the call logs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

PYTHONPATH=src python3 -c "
from adaptive_ivr_agent.classify import CallEvidence, classify

LINES = {
    'AF Roksolana (call 4)': CallEvidence(
        states_visited=['welcome', 'open', 'examples1', 'examples2', 'yes_no',
                        'key_menu', 'submenu', 'sms', 'identify', 'queue'],
        surprises=['no_match x2', 'yes/no failed 4 times', 'words change between calls'],
        same_input_different_result=True,
        silence_reprompted=True,
        known_branches_unexplored=True,
    ),
    'Swedbank (28 Oct)': CallEvidence(
        states_visited=['menu', 'self_service'],
        known_branches_unexplored=True,
    ),
    'FK (28 Oct)': CallEvidence(
        states_visited=['queue'],
        known_branches_unexplored=True,
    ),
    'Region Skane (30 Oct)': CallEvidence(
        states_visited=['language', 'menu', 'identify', 'queue', 'callback', 'human'],
        human_entered=True,
        known_branches_unexplored=True,
    ),
}

for name, evidence in LINES.items():
    print(f'=== {name} ===')
    for verdict in classify(evidence):
        print(f'  {verdict.axis:13} {verdict.value:28} ({verdict.reason})')
"
