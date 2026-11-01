#!/usr/bin/env bash
# Record the robot voice from BlackHole.
# First checks the whole sound chain and shows a checklist.
# Switches the Mac's audio output and microphone back when the script ends.
#
# Usage:
#   ./sh/record-call.sh             checks, then records (you start the call yourself)
#   ./sh/record-call.sh --call      checks, places the call from the Mac, then records
#   ./sh/record-call.sh --check     only runs the checks (steps 1-4), then stops
#   ./sh/record-call.sh --airpods   listen in AirPods instead of the MacBook speakers
#   (options can be combined, for example --airpods --call)
set -euo pipefail

OUTPUT_SPEAKERS="IVR_Agent_Speakers"   # MacBook speakers + BlackHole (default)
OUTPUT_AIRPODS="IVR_Agent_Output"      # AirPods + BlackHole (with --airpods)
NORMAL_OUTPUT="Högtalare i MacBook Pro" # switch back to this if the script started on an IVR_Agent device
BLACKHOLE="BlackHole 16ch"          # ffmpeg records from this (both outputs above send sound into it)
MIC="MacBook Pro-mikrofon"
# CALL_NUMBER comes from .env in the repo root (not in git, see .env.example)
ENV_FILE="$(cd "$(dirname "$0")/.." && pwd)/.env"
if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi
CALL_NUMBER="${CALL_NUMBER:-}"
TEST_SOUND="/System/Library/Sounds/Ping.aiff"
SILENT_BELOW_DB=-60

YELLOW=$'\033[1;33m'
GREEN=$'\033[1;32m'
RED=$'\033[1;31m'
BLUE=$'\033[1;34m'
RESET=$'\033[0m'

ok()   { echo "  ${GREEN}✓${RESET} $1"; }
warn() { echo "  ${YELLOW}!${RESET} $1"; }
fail() { echo "  ${RED}✗ $1${RESET}"; exit 1; }
step() { echo; echo "${BLUE}$1${RESET}"; }
info() { echo "  • $1"; }

# Loudest point of a sound file, in dB
max_db() {
  ffmpeg -hide_banner -nostats -i "$1" -af volumedetect -f null - 2>&1 \
    | sed -n 's/.*max_volume: \(-*[0-9.]*\) dB.*/\1/p'
}

PLACE_CALL=false
CHECK_ONLY=false
MULTI_OUTPUT="$OUTPUT_SPEAKERS"
for arg in "$@"; do
  case "$arg" in
    --call)    PLACE_CALL=true ;;
    --check)   CHECK_ONLY=true ;;
    --airpods) MULTI_OUTPUT="$OUTPUT_AIRPODS" ;;
    *) echo "Unknown option: $arg (use --call, --check or --airpods)"; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$SCRIPT_DIR/../data/recordings"
REC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/data/recordings"
OUT_FILE="$REC_DIR/robot-$(date +%Y%m%d-%H%M%S).wav"
TEST_FILE="${TMPDIR:-/tmp}/blackhole-test-$$.wav"

# ---------- 1. Tools ----------
step "1. Tools"
for tool in ffmpeg SwitchAudioSource afplay; do
  if command -v "$tool" >/dev/null; then ok "$tool is installed"; else fail "$tool is missing"; fi
done

# ---------- 2. Devices ----------
step "2. Audio devices"
if SwitchAudioSource -a -t output | grep -Fxq "$MULTI_OUTPUT"; then
  ok "Output device '$MULTI_OUTPUT' exists"
else
  fail "Output device '$MULTI_OUTPUT' not found (create it in Audio MIDI Setup)"
fi
info "Output right now: '$(SwitchAudioSource -c -t output)' (step 3 switches it, you don't need to)"
# ffmpeg always exits with an error code when it only lists devices,
# so save the list first and search it afterwards
FFMPEG_DEVICES="$(ffmpeg -hide_banner -f avfoundation -list_devices true -i "" 2>&1 || true)"
if echo "$FFMPEG_DEVICES" | grep -Fq "$BLACKHOLE"; then
  ok "ffmpeg can record from '$BLACKHOLE'"
else
  fail "ffmpeg can't find '$BLACKHOLE'"
fi
if SwitchAudioSource -a -t input | grep -Fxq "$MIC"; then
  ok "Microphone '$MIC' exists"
else
  fail "Microphone '$MIC' not found"
fi

# ---------- 3. Switch output and microphone ----------
step "3. Switch sound"
ORIGINAL_OUTPUT="$(SwitchAudioSource -c -t output)"
# If we start on one of our own IVR_Agent devices, switch back to normal speakers afterwards
case "$ORIGINAL_OUTPUT" in
  IVR_Agent_*) ORIGINAL_OUTPUT="$NORMAL_OUTPUT" ;;
esac
ORIGINAL_INPUT="$(SwitchAudioSource -c -t input)"

switch_back() {
  rm -f "$TEST_FILE"
  SwitchAudioSource -s "$ORIGINAL_OUTPUT" -t output >/dev/null
  SwitchAudioSource -s "$ORIGINAL_INPUT" -t input >/dev/null
  echo
  echo "${GREEN}Sound switched back: output '$ORIGINAL_OUTPUT', microphone '$ORIGINAL_INPUT'${RESET}"
  if [ -s "$OUT_FILE" ]; then
    echo "${GREEN}Saved: $OUT_FILE${RESET}"
    "$SCRIPT_DIR/check-recording.sh" "$OUT_FILE" || true
  fi
}
trap switch_back EXIT
trap 'exit 130' INT TERM

SwitchAudioSource -s "$MULTI_OUTPUT" -t output >/dev/null
if [ "$(SwitchAudioSource -c -t output)" = "$MULTI_OUTPUT" ]; then
  ok "Output is now '$MULTI_OUTPUT' (switches back to '$ORIGINAL_OUTPUT' when done)"
else
  fail "Could not switch output to '$MULTI_OUTPUT'"
fi

SwitchAudioSource -s "$MIC" -t input >/dev/null
if [ "$(SwitchAudioSource -c -t input)" = "$MIC" ]; then
  ok "Microphone is now '$MIC' (switches back to '$ORIGINAL_INPUT' when done)"
else
  fail "Could not switch microphone to '$MIC'"
fi

# ---------- 4. Sound test: does a ping reach BlackHole? ----------
step "4. Sound test (you will hear a ping)"
ffmpeg -hide_banner -loglevel error -f avfoundation -i ":$BLACKHOLE" -t 3 -ac 1 -ar 16000 -y "$TEST_FILE" &
FFMPEG_PID=$!
sleep 1
afplay "$TEST_SOUND"
wait "$FFMPEG_PID"
TEST_DB="$(max_db "$TEST_FILE")"
if [ -n "$TEST_DB" ] && awk -v m="$TEST_DB" -v t="$SILENT_BELOW_DB" 'BEGIN { exit !(m >= t) }'; then
  ok "The ping reached BlackHole (loudest $TEST_DB dB)"
else
  fail "The ping did NOT reach BlackHole (loudest ${TEST_DB:-unknown} dB). Check '$MULTI_OUTPUT' in Audio MIDI Setup."
fi

if $CHECK_ONLY; then
  echo
  echo "${GREEN}All checks passed. Ready to record a call.${RESET}"
  exit 0
fi

# ---------- 5. The call ----------
step "5. The call"
if $PLACE_CALL; then
  if [ -z "$CALL_NUMBER" ]; then
    echo "CALL_NUMBER is empty. Set it in .env (see .env.example)."
    exit 1
  fi
  open "tel:$CALL_NUMBER"
  ok "Call to $CALL_NUMBER sent to FaceTime"
  warn "Click 'Ring' in the box on the Mac if it asks"
else
  warn "Start the call from FaceTime on the Mac now (not on the iPhone)"
fi
warn "Take the call on the Mac, not on the iPhone, or the sound stays on the phone"

# ---------- 6. Record ----------
step "6. Recording"
echo "  To: $OUT_FILE"
echo
echo "${YELLOW}>>> Press q to stop the recording <<<${RESET}"
echo

ffmpeg -hide_banner -loglevel warning -stats -f avfoundation -i ":$BLACKHOLE" -ac 1 -ar 16000 "$OUT_FILE"
