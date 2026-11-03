#!/bin/bash
# Record one video shot with ffmpeg (#132). Screen only, no audio (dub after).
# Runs on: Rickard's Mac (M4). Modes: run | check (check lists screens).
# Run: ./sh/record-shot.sh 02 start   (saves data/video/shot-02-start.mov, q stops)
# Pick another screen: SCREEN_INDEX=2 ./sh/record-shot.sh 02 start
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"

ROOT="$(cd "$HERE/.." && pwd)"
SCREEN_INDEX="${SCREEN_INDEX:-1}"

title "Record shot ($MODE)"

step "Preflight"
what "ffmpeg must exist and the video folder must be there."
command -v ffmpeg >/dev/null 2>&1 || fail "ffmpeg is missing (brew install ffmpeg)"
[ -d "$ROOT/data/video" ] || fail "data/video is missing"
ok "ffmpeg ok"

if [ "$MODE" = "check" ]; then
  step "Screens"
  what "List capturable screens so you can pick SCREEN_INDEX."
  ffmpeg -f avfoundation -list_devices true -i "" 2>&1 | grep -A6 "AVFoundation video" || fail "no screens listed"
  ok "screens listed above (default index is 1)"
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
ok "recording to $OUT (q stops)"
ffmpeg -f avfoundation -framerate 30 -i "$SCREEN_INDEX:none" -c:v libx264 -pix_fmt yuv420p "$OUT"
