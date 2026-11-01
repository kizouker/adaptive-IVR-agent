#!/bin/bash
# Talk to the practice robot with your own voice (push-to-talk loop).
# Runs on: Rickard's Mac (M4). Modes: talk (default) | check. Flag: --airpods.
# Each round records ~5s from the MacBook mic, transcribes with whisper.cpp,
# and the robot answers aloud (Alva). Output goes through the IVR_Agent device
# (speakers + BlackHole) and everything is switched back on exit.
# Ctrl+C ends the loop; your audio setup is always restored.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
ROOT="$(cd "$HERE/.." && pwd)"

MODE="talk"
AIRPODS=0
for arg in "$@"; do
  case "$arg" in
    check|--check) MODE="check" ;;
    --airpods) AIRPODS=1 ;;
    *) fail "Unknown argument: $arg (use: check, --airpods)" ;;
  esac
done

OUTPUT_SPEAKERS="IVR_Agent_Speakers"   # MacBook speakers + BlackHole (default)
OUTPUT_AIRPODS="IVR_Agent_Output"      # AirPods + BlackHole (with --airpods)
NORMAL_OUTPUT="Högtalare i MacBook Pro" # switch back to this if we start on an IVR_Agent device
MIC="MacBook Pro-mikrofon"
RECORD_SECONDS="${RECORD_SECONDS:-5}"
MIC_INDEX="${MIC_INDEX:-}"             # empty = auto-detect; set to force an avfoundation index
VOICE="${VOICE:-Alva}"
TALK_VOLUME="${TALK_VOLUME:-0.4}"          # 1 = full blast; Rickard sets his own (e.g. TALK_VOLUME=0.7)
MODEL="$HOME/models/whisper/ggml-small.bin"
REC_DIR="$ROOT/data/recordings"
PHRASEBOOKS="$ROOT/data/role-phrasebooks.json"
MISS_FILE="$ROOT/data/talk-misses.jsonl"
LEARNED_FILE="$ROOT/data/learned-words.json"

MULTI_OUTPUT="$OUTPUT_SPEAKERS"
[ "$AIRPODS" = 1 ] && MULTI_OUTPUT="$OUTPUT_AIRPODS"

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
info "Agda plays at volume $TALK_VOLUME (1 = full; change with TALK_VOLUME=0.7 sh/talk.sh)"
info "Misses are logged to $MISS_FILE (teach them with sh/learn-words.sh)"

[ "$MODE" = "check" ] && { title "Check only: nothing changed"; exit 0; }

step "Switch audio"
what "Route output through $MULTI_OUTPUT (you hear the robot) and input from $MIC. Originals are restored on exit."
ORIGINAL_OUTPUT="$(SwitchAudioSource -c -t output)"
case "$ORIGINAL_OUTPUT" in
  IVR_Agent_*) ORIGINAL_OUTPUT="$NORMAL_OUTPUT" ;;
esac
ORIGINAL_INPUT="$(SwitchAudioSource -c -t input)"
switch_back() {
  SwitchAudioSource -s "$ORIGINAL_OUTPUT" -t output >/dev/null
  SwitchAudioSource -s "$ORIGINAL_INPUT" -t input >/dev/null
  info "Audio restored: output='$ORIGINAL_OUTPUT' input='$ORIGINAL_INPUT'"
}
trap switch_back EXIT
trap 'exit 130' INT TERM
SwitchAudioSource -s "$MULTI_OUTPUT" -t output >/dev/null
[ "$(SwitchAudioSource -c -t output)" = "$MULTI_OUTPUT" ] \
  || fail "Could not switch output to $MULTI_OUTPUT"
ok "output -> $MULTI_OUTPUT"
SwitchAudioSource -s "$MIC" -t input >/dev/null
[ "$(SwitchAudioSource -c -t input)" = "$MIC" ] || fail "Could not switch input to $MIC"
ok "input -> $MIC"

CALL_STAMP="$(date +%Y%m%d-%H%M%S)"
MISSES=0
TURNS_FILE="$REC_DIR/talk-$CALL_STAMP-turns.jsonl"
BOARD_FILE="$ROOT/ui/board/public/board-state.json"
AUDIO_DIR="$ROOT/ui/board/public/audio"

agda_says() {
  # $1 = opening|round, $2 = transcript file (round only), $3 = aiff file, $4 = caller wav (round only).
  # Speaks Agda's line, saves the audio, publishes the board state,
  # prints the exchange plus TALK_DONE / TALK_MISSES.
  TALK_ROOT="$ROOT" TALK_TXT="${2:-}" TALK_AIFF="$3" TALK_VOICE="$VOICE" TALK_MISSES="$MISSES" \
    TALK_VOLUME="$TALK_VOLUME" TALK_CALL="$CALL_STAMP" TALK_ROUND="${ROUND:-0}" \
    TALK_WAV="${4:-}" TALK_TURNS_FILE="$TURNS_FILE" TALK_BOARD_FILE="$BOARD_FILE" \
    TALK_AUDIO_DIR="$AUDIO_DIR" TALK_MISS_FILE="$MISS_FILE" TALK_LEARNED_FILE="$LEARNED_FILE" \
    PYTHONPATH="$ROOT/src" python3 - "$1" <<'EOF'
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from adaptive_ivr_agent.live_view import LiveCall, build_live_board, write_captions
from adaptive_ivr_agent.reactive import ReactiveRobot
from adaptive_ivr_agent.robot import SAY_VOICE, load_indexed_lines
from adaptive_ivr_agent.talk import AgdaCall, with_aliases

root = os.environ["TALK_ROOT"]
voice = os.environ.get("TALK_VOICE", SAY_VOICE)
lines = load_indexed_lines(os.path.join(root, "data/doorkeeper-lines.json"))
ears = ReactiveRobot.from_phrasebooks(os.path.join(root, "data/role-phrasebooks.json"))
learned_path = os.environ["TALK_LEARNED_FILE"]
aliases = json.load(open(learned_path, encoding="utf-8")) if os.path.exists(learned_path) else {}
agda = AgdaCall(
    opening=f"{lines['L01']} {lines['L02']}",
    examples=lines["L03"],
    yesno=lines["L22"],
    transfer=lines["L19"],
    respond=with_aliases(ears.respond, aliases),
)


def log_miss(heard):
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "call": os.environ["TALK_CALL"],
        "round": int(os.environ["TALK_ROUND"]),
        "heard": heard.strip(),
    }
    with open(os.environ["TALK_MISS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def say_and_save(text):
    out = os.environ["TALK_AIFF"]
    volume = os.environ.get("TALK_VOLUME", "0.4")
    subprocess.run(["say", "-v", voice, "-o", out, text], check=True)
    subprocess.run(["afplay", "-v", volume, out], check=True)


def state_after(done, misses):
    if done:
        return "transfer"
    if misses == 2:
        return "yes_no"
    if misses == 1:
        return "example_words"
    return "open_question"


def load_call():
    call = LiveCall()
    path = os.environ["TALK_TURNS_FILE"]
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                turn = json.loads(line)
                call.add_turn(turn["caller"], turn["robot"], turn["matched"], turn["state"],
                              turn.get("caller_audio"), turn.get("robot_audio"),
                              turn.get("caller_captions"), turn.get("robot_captions"))
    return call


def duration_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path],
                         check=True, capture_output=True, text=True)
    return float(out.stdout.strip())


def write_board(call):
    board = build_live_board([call])
    with open(os.environ["TALK_BOARD_FILE"], "w", encoding="utf-8") as handle:
        handle.write(json.dumps(board, ensure_ascii=False))


if sys.argv[1] == "opening":
    say_and_save(agda.opening)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r0"
    agda_name, agda_vtt = f"{base}-agda.mp3", f"{base}-agda.vtt"
    aiff = os.environ["TALK_AIFF"]
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", aiff,
                    "-codec:a", "libmp3lame", "-q:a", "4",
                    os.path.join(audio_dir, agda_name)], check=True)
    write_captions(os.path.join(audio_dir, agda_vtt), agda.opening, duration_of(aiff))
    call = LiveCall()
    call.add_turn("", agda.opening, False, "open_question",
                  robot_audio=f"audio/{agda_name}", robot_captions=f"audio/{agda_vtt}")
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    print(f"ROBOT: {agda.opening}")
else:
    heard = open(os.environ["TALK_TXT"], encoding="utf-8").read()
    reply, matched, done, misses = agda.reply_to(heard, int(os.environ["TALK_MISSES"]))
    if matched is None:
        log_miss(heard)
    say_and_save(reply)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r{os.environ['TALK_ROUND']}"
    you_name, agda_name = f"{base}-you.wav", f"{base}-agda.mp3"
    you_vtt, agda_vtt = f"{base}-you.vtt", f"{base}-agda.vtt"
    wav = os.environ["TALK_WAV"]
    aiff = os.environ["TALK_AIFF"]
    shutil.copy(wav, os.path.join(audio_dir, you_name))
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", aiff,
                    "-codec:a", "libmp3lame", "-q:a", "4",
                    os.path.join(audio_dir, agda_name)], check=True)
    write_captions(os.path.join(audio_dir, you_vtt), heard, duration_of(wav))
    write_captions(os.path.join(audio_dir, agda_vtt), reply, duration_of(aiff))
    call = load_call()
    call.add_turn(heard.strip(), reply, matched is not None,
                  state_after(done, misses),
                  caller_audio=f"audio/{you_name}", robot_audio=f"audio/{agda_name}",
                  caller_captions=f"audio/{you_vtt}", robot_captions=f"audio/{agda_vtt}")
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    print(f"YOU:   {heard.strip()}")
    print(f"ROBOT: {reply} (matched: {matched})")
    print(f"TALK_DONE={'yes' if done else 'no'}")
    print(f"TALK_MISSES={misses}")
EOF
}

title "Agda is calling..."
run "Agda speaks the opening ($VOICE)"
OPENING_AIFF="$REC_DIR/talk-$CALL_STAMP-robot0.aiff"
agda_says opening "" "$OPENING_AIFF" || fail "Agda failed to speak the opening"
[ -s "$OPENING_AIFF" ] || fail "Opening audio missing: $OPENING_AIFF"
ok "opening saved: $OPENING_AIFF"
OPENING_MP3="$AUDIO_DIR/talk-$CALL_STAMP-r0-agda.mp3"
[ -s "$OPENING_MP3" ] || fail "Opening board audio missing: $OPENING_MP3"
ok "opening on board: $OPENING_MP3"

ROUND=0
while [ "$ROUND" -lt 6 ]; do
  ROUND=$((ROUND + 1))
  title "Round $ROUND: speak now ($RECORD_SECONDS s, Ctrl+C to stop)"
  WAV="$REC_DIR/talk-$CALL_STAMP-r$ROUND.wav"
  TXT="${WAV%.wav}.txt"
  ROBOT_AIFF="${WAV%.wav}-robot.aiff"
  run "ffmpeg ... -t $RECORD_SECONDS $WAV"
  ffmpeg -hide_banner -loglevel error -f avfoundation -i ":$MIC_INDEX" \
    -t "$RECORD_SECONDS" -ar 16000 -ac 1 -y "$WAV" \
    || fail "Recording failed (mic busy or permission revoked?)"
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
  run "Agda answers aloud ($VOICE)"
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
  [ -f "$BOARD_FILE" ] || fail "Board state missing: $BOARD_FILE"
  ok "board updated: $BOARD_FILE"
  if printf '%s\n' "$OUT" | grep -qx 'TALK_DONE=yes'; then
    title "Call over — Agda transferred you. Your audio setup is restored on exit."
    exit 0
  fi
done
warn "Round cap reached; stopping anyway (audio setup is restored on exit)"
