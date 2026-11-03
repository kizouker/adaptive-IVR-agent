#!/bin/bash
# Record one video shot with ffmpeg (#132). Screen only, no audio (dub after).
# Runs on: Rickard's Mac (M4). Modes: run | check (check lists screens).
# Run: ./sh/record-shot.sh 02 start   (saves data/video/shot-02-start.mov, q stops)
# Pick another source: SCREEN="FaceTime HD Camera" ./sh/record-shot.sh 02 cam
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"

ROOT="$(cd "$HERE/.." && pwd)"
SCREEN="${SCREEN:-Capture screen 0}"

title "Record shot ($MODE)"

step "Preflight"
what "ffmpeg must exist and the video folder must be there."
command -v ffmpeg >/dev/null 2>&1 || fail "ffmpeg is missing (brew install ffmpeg)"
[ -d "$ROOT/data/video" ] || fail "data/video is missing"
ok "ffmpeg ok"

if [ "$MODE" = "check" ]; then
  step "Screens"
  what "List capturable devices so you can pick SCREEN."
  ffmpeg -f avfoundation -list_devices true -i "" 2>&1 | grep -E "AVFoundation (video|audio) devices|^\[.*\] [A-Z]" || fail "no devices listed"
  ok "devices listed above (default SCREEN is Capture screen 0)"
  exit 0
fi

NUM="$MODE"
NAME="${2:-shot}"
[ "$NUM" -ge 0 ] 2>/dev/null || fail "first arg must be the shot number (example: ./sh/record-shot.sh 02 start)"
OUT="$ROOT/data/video/shot-$(printf '%02d' "$NUM")-$NAME.mov"

step "Record"
what "Capture the screen to $OUT. Press q in this window to stop."
if [ -f "$OUT" ] && [ "${OVERWRITE:-0}" != "1" ]; then
  fail "$OUT exists already (retake with OVERWRITE=1 or pick another number)"
fi
ok "recording $SCREEN to $OUT (q stops)"
ffmpeg -f avfoundation -framerate 30 -i "$SCREEN:none" -c:v libx264 -pix_fmt yuv420p "$OUT"
