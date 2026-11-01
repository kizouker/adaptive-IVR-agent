#!/usr/bin/env bash
# Robot speaks the first 3 documented AF Agda lines (Alva). Live audio, Mac only.
# Part of T-042 (#44). Run from anywhere: sh /path/to/sh/demo-robot.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

PYTHONPATH=src python3 -c "from adaptive_ivr_agent.robot import PracticeRobot, load_lines, mac_say; lines = load_lines('data/doorkeeper-lines.json'); PracticeRobot(lines[:3], speak=mac_say).run('/tmp/robot-says.json')"
echo "Robot done."
