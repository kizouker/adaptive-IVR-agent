#!/usr/bin/env bash
# Demo: fire the Mac queue alert for a place (default 2). T-012.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

PLACE="${1:-2}"

PYTHONPATH=src python3 -c "
import sys
from adaptive_ivr_agent.alerter import QueueAlert, mac_notify

place = int(sys.argv[1])
fired = QueueAlert(notify=mac_notify).check(place)
print('alert fired' if fired else 'no alert')
" "$PLACE"
