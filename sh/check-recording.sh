#!/usr/bin/env bash
# Check if a recording has sound or is silent.
# No argument = the newest file in data/recordings.
# Exit code: 0 = has sound, 2 = silent.
set -euo pipefail

# Quieter than this (loudest point, in dB) counts as silent
SILENT_BELOW_DB=-60

RED=$'\033[1;31m'
GREEN=$'\033[1;32m'
RESET=$'\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/data/recordings"

FILE="${1:-$(ls -t "$REC_DIR"/*.wav 2>/dev/null | head -1 || true)}"
if [ -z "$FILE" ]; then
  echo "No recordings found in $REC_DIR"
  exit 1
fi

STATS="$(ffmpeg -hide_banner -nostats -i "$FILE" -af volumedetect -f null - 2>&1)"
MAX_DB="$(echo "$STATS" | sed -n 's/.*max_volume: \(-*[0-9.]*\) dB.*/\1/p')"
MEAN_DB="$(echo "$STATS" | sed -n 's/.*mean_volume: \(-*[0-9.]*\) dB.*/\1/p')"

if [ -z "$MAX_DB" ]; then
  echo "${RED}Could not measure: $FILE${RESET}"
  exit 1
fi

if awk -v m="$MAX_DB" -v t="$SILENT_BELOW_DB" 'BEGIN { exit !(m < t) }'; then
  echo "${RED}SILENT: $FILE (loudest $MAX_DB dB, average $MEAN_DB dB)${RESET}"
  echo "${RED}The sound never reached BlackHole.${RESET}"
  exit 2
fi

echo "${GREEN}Has sound: $FILE (loudest $MAX_DB dB, average $MEAN_DB dB)${RESET}"
