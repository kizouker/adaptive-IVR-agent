#!/usr/bin/env bash
# Play a recording. No argument = the newest file in data/recordings.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/data/recordings"

FILE="${1:-$(ls -t "$REC_DIR"/*.wav 2>/dev/null | head -1 || true)}"
if [ -z "$FILE" ]; then
  echo "No recordings found in $REC_DIR"
  exit 1
fi

echo "Playing $FILE (Ctrl+C to stop)"
afplay "$FILE"
