#!/bin/bash
# Talk to the practice robot with your own voice (push-to-talk loop).
# Runs on: Rickard's Mac (M4). Modes: talk (default) | check.
# Flags: --airpods (physical AirPods; must be connected), --as <persona> (role-play + tag rounds for Holdmate training),
#   --queue N (simulate a queue of N, 1-99; default is a random short one),
#   --quiet (type + read instead of speak + listen).
# Env: AGDA_FORGIVING=1 enables Agda's bad memory (learned aliases, unrealistic).
#   QUEUE_TICK seconds between queue numbers (default 8).
# Keys during record/playback: any key skips ahead, 0 jumps to the English
# menu (full call-5 path on DTMF digits), a toggles speakers/AirPods output,
# t toggles quiet mode (hushes in-flight audio at once), + / - adjusts volume
# (0.1-4.0, 1 = normal; the board slider writes the same .talk-volume file).
# Each round records ~5s from the MacBook mic, transcribes with whisper.cpp,
# and the robot answers aloud (Alva). Output goes through the IVR_Agent device
# (speakers + BlackHole) and everything is switched back on exit.
# Transfer asks for identification (faked test number, human in the loop),
# then the call lands in the simulated queue. Ctrl+C ends the loop.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
ROOT="$(cd "$HERE/.." && pwd)"

MODE="talk"
AIRPODS=0
PERSONA=""
QUIET=0
QUEUE_START=""
while [ $# -gt 0 ]; do
  case "$1" in
    check|--check) MODE="check" ;;
    --airpods) AIRPODS=1 ;;
    --quiet) QUIET=1 ;;
    --as)
      PERSONA="${2:-}"
      [ -n "$PERSONA" ] || fail "--as needs a persona id (see data/role-phrasebooks.json)"
      shift
      ;;
    --queue)
      QUEUE_START="${2:-}"
      case "$QUEUE_START" in
        '' | *[!0-9]*) fail "--queue needs a number 1-99" ;;
      esac
      if [ "$QUEUE_START" -lt 1 ] || [ "$QUEUE_START" -gt 99 ]; then
        fail "--queue needs a number 1-99"
      fi
      shift
      ;;
    *) fail "Unknown argument: $1 (use: check, --airpods, --as <persona>, --queue N, --quiet)" ;;
  esac
  shift
done

OUTPUT_SPEAKERS="IVR_Agent_Speakers"   # MacBook speakers + BlackHole (default)
NORMAL_OUTPUT="Högtalare i MacBook Pro" # physical fallback (also the AirPods-off target)
MIC="MacBook Pro-mikrofon"
RECORD_SECONDS="${RECORD_SECONDS:-5}"
MIC_INDEX="${MIC_INDEX:-}"             # empty = auto-detect; set to force an avfoundation index
VOICE="${VOICE:-Alva}"
FLOOR_LEVEL=70                        # talk mode raises a quieter physical output to this (merged devices can't be raised later)
FLOOR_CHANGED=0
FLOOR_TARGET=""
ORIG_SYS_VOL=""
ORIG_SYS_MUTED=""
if [ -z "${TALK_VOLUME+x}" ]; then
  TALK_VOLUME="0.7"                       # Rickard's level; +/- during a call adjusts + remembers
  if [ -f "$ROOT/.talk-volume" ] && grep -Eq '^(0\.[0-9]+|[1-3](\.[0-9]+)?|4(\.0+)?)$' "$ROOT/.talk-volume"; then
    TALK_VOLUME="$(cat "$ROOT/.talk-volume")"
  fi
fi
AGDA_FORGIVING="${AGDA_FORGIVING:-0}"     # 1 = Agda's bad memory (learned aliases); 0 = exact AF words
QUEUE_TICK="${QUEUE_TICK:-8}"             # seconds between queue numbers (any key hurries)
FAKE_PERSONNUMMER="19121212-1212"         # test number for the faked ID step; nothing real ever flows
MODEL="$HOME/models/whisper/ggml-small.bin"
REC_DIR="$ROOT/data/recordings"
PHRASEBOOKS="$ROOT/data/role-phrasebooks.json"
MISS_FILE="$ROOT/data/talk-misses.jsonl"
LEARNED_FILE="$ROOT/data/learned-words.json"
ROUNDS_FILE="$ROOT/data/talk-rounds.jsonl"

find_airpods() {
  # Print the physical AirPods output device name, or empty if none connected.
  SwitchAudioSource -a -t output 2>/dev/null | grep -i -m1 'airpods' || true
}

MULTI_OUTPUT="$OUTPUT_SPEAKERS"
if [ "$AIRPODS" = 1 ]; then
  MULTI_OUTPUT="$(find_airpods)"
  [ -n "$MULTI_OUTPUT" ] || fail "No AirPods found among output devices (connect them first, then retry)"
fi

audio_index_for() {
  # Print the avfoundation audio index for a device name (exact match first,
  # then a MacBook/mic guess, then the first audio device). Empty = not found.
  _want="$1"
  _list="$(ffmpeg -hide_banner -f avfoundation -list_devices true -i "" 2>&1 \
    | sed -n '/audio devices:/,$ p' | grep -o '\[[0-9][0-9]*\] .*')"
  _line="$(printf '%s\n' "$_list" | grep -F " $_want" | head -1)"
  [ -z "$_line" ] && _line="$(printf '%s\n' "$_list" | grep -i -m1 'macbook\|mikrofon\|microphone')"
  [ -z "$_line" ] && _line="$(printf '%s\n' "$_list" | head -1)"
  printf '%s\n' "$_line" | sed -n 's/^\[\([0-9][0-9]*\)\].*/\1/p'
}

floor_system_volume() {
  # $1 = physical device already current. Unmute + raise below FLOOR_LEVEL.
  # Remembers originals for restore_system_volume. Never fails the call.
  FLOOR_TARGET="$1"
  FLOOR_CHANGED=0
  ORIG_SYS_VOL=""
  ORIG_SYS_MUTED=""
  command -v osascript >/dev/null 2>&1 || { warn "osascript missing, skipping volume floor"; return 0; }
  _vol="$(osascript -e 'output volume of (get volume settings)' 2>/dev/null || true)"
  _muted="$(osascript -e 'output muted of (get volume settings)' 2>/dev/null || true)"
  case "$_vol" in
    '' | *[!0-9]*) warn "could not read system volume, skipping floor"; return 0 ;;
  esac
  ORIG_SYS_VOL="$_vol"
  ORIG_SYS_MUTED="$_muted"
  if [ "$_muted" = "true" ]; then
    osascript -e 'set volume output muted false' 2>/dev/null || true
    FLOOR_CHANGED=1
    info "unmuted $1 (was muted)"
  fi
  if [ "$_vol" -lt "$FLOOR_LEVEL" ]; then
    osascript -e "set volume output volume $FLOOR_LEVEL" 2>/dev/null || true
    FLOOR_CHANGED=1
    info "raised $1 system volume $_vol -> $FLOOR_LEVEL (merged device can't be raised later)"
  else
    ok "system volume $1: $_vol (floor $FLOOR_LEVEL)"
  fi
}

restore_system_volume() {
  # Undo floor_system_volume: exact level/mute back on FLOOR_TARGET, then back
  # to ORIGINAL_OUTPUT. Silent no-op unless the floor changed something.
  [ "${FLOOR_CHANGED:-0}" = 1 ] || return 0
  [ -n "${FLOOR_TARGET:-}" ] || return 0
  command -v osascript >/dev/null 2>&1 || return 0
  case "${ORIG_SYS_VOL:-}" in
    '' | *[!0-9]*) return 0 ;;
  esac
  if [ "$(SwitchAudioSource -c -t output 2>/dev/null)" != "$FLOOR_TARGET" ]; then
    SwitchAudioSource -s "$FLOOR_TARGET" -t output >/dev/null 2>/dev/null || return 0
  fi
  osascript -e "set volume output volume $ORIG_SYS_VOL" 2>/dev/null || true
  if [ "${ORIG_SYS_MUTED:-}" = "true" ]; then
    osascript -e 'set volume output muted true' 2>/dev/null || true
  fi
  if [ "$(SwitchAudioSource -c -t output 2>/dev/null)" != "$ORIGINAL_OUTPUT" ]; then
    SwitchAudioSource -s "$ORIGINAL_OUTPUT" -t output >/dev/null 2>/dev/null || true
  fi
  info "system volume restored: $FLOOR_TARGET -> $ORIG_SYS_VOL"
}

title "Talk to the robot ($MODE)"

step "Preflight"
what "Check tools, model, phrasebooks and audio devices before touching anything."
for tool in ffmpeg ffprobe whisper-cli say afplay SwitchAudioSource python3; do
  command -v "$tool" >/dev/null 2>&1 || fail "$tool is missing (brew install $tool)"
done
ok "tools: ffmpeg, ffprobe, whisper-cli, say, afplay, SwitchAudioSource, python3"
[ -f "$MODEL" ] || fail "Whisper model not found: $MODEL (see docs/recording-setup.md, step 7)"
ok "Whisper model: $MODEL"
[ -f "$PHRASEBOOKS" ] || fail "Phrasebooks not found: $PHRASEBOOKS"
ok "phrasebooks: $PHRASEBOOKS"
SwitchAudioSource -a -t output | grep -Fxq "$MULTI_OUTPUT" \
  || fail "Output device '$MULTI_OUTPUT' not found (open Audio MIDI Setup and check the Multi-Output device)"
ok "output device: $MULTI_OUTPUT"
if [ "$MULTI_OUTPUT" = "$OUTPUT_SPEAKERS" ]; then
  ALT_CHECK="$(find_airpods)"
  if [ -n "$ALT_CHECK" ]; then
    ok "toggle target: $ALT_CHECK (press a during the call)"
  else
    warn "no AirPods connected (mid-call a-key stays put)"
  fi
elif SwitchAudioSource -a -t output | grep -Fxq "$OUTPUT_SPEAKERS"; then
  ok "toggle target: $OUTPUT_SPEAKERS (press a during the call)"
else
  warn "toggle target '$OUTPUT_SPEAKERS' not found (mid-call a-key stays put)"
fi
if command -v osascript >/dev/null 2>&1; then
  SYS_VOL="$(osascript -e "get volume settings" 2>/dev/null || true)"
  case "$SYS_VOL" in
    *"output muted:true"*) warn "macOS output is MUTED (unmute to hear Agda)" ;;
  esac
  SYS_LEVEL="$(printf '%s' "$SYS_VOL" | sed -n 's/.*output volume:\([0-9][0-9]*\).*/\1/p')"
  case "$SYS_LEVEL" in
    '' | *[!0-9]*) ;;
    *) if [ "$SYS_LEVEL" -lt 40 ]; then warn "macOS system volume is $SYS_LEVEL (raise it to hear Agda well)"; fi ;;
  esac
fi
if [ "$MODE" = "check" ] && command -v osascript >/dev/null 2>&1; then
  info "check: talk mode would unmute + raise below $FLOOR_LEVEL to $FLOOR_LEVEL (now: ${SYS_LEVEL:-unknown})"
fi
if [ "$QUIET" = 1 ]; then
  info "quiet mode: type + read, t toggles sound back on"
fi
SwitchAudioSource -a -t input | grep -Fxq "$MIC" \
  || fail "Mic '$MIC' not found (check System Settings -> Sound -> Input)"
ok "mic: $MIC"
if [ -z "$MIC_INDEX" ]; then
  MIC_INDEX="$(audio_index_for "$MIC")"
  [ -n "$MIC_INDEX" ] || fail "Could not find '$MIC' in the ffmpeg device list (first run may need mic permission: allow Terminal, then re-run)"
fi
ok "ffmpeg mic index: $MIC_INDEX"
mkdir -p "$REC_DIR"
info "Recordings go to: $REC_DIR"
info "Agda plays at volume $TALK_VOLUME (1 = normal, up to 4 = boost; + / - during the call or the board slider)"
info "Misses are logged to $MISS_FILE (teach them with sh/learn-words.sh)"
info "Every round is logged to $ROUNDS_FILE (Holdmate's training data)"
if [ "$AGDA_FORGIVING" = "1" ]; then
  warn "bad memory ON: Agda accepts learned aliases (unrealistic practice)"
else
  info "bad memory off: Agda only knows exact AF words (realistic)"
fi
case "$QUEUE_TICK" in
  '' | *[!0-9]*) fail "QUEUE_TICK must be whole seconds" ;;
esac
if [ -n "$QUEUE_START" ]; then
  info "queue starts at $QUEUE_START, ticks every ${QUEUE_TICK}s (any key hurries)"
else
  info "queue starts at random 2-5, ticks every ${QUEUE_TICK}s (any key hurries)"
fi

[ "$MODE" = "check" ] && { title "Check only: nothing changed"; exit 0; }

step "Switch audio"
what "Level the physical output first (merged devices can't be raised later), then route through $MULTI_OUTPUT. Originals are restored on exit."
ORIGINAL_OUTPUT="$(SwitchAudioSource -c -t output)"
case "$ORIGINAL_OUTPUT" in
  IVR_Agent_*) ORIGINAL_OUTPUT="$NORMAL_OUTPUT" ;;
esac
ORIGINAL_INPUT="$(SwitchAudioSource -c -t input)"
switch_back() {
  stty sane 2>/dev/null || true
  SwitchAudioSource -s "$ORIGINAL_OUTPUT" -t output >/dev/null
  SwitchAudioSource -s "$ORIGINAL_INPUT" -t input >/dev/null
  info "Audio restored: output='$ORIGINAL_OUTPUT' input='$ORIGINAL_INPUT'"
  restore_system_volume
}
trap switch_back EXIT
trap 'exit 130' INT TERM
_floor_target="$NORMAL_OUTPUT"
if [ "$AIRPODS" = 1 ]; then
  _pods="$(find_airpods)"
  [ -n "$_pods" ] && _floor_target="$_pods"
fi
if [ "$(SwitchAudioSource -c -t output)" != "$_floor_target" ]; then
  SwitchAudioSource -s "$_floor_target" -t output >/dev/null \
    || fail "Could not switch output to $_floor_target"
  ok "output -> $_floor_target (level check)"
fi
floor_system_volume "$_floor_target"
SwitchAudioSource -s "$MULTI_OUTPUT" -t output >/dev/null
[ "$(SwitchAudioSource -c -t output)" = "$MULTI_OUTPUT" ] \
  || fail "Could not switch output to $MULTI_OUTPUT"
ok "output -> $MULTI_OUTPUT"
SwitchAudioSource -s "$MIC" -t input >/dev/null
[ "$(SwitchAudioSource -c -t input)" = "$MIC" ] || fail "Could not switch input to $MIC"
ok "input -> $MIC"

if [ -n "$PERSONA" ]; then
  step "Role card"
  what "Show who you are calling as, so you can speak from that errand."
  run "read $PERSONA from role-phrasebooks.json"
  if ! PYTHONPATH="$ROOT/src" python3 - "$PERSONA" "$PHRASEBOOKS" <<'CARD'
import json
import sys
roles = json.load(open(sys.argv[2], encoding="utf-8"))["roles"]
persona = next((r for r in roles if r["id"] == sys.argv[1]), None)
if persona is None:
    sys.exit(1)
print(f"Role: {persona['label']}")
print(f"Errand: {persona['errand']}")
print(f"Try words like: {', '.join(persona['vocabulary'])}")
CARD
  then
    info "valid persona ids:"
    PYTHONPATH="$ROOT/src" python3 -c "import json; [print(' - ' + r['id']) for r in json.load(open('$PHRASEBOOKS'))['roles']]"
    fail "Unknown persona '$PERSONA'"
  fi
  ok "rounds will be tagged: $PERSONA"
fi

CALL_STAMP="$(date +%Y%m%d-%H%M%S)"
MISSES=0
TURNS_FILE="$REC_DIR/talk-$CALL_STAMP-turns.jsonl"
BOARD_FILE="$ROOT/ui/board/public/board-state.json"
AUDIO_DIR="$ROOT/ui/board/public/audio"
VOLUME_FILE="$ROOT/.talk-volume"

save_volume() {
  printf '%s' "$TALK_VOLUME" > "$VOLUME_FILE"
}

load_volume() {
  # Re-read the GUI-shared volume file (the board slider writes it live).
  if [ -f "$VOLUME_FILE" ] && grep -Eq '^(0\.[0-9]+|[1-3](\.[0-9]+)?|4(\.0+)?)$' "$VOLUME_FILE"; then
    TALK_VOLUME="$(cat "$VOLUME_FILE")"
  fi
}

volume_step() { # $1 = +0.2 | -0.2; clamps to 0.1..4.0 (1 = normal) and remembers
  TALK_VOLUME="$(LC_ALL=C awk -v v="$TALK_VOLUME" -v d="$1" 'BEGIN { n = v + d; if (n < 0.1) n = 0.1; if (n > 4) n = 4; printf "%.1f", n }')"
  save_volume
  info "volume $TALK_VOLUME"
}

quit_call() {
  title "Quitting — your audio setup is restored on exit."
  exit 0
}

toggle_output() {
  # Switch system output between speakers and physical AirPods; never fails.
  if [ "$MULTI_OUTPUT" = "$OUTPUT_SPEAKERS" ]; then
    ALT_TARGET="$(find_airpods)"
    if [ -z "$ALT_TARGET" ]; then
      warn "no AirPods connected, staying put"
      return 0
    fi
  else ALT_TARGET="$OUTPUT_SPEAKERS"; fi
  if ! SwitchAudioSource -a -t output | grep -Fxq "$ALT_TARGET"; then
    warn "device '$ALT_TARGET' not found, staying put"
    return 0
  fi
  SwitchAudioSource -s "$ALT_TARGET" -t output >/dev/null
  if [ "$(SwitchAudioSource -c -t output)" = "$ALT_TARGET" ]; then
    MULTI_OUTPUT="$ALT_TARGET"
    info "output -> $ALT_TARGET (press a to switch back)"
  else
    warn "could not switch to $ALT_TARGET"
  fi
}

toggle_quiet() {
  # $1 = pid to hush (or ""). Flips QUIET; 0 = skip ahead, 1 = keep waiting.
  if [ "$QUIET" = 1 ]; then QUIET=0; info "sound on"
  else QUIET=1; info "quiet: type + read from here"; fi
  if [ -n "${1:-}" ]; then kill "$1" 2>/dev/null; return 0; fi
  return 1
}

wait_keys() { # $1 seconds, $2 pid to watch (or ""); 0 = skip, 1 = time out, 2 = quit
  KEY_PRESSED=""
  if [ ! -t 0 ]; then
    return 1
  fi
  ETX="$(printf '\003')"
  EOT="$(printf '\004')"
  end=$((SECONDS + $1))
  while [ "$SECONDS" -lt "$end" ]; do
    if [ -n "$2" ]; then kill -0 "$2" 2>/dev/null || return 1; fi
    if read -t 1 -n 1 -s key; then
      KEY_PRESSED="$key"
      case "$key" in
        +) volume_step +0.2 ;;
        -) volume_step -0.2 ;;
        a|A) toggle_output ;;
        t|T) if toggle_quiet "$2"; then return 0; fi ;;
        q|Q|"$ETX"|"$EOT") return 2 ;;
        *) return 0 ;;
      esac
    fi
  done
  return 1
}

wait_digit() { # $1 seconds; 0 = digit in DIGIT, 1 = silence, 2 = quit
  DIGIT=""
  if [ ! -t 0 ]; then
    return 1
  fi
  ETX="$(printf '\003')"
  EOT="$(printf '\004')"
  end=$((SECONDS + $1))
  while [ "$SECONDS" -lt "$end" ]; do
    if read -t 1 -n 1 -s key; then
      case "$key" in
        +) volume_step +0.2 ;;
        -) volume_step -0.2 ;;
        a|A) toggle_output ;;
        t|T) toggle_quiet "" ;;
        q|Q|"$ETX"|"$EOT") return 2 ;;
        [0-9]) DIGIT="$key"; return 0 ;;
      esac
    fi
  done
  return 1
}

prepare_playback() {
  # From TALK_VOLUME + PLAY_SRC: set PLAY_FILE/PLAY_VOL/PLAY_FROM (boost incl).
  PLAY_FILE="$PLAY_SRC"
  PLAY_VOL="$TALK_VOLUME"
  PLAY_FROM="$TALK_VOLUME"
  if LC_ALL=C awk "BEGIN { exit !($TALK_VOLUME > 1) }" 2>/dev/null; then
    PLAY_FILE="$PLAY_SRC-boost.aiff"
    if ffmpeg -hide_banner -loglevel error -y -i "$PLAY_SRC" \
        -af "volume=$TALK_VOLUME,alimiter=limit=0.95" "$PLAY_FILE" 2>/dev/null; then
      PLAY_VOL="1"
      info "boost x$TALK_VOLUME (ffmpeg gain)"
    else
      warn "boost failed, playing at max instead"
      PLAY_FILE="$PLAY_SRC"; PLAY_VOL="1"
    fi
  fi
}

play_skippable() { # $1 = file; any key skips, + / - and slider act live
  DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1" 2>/dev/null)" || DUR="8"
  if [ "$QUIET" = 1 ]; then
    info "(quiet: muted — any key continues, t for sound, q quits)"
    wait_keys "$((${DUR%.*} + 2))" ""; RC=$?
    if [ "$RC" = 2 ]; then quit_call; fi
    return 0
  fi
  SECS=$((${DUR%.*} + 2))
  load_volume # pick up board-slider changes made since the last turn
  PLAY_SRC="$1"
  prepare_playback
  afplay -v "$PLAY_VOL" "$PLAY_FILE" & APID=$!
  HAVE_SWITCHER=0
  command -v SwitchAudioSource >/dev/null 2>&1 && HAVE_SWITCHER=1
  CUR_DEV=""
  if [ "$HAVE_SWITCHER" = 1 ]; then
    CUR_DEV="$(SwitchAudioSource -c -t output 2>/dev/null || true)"
  fi
  LEFT="$SECS"
  while [ "$LEFT" -gt 0 ]; do
    kill -0 "$APID" 2>/dev/null || break
    wait_keys 1 "$APID"; RC=$?
    if [ "$RC" = 2 ]; then
      kill "$APID" 2>/dev/null
      quit_call
    elif [ "$RC" = 0 ]; then
      kill "$APID" 2>/dev/null
      info "skipped ahead"
      break
    fi
    kill -0 "$APID" 2>/dev/null || break
    load_volume
    RESTART=""
    if [ "$TALK_VOLUME" != "$PLAY_FROM" ]; then RESTART="volume $TALK_VOLUME"; fi
    if [ "$HAVE_SWITCHER" = 1 ]; then
      NEW_DEV="$(SwitchAudioSource -c -t output 2>/dev/null || true)"
      if [ -n "$NEW_DEV" ] && [ "$NEW_DEV" != "$CUR_DEV" ]; then
        CUR_DEV="$NEW_DEV"
        RESTART="output $CUR_DEV"
      fi
    fi
    if [ -n "$RESTART" ]; then
      kill "$APID" 2>/dev/null
      info "$RESTART (replaying line)"
      prepare_playback
      afplay -v "$PLAY_VOL" "$PLAY_FILE" & APID=$!
    fi
    LEFT=$((LEFT - 1))
  done
  wait "$APID" 2>/dev/null || true
}

agda_says() {
  # $1 = opening|round|identified|queue|english|officer, $2 = transcript (round only),
  # $3 = aiff file, $4 = caller wav (round only), $5 = voice override (or "").
  # Speaks Agda's line, saves the audio, publishes the board state,
  # prints the exchange plus TALK_DONE / TALK_MISSES.
  TALK_ROOT="$ROOT" TALK_TXT="${2:-}" TALK_AIFF="$3" TALK_VOICE="${5:-$VOICE}" TALK_MISSES="$MISSES" \
    TALK_CALL="$CALL_STAMP" TALK_ROUND="${ROUND:-0}" \
    TALK_WAV="${4:-}" TALK_TURNS_FILE="$TURNS_FILE" TALK_BOARD_FILE="$BOARD_FILE" \
    TALK_AUDIO_DIR="$AUDIO_DIR" TALK_MISS_FILE="$MISS_FILE" TALK_LEARNED_FILE="$LEARNED_FILE" \
    TALK_ROUNDS_FILE="$ROUNDS_FILE" TALK_PERSONA="$PERSONA" TALK_FORGIVING="$AGDA_FORGIVING" \
    TALK_QUEUE_START="$QUEUE_START" TALK_PLACE="${PLACE:-}" TALK_TOTAL="${START:-}" \
    PYTHONPATH="$ROOT/src" python3 - "$1" <<'EOF'
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from adaptive_ivr_agent.live_view import (
    LIVE_MAP,
    LIVE_ROBOT_NAME,
    LiveCall,
    build_live_board,
    write_captions,
)
from adaptive_ivr_agent.reactive import ReactiveRobot
from adaptive_ivr_agent.robot import SAY_VOICE, load_indexed_lines
from adaptive_ivr_agent.talk import AgdaCall, with_aliases

root = os.environ["TALK_ROOT"]
voice = os.environ.get("TALK_VOICE", SAY_VOICE)
lines = load_indexed_lines(os.path.join(root, "data/doorkeeper-lines.json"))
ears = ReactiveRobot.from_phrasebooks(os.path.join(root, "data/role-phrasebooks.json"))
learned_path = os.environ["TALK_LEARNED_FILE"]
forgiving = os.environ.get("TALK_FORGIVING") == "1"
if forgiving and os.path.exists(learned_path):
    aliases = json.load(open(learned_path, encoding="utf-8"))
else:
    aliases = {}
forced_start = os.environ.get("TALK_QUEUE_START", "").strip()
forced = int(forced_start) if forced_start.isdigit() else None
# Rickard 1 Nov: Alva mangles the English sentence, so Agda skips it.
# L01 keeps the verbatim line (that IS what AF says); only speech drops it.
welcome = lines["L01"].split(" For English, press 0.")[0]
assert "press" not in welcome.lower(), f"English slipped into opening: {welcome}"
# L30: Rickard's pick 1 Nov (UNVERIFIED memory). Replace with verbatim
# from Monday's sampling.
SERVED_LINE = lines["L30"]
agda = AgdaCall(
    opening=f"{welcome} {lines['L02']}",
    examples=lines["L03"],
    yesno=lines["L22"],
    yesno_reprompt=lines["L41"],
    transfer=lines["L19"],
    identify_line=lines["L09"],
    identified_line=lines["L11"],
    served_line=SERVED_LINE,
    queue_line=lines["L13"],
    place_template=lines["L29"],
    respond=with_aliases(ears.respond, aliases),
    queue_place=(lambda: forced) if forced else None,
)


def log_miss(heard):
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "call": os.environ["TALK_CALL"],
        "round": int(os.environ["TALK_ROUND"]),
        "persona": os.environ.get("TALK_PERSONA", ""),
        "heard": heard.strip(),
    }
    with open(os.environ["TALK_MISS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_round(heard, matched):
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "call": os.environ["TALK_CALL"],
        "round": int(os.environ["TALK_ROUND"]),
        "persona": os.environ.get("TALK_PERSONA", ""),
        "heard": heard.strip(),
        "matched": matched,
    }
    with open(os.environ["TALK_ROUNDS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def render_reply(text):
    # Render only; the shell plays it so a keypress can skip ahead.
    subprocess.run(["say", "-v", voice, "-o", os.environ["TALK_AIFF"], text], check=True)


def state_after(done, misses, identify):
    if done:
        return "queue"
    if identify:
        return "transfer"
    if misses >= 2:
        return "yes_no"
    if misses == 1:
        return "example_words"
    return "open_question"


def load_call():
    call = LiveCall(
        map_name=os.environ.get("TALK_MAP", LIVE_MAP),
        robot_name=os.environ.get("TALK_ROBOT_NAME", LIVE_ROBOT_NAME),
    )
    path = os.environ["TALK_TURNS_FILE"]
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                turn = json.loads(line)
                call.add_turn(turn["caller"], turn["robot"], turn["matched"], turn["state"],
                              turn.get("caller_audio"), turn.get("robot_audio"),
                              turn.get("caller_captions"), turn.get("robot_captions"),
                              turn.get("queue_place"), turn.get("queue_total"))
    return call


def duration_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path],
                         check=True, capture_output=True, text=True)
    return float(out.stdout.strip())


def to_mp3(aiff, mp3):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", aiff,
                    "-codec:a", "libmp3lame", "-q:a", "4",
                    mp3], check=True)


def write_board(call):
    board = build_live_board([call])
    with open(os.environ["TALK_BOARD_FILE"], "w", encoding="utf-8") as handle:
        handle.write(json.dumps(board, ensure_ascii=False))


if sys.argv[1] == "opening":
    render_reply(agda.opening)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r0"
    agda_name, agda_vtt = f"{base}-agda.mp3", f"{base}-agda.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, agda_name))
    write_captions(os.path.join(audio_dir, agda_vtt), agda.opening, duration_of(aiff))
    call = LiveCall()
    call.add_turn("", agda.opening, False, "open_question",
                  robot_audio=f"audio/{agda_name}", robot_captions=f"audio/{agda_vtt}")
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    print(f"ROBOT: {agda.opening}")
elif sys.argv[1] == "round":
    heard = open(os.environ["TALK_TXT"], encoding="utf-8").read()
    answer = agda.reply_to(heard, int(os.environ["TALK_MISSES"]))
    log_round(heard, answer.matched)
    if answer.matched is None:
        log_miss(heard)
    render_reply(answer.reply)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r{os.environ['TALK_ROUND']}"
    you_name, agda_name = f"{base}-you.wav", f"{base}-agda.mp3"
    you_vtt, agda_vtt = f"{base}-you.vtt", f"{base}-agda.vtt"
    wav = os.environ["TALK_WAV"]
    aiff = os.environ["TALK_AIFF"]
    shutil.copy(wav, os.path.join(audio_dir, you_name))
    to_mp3(aiff, os.path.join(audio_dir, agda_name))
    write_captions(os.path.join(audio_dir, you_vtt), heard, duration_of(wav))
    write_captions(os.path.join(audio_dir, agda_vtt), answer.reply, duration_of(aiff))
    call = load_call()
    call.add_turn(heard.strip(), answer.reply, answer.matched is not None,
                  state_after(answer.done, answer.misses, answer.identify),
                  caller_audio=f"audio/{you_name}", robot_audio=f"audio/{agda_name}",
                  caller_captions=f"audio/{you_vtt}", robot_captions=f"audio/{agda_vtt}",
                  queue_place=answer.queue_place)
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    print(f"YOU:   {heard.strip()}")
    print(f"ROBOT: {answer.reply} (matched: {answer.matched})")
    print(f"TALK_DONE={'yes' if answer.done else 'no'}")
    print(f"TALK_MISSES={answer.misses}")
    print(f"TALK_IDENTIFY={'yes' if answer.identify else 'no'}")
elif sys.argv[1] == "identified":
    answer = agda.after_identified(int(os.environ["TALK_MISSES"]))
    render_reply(answer.reply)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r{os.environ['TALK_ROUND']}id"
    agda_name, agda_vtt = f"{base}-agda.mp3", f"{base}-agda.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, agda_name))
    write_captions(os.path.join(audio_dir, agda_vtt), answer.reply, duration_of(aiff))
    call = load_call()
    call.add_turn("", answer.reply, False, "queue",
                  robot_audio=f"audio/{agda_name}", robot_captions=f"audio/{agda_vtt}",
                  queue_place=answer.queue_place, queue_total=answer.queue_place)
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    print(f"ROBOT: {answer.reply}")
    print(f"TALK_PLACE={answer.queue_place}")
    print("TALK_DONE=no")
elif sys.argv[1] == "queue":
    answer = agda.queue_tick(int(os.environ["TALK_PLACE"]), int(os.environ["TALK_MISSES"]))
    render_reply(answer.reply)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r{os.environ['TALK_ROUND']}q{answer.queue_place}"
    agda_name, agda_vtt = f"{base}-agda.mp3", f"{base}-agda.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, agda_name))
    write_captions(os.path.join(audio_dir, agda_vtt), answer.reply, duration_of(aiff))
    call = load_call()
    call.add_turn("", answer.reply, False, "queue",
                  robot_audio=f"audio/{agda_name}", robot_captions=f"audio/{agda_vtt}",
                  queue_place=answer.queue_place,
                  queue_total=int(os.environ["TALK_TOTAL"]))
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    print(f"ROBOT: {answer.reply}")
    print(f"TALK_PLACE={answer.queue_place}")
    print(f"TALK_DONE={'yes' if answer.done else 'no'}")
elif sys.argv[1] == "english":
    heard = os.environ.get("TALK_EN_CALLER", "")
    ids = os.environ["TALK_EN_IDS"].split()
    text = " ".join(lines[line_id] for line_id in ids)
    sub = os.environ.get("TALK_EN_SUB", "")
    if sub:
        text = text.replace("1", sub, 1)
    state = os.environ["TALK_EN_STATE"]
    digit = os.environ.get("TALK_EN_DIGIT", "")
    if heard and state not in ("queue", "officer"):
        log_round(heard, f"dtmf:{digit}" if digit else None)
    render_reply(text)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = os.environ["TALK_EN_BASE"]
    agda_name, agda_vtt = f"{base}-agda.mp3", f"{base}-agda.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, agda_name))
    write_captions(os.path.join(audio_dir, agda_vtt), text, duration_of(aiff))
    call = load_call()
    place = os.environ.get("TALK_EN_PLACE", "")
    total = os.environ.get("TALK_EN_TOTAL", "")
    call.add_turn(heard, text, bool(digit), state,
                  robot_audio=f"audio/{agda_name}", robot_captions=f"audio/{agda_vtt}",
                  queue_place=int(place) if place else None,
                  queue_total=int(total) if total else None)
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    print(f"YOU:   {heard}")
    print(f"ROBOT: {text}")
    if place:
        print(f"TALK_PLACE={place}")
    print(f"TALK_DONE={'yes' if os.environ.get('TALK_EN_DONE', '') == '1' else 'no'}")
elif sys.argv[1] == "officer":
    text = lines[os.environ["TALK_OFF_ID"]]
    render_reply(text)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = os.environ["TALK_OFF_BASE"]
    agda_name, agda_vtt = f"{base}-agda.mp3", f"{base}-agda.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, agda_name))
    write_captions(os.path.join(audio_dir, agda_vtt), text, duration_of(aiff))
    call = load_call()
    call.add_turn("", text, False, "officer",
                  robot_audio=f"audio/{agda_name}", robot_captions=f"audio/{agda_vtt}",
                  speaker=os.environ.get("TALK_OFF_SPEAKER") or None)
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    print(f"ROBOT: {text}")
EOF
}

pick_english_voice() {
  # First decent installed English voice, else the Swedish default.
  _found="$(say -v '?' 2>/dev/null | grep -oE '^(Samantha|Karen|Moira|Daniel|Tessa|Fiona|Serena)' | head -1)"
  printf '%s' "${_found:-$VOICE}"
}

digit_caller() {
  # $1 = wait_digit return code. Sets DC_CALLER/DC_DIGIT, quits on 2.
  if [ "$1" = 2 ]; then quit_call; fi
  if [ "$1" = 0 ]; then
    DC_CALLER="(pressed $DIGIT)"; DC_DIGIT="$DIGIT"
  else
    DC_CALLER="(silence)"; DC_DIGIT=""
  fi
}

en_turn() {
  # $1 caller, $2 line ids, $3 digit sub (or ""), $4 state, $5 audio base,
  # $6 place (or ""), $7 total (or ""), $8 done 1/0, $9 digit (or "").
  EN_AIFF="$REC_DIR/talk-$CALL_STAMP-e$5.aiff"
  EN_ROBOT="AF Agda ($EN_VOICE)"
  EN_OUT="$(TALK_MAP=english TALK_ROBOT_NAME="$EN_ROBOT" \
    TALK_EN_CALLER="$1" TALK_EN_IDS="$2" TALK_EN_SUB="$3" TALK_EN_STATE="$4" \
    TALK_EN_BASE="talk-$CALL_STAMP-e$5" TALK_EN_PLACE="$6" TALK_EN_TOTAL="$7" \
    TALK_EN_DONE="$8" TALK_EN_DIGIT="$9" \
    agda_says english "" "$EN_AIFF" "" "$EN_VOICE")" || fail "Agda failed in English ($4)"
  printf '%s\n' "$EN_OUT" | grep -v '^TALK_'
  [ -s "$EN_AIFF" ] || fail "English audio missing: $EN_AIFF"
  [ -s "$AUDIO_DIR/talk-$CALL_STAMP-e$5-agda.mp3" ] || fail "English board audio missing: e$5"
  [ -s "$AUDIO_DIR/talk-$CALL_STAMP-e$5-agda.vtt" ] || fail "English board captions missing: e$5"
  ok "English turn on board: e$5 ($4)"
  run "Agda speaks English (any key skips, q quits, +/- volume)"
  play_skippable "$EN_AIFF"
}

run_english() {
  title "English menu (pressed 0)"
  what "Full call-5 path: key menu, sub-menu, SMS offer, identification, queue. Digits answer; silence moves on."
  EN_VOICE="$(pick_english_voice)"
  info "English voice: $EN_VOICE"
  en_turn "(pressed 0)" "L17" "" english_menu e01 "" "" 0 0
  run "wait for 1/2/4 (12 s, silence moves on)"
  wait_digit 12; digit_caller $?
  en_turn "$DC_CALLER" "L18" "" english_submenu e02 "" "" 0 "$DC_DIGIT"
  run "wait for 1/2 (12 s, silence moves on)"
  wait_digit 12; digit_caller $?
  en_turn "$DC_CALLER" "L31" "" sms e03 "" "" 0 "$DC_DIGIT"
  run "wait for 1 (12 s, silence moves on)"
  wait_digit 12; digit_caller $?
  en_turn "$DC_CALLER" "L32" "" identification e04 "" "" 0 "$DC_DIGIT"
  run "wait for BankID 1 / Freja 2 (12 s)"
  wait_digit 12; EN_RC=$?
  if [ "$EN_RC" = 2 ]; then quit_call; fi
  if [ "$EN_RC" = 0 ]; then
    ID_OK=1; ID_CALLER="(pressed $DIGIT)"; ID_DIGIT="$DIGIT"
  else
    en_turn "(silence)" "L33" "" identification e05 "" "" 0 ""
    run "wait again for 1/2 (12 s)"
    wait_digit 12; EN_RC=$?
    if [ "$EN_RC" = 2 ]; then quit_call; fi
    if [ "$EN_RC" = 0 ]; then
      ID_OK=1; ID_CALLER="(pressed $DIGIT)"; ID_DIGIT="$DIGIT"
    else
      ID_OK=0; ID_CALLER="(silence)"; ID_DIGIT=""
    fi
  fi
  if [ -n "$QUEUE_START" ]; then PLACE="$QUEUE_START"; else PLACE=$((RANDOM % 4 + 2)); fi
  START="$PLACE"
  if [ "$ID_OK" = 1 ]; then
    en_turn "$ID_CALLER" "L38 L35 L36" "$PLACE" queue e06 "$PLACE" "$START" 0 "$ID_DIGIT"
  else
    en_turn "$ID_CALLER" "L34 L35 L36" "$PLACE" queue e06 "$PLACE" "$START" 0 ""
  fi
  while [ "$PLACE" -gt 0 ]; do
    title "Queue: place $PLACE of $START (any key hurries, q quits, +/- volume)"
    if [ -t 0 ]; then
      wait_keys "$QUEUE_TICK" ""; EN_RC=$?
      [ "$EN_RC" = 2 ] && quit_call
    else
      sleep "$QUEUE_TICK"
    fi
    NEXT=$((PLACE - 1))
    if [ "$NEXT" = 0 ]; then
      en_turn "" "L37" "" officer eserv 0 "$START" 1 ""
      PLACE=0
    else
      en_turn "" "L36" "$NEXT" queue "q$NEXT" "$NEXT" "$START" 0 ""
      PLACE="$NEXT"
    fi
  done
  officer_scene en
  title "Call over — the officer answered. Your audio setup is restored on exit."
  exit 0
}

pick_sv_officer() {
  # Klara answers, unless Agda already uses her voice.
  if [ "$VOICE" != "Klara" ] && say -v '?' 2>/dev/null | grep -q '^Klara '; then
    printf 'Klara'
  else
    printf '%s' "$VOICE"
  fi
}

pick_en_officer() {
  # First installed English voice that is not Agda's English voice.
  for _v in Daniel Karen Moira Samantha Tessa Fiona Serena; do
    if [ "$_v" != "$EN_VOICE" ] && say -v '?' 2>/dev/null | grep -q "^$_v "; then
      printf '%s' "$_v"
      return 0
    fi
  done
  printf '%s' "$EN_VOICE"
}

officer_scene() {
  # $1 = sv|en. Touch-tone beeps while connecting, then the officer answers.
  if [ "$1" = "en" ]; then
    OFF_VOICE="$(pick_en_officer)"; OFF_ID="L40"; OFF_BASE="oen"
    OFF_MAP="english"; OFF_SPEAKER="Officer ($OFF_VOICE)"
  else
    OFF_VOICE="$(pick_sv_officer)"; OFF_ID="L39"; OFF_BASE="osv"
    OFF_MAP="swedish"; OFF_SPEAKER="Handläggare ($OFF_VOICE)"
  fi
  info "officer voice: $OFF_VOICE"
  step "Connecting"
  what "Touch-tone beeps while the call goes through, then the officer answers."
  if [ "$QUIET" = 1 ]; then
    info "(quiet: beeps muted)"
  else
  BEEPS_WAV="$REC_DIR/talk-$CALL_STAMP-beeps.wav"
  run "write DTMF beeps to $BEEPS_WAV"
  PYTHONPATH="$ROOT/src" python3 - "$BEEPS_WAV" <<'EOF' || fail "Could not make beeps"
import sys
from adaptive_ivr_agent.tones import write_beeps
write_beeps(sys.argv[1])
EOF
  [ -s "$BEEPS_WAV" ] || fail "Beeps missing: $BEEPS_WAV"
  run "play beeps (any key skips, q quits, +/- volume)"
  play_skippable "$BEEPS_WAV"
  fi
  OFF_AIFF="$REC_DIR/talk-$CALL_STAMP-officer.aiff"
  run "render officer ($OFF_VOICE)"
  OFF_OUT="$(TALK_MAP="$OFF_MAP" TALK_OFF_ID="$OFF_ID" \
    TALK_OFF_BASE="talk-$CALL_STAMP-$OFF_BASE" TALK_OFF_SPEAKER="$OFF_SPEAKER" \
    agda_says officer "" "$OFF_AIFF" "" "$OFF_VOICE")" || fail "Officer failed to answer"
  printf '%s\n' "$OFF_OUT" | grep -v '^TALK_'
  [ -s "$OFF_AIFF" ] || fail "Officer audio missing: $OFF_AIFF"
  [ -s "$AUDIO_DIR/talk-$CALL_STAMP-$OFF_BASE-agda.mp3" ] || fail "Officer board audio missing"
  ok "officer on board: $OFF_BASE"
  run "Officer speaks (any key skips, q quits, +/- volume)"
  play_skippable "$OFF_AIFF"
}

title "Agda is calling..."
run "render opening ($VOICE)"
OPENING_AIFF="$REC_DIR/talk-$CALL_STAMP-robot0.aiff"
agda_says opening "" "$OPENING_AIFF" || fail "Agda failed to speak the opening"
[ -s "$OPENING_AIFF" ] || fail "Opening audio missing: $OPENING_AIFF"
ok "opening saved: $OPENING_AIFF"
OPENING_MP3="$AUDIO_DIR/talk-$CALL_STAMP-r0-agda.mp3"
[ -s "$OPENING_MP3" ] || fail "Opening board audio missing: $OPENING_MP3"
ok "opening on board: $OPENING_MP3"
run "Agda speaks (any key skips, q quits, +/- volume)"
play_skippable "$OPENING_AIFF"
if [ "${KEY_PRESSED:-}" = "0" ]; then
  info "pressed 0: switching to the English menu"
  run_english
fi

run_identification() {
  title "Identification (faked, human in the loop)"
  what "Agda asked for BankID/Freja. A TEST number is pre-filled; typed input is ignored and digits are never logged."
  printf 'Personnummer [%s] (q quits): ' "$FAKE_PERSONNUMMER"
  read -r typed || typed=""
  if [ "$typed" = "q" ] || [ "$typed" = "Q" ]; then quit_call; fi
  if [ -n "$typed" ] && [ "$typed" != "$FAKE_PERSONNUMMER" ]; then
    info "ignoring typed input, using test number"
  fi
  ok "identified with test number"
  run "render confirmation ($VOICE)"
  ID_AIFF="$REC_DIR/talk-$CALL_STAMP-rid.aiff"
  OUT2="$(agda_says identified "" "$ID_AIFF")" || fail "Agda failed after identification"
  printf '%s\n' "$OUT2" | grep -v '^TALK_'
  [ -s "$ID_AIFF" ] || fail "Confirmation audio missing: $ID_AIFF"
  ID_MP3="$AUDIO_DIR/talk-$CALL_STAMP-r${ROUND}id-agda.mp3"
  [ -s "$ID_MP3" ] || fail "Confirmation board audio missing: $ID_MP3"
  ok "confirmation on board: $ID_MP3"
  run "Agda speaks (any key skips, q quits, +/- volume)"
  play_skippable "$ID_AIFF"
  START="$(printf '%s\n' "$OUT2" | sed -n 's/^TALK_PLACE=//p')"
  case "$START" in
    '' | *[!0-9]*) fail "Lost track of the queue place" ;;
  esac
  PLACE="$START"
  while [ "$PLACE" -gt 0 ]; do
    title "Queue: place $PLACE of $START (any key hurries, q quits, +/- volume)"
    if [ -t 0 ]; then
      wait_keys "$QUEUE_TICK" ""; RC=$?
      [ "$RC" = 2 ] && quit_call
    else
      sleep "$QUEUE_TICK"
    fi
    run "render queue number ($VOICE)"
    Q_AIFF="$REC_DIR/talk-$CALL_STAMP-q$PLACE.aiff"
    OUT3="$(agda_says queue "" "$Q_AIFF")" || fail "Agda failed in the queue"
    printf '%s\n' "$OUT3" | grep -v '^TALK_'
    [ -s "$Q_AIFF" ] || fail "Queue audio missing: $Q_AIFF"
    PLACE="$(printf '%s\n' "$OUT3" | sed -n 's/^TALK_PLACE=//p')"
    case "$PLACE" in
      '' | *[!0-9]*) fail "Lost track of the queue place" ;;
    esac
    Q_MP3="$AUDIO_DIR/talk-$CALL_STAMP-r${ROUND}q${PLACE}-agda.mp3"
    [ -s "$Q_MP3" ] || fail "Queue board audio missing: $Q_MP3"
    ok "queue number on board: $Q_MP3"
    run "Agda speaks (any key skips, q quits, +/- volume)"
    play_skippable "$Q_AIFF"
  done
  if [ "$(printf '%s\n' "$OUT3" | sed -n 's/^TALK_DONE=//p')" != "yes" ]; then
    fail "Queue did not finish"
  fi
  officer_scene sv
  title "Call over — the officer answered. Your audio setup is restored on exit."
  exit 0
}

ROUND=0
while [ "$ROUND" -lt 6 ]; do
  ROUND=$((ROUND + 1))
  if [ "$QUIET" = 1 ]; then
    title "Round $ROUND: type instead of speaking (q quits, /sound for sound)"
  else
    title "Round $ROUND: speak now ($RECORD_SECONDS s; any key stops, q quits, +/- volume)"
  fi
  WAV="$REC_DIR/talk-$CALL_STAMP-r$ROUND.wav"
  TXT="${WAV%.wav}.txt"
  ROBOT_AIFF="${WAV%.wav}-robot.aiff"
  if [ "$QUIET" = 1 ]; then
    printf 'Type now (q quits, /sound for sound, empty skips): '
    read -r typed || typed=""
    if [ "$typed" = "q" ] || [ "$typed" = "Q" ]; then quit_call; fi
    if [ "$typed" = "/sound" ]; then QUIET=0; info "sound on"; continue; fi
    if [ -z "${typed//[[:space:]]/}" ]; then warn "nothing typed, skipping this round"; continue; fi
    printf '%s\n' "$typed" > "$TXT"
    run "ffmpeg silent stand-in $WAV"
    ffmpeg -hide_banner -loglevel error -f lavfi -i anullsrc=r=16000:cl=mono -t 0.5 -y "$WAV" \
      || fail "Could not write silent audio"
  else
  run "ffmpeg ... -t $RECORD_SECONDS $WAV"
  ffmpeg -hide_banner -loglevel error -f avfoundation -i ":$MIC_INDEX" \
    -t "$RECORD_SECONDS" -ar 16000 -ac 1 -y "$WAV" &
  FFPID=$!
  wait_keys "$RECORD_SECONDS" "$FFPID"; RC=$?
  if [ "$RC" = 2 ]; then
    kill -INT "$FFPID" 2>/dev/null
    quit_call
  elif [ "$RC" = 0 ]; then
    kill -INT "$FFPID" 2>/dev/null
    if [ "${KEY_PRESSED:-}" = "0" ]; then
      wait "$FFPID" 2>/dev/null || true
      rm -f "$WAV"
      info "pressed 0: switching to the English menu"
      run_english
    fi
    info "stopped early"
  fi
  wait "$FFPID"; RC=$?
  case "$RC" in
    0|130|143) ;;
    *) fail "Recording failed (mic busy or permission revoked?)" ;;
  esac
  [ -s "$WAV" ] || fail "Recording is empty: $WAV"
  ok "recorded: $WAV"
  if ! "$HERE/check-recording.sh" "$WAV" >/dev/null 2>&1; then
    warn "silent recording, skipping this round"
    rm -f "$WAV"
    continue
  fi
  run "sh/transcribe-latest.sh $WAV"
  WHISPER_LANG="${WHISPER_LANG:-sv}" "$HERE/transcribe-latest.sh" "$WAV" >/dev/null \
    || fail "Transcription failed for $WAV"
  [ -f "$TXT" ] || fail "Transcript missing: $TXT"
  grep -q '[^[:space:]]' "$TXT" || { warn "nothing heard, skipping this round"; continue; }
  fi
  run "render reply ($VOICE)"
  OUT="$(agda_says round "$TXT" "$ROBOT_AIFF" "$WAV")" || fail "Agda failed to answer"
  printf '%s\n' "$OUT" | grep -v '^TALK_'
  MISSES="$(printf '%s\n' "$OUT" | sed -n 's/^TALK_MISSES=//p')"
  case "$MISSES" in
    '' | *[!0-9]*) fail "Lost track of the miss count" ;;
  esac
  [ -s "$ROBOT_AIFF" ] || fail "Robot audio missing: $ROBOT_AIFF"
  ok "robot reply saved: $ROBOT_AIFF"
  MP3="$AUDIO_DIR/talk-$CALL_STAMP-r$ROUND-agda.mp3"
  [ -s "$MP3" ] || fail "Board audio missing: $MP3"
  ok "board audio: $MP3"
  VTT="$AUDIO_DIR/talk-$CALL_STAMP-r$ROUND-agda.vtt"
  [ -s "$VTT" ] || fail "Board captions missing: $VTT"
  ok "board captions: $VTT"
  [ -f "$ROUNDS_FILE" ] || fail "Rounds log missing: $ROUNDS_FILE"
  ok "round logged for Holdmate training"
  [ -f "$BOARD_FILE" ] || fail "Board state missing: $BOARD_FILE"
  ok "board updated: $BOARD_FILE"
  run "Agda speaks (any key skips, q quits, +/- volume)"
  play_skippable "$ROBOT_AIFF"
  if [ "${KEY_PRESSED:-}" = "0" ]; then
    info "pressed 0: switching to the English menu"
    run_english
  fi
  if printf '%s\n' "$OUT" | grep -qx 'TALK_IDENTIFY=yes'; then
    run_identification
  fi
  if printf '%s\n' "$OUT" | grep -qx 'TALK_DONE=yes'; then
    title "Call over — Agda transferred you. Your audio setup is restored on exit."
    exit 0
  fi
done
warn "Round cap reached; stopping anyway (audio setup is restored on exit)"
