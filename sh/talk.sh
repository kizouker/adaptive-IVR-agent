#!/bin/bash
# Talk to the practice robot with your own voice (push-to-talk loop).
# Runs on: Rickard's Mac (M4). Modes: talk (default) | check.
# check mode warns (exit 0) when audio devices are absent — a missing device on a
# clean machine is not an error; talk mode still fails loudly without them.
# Flags: --airpods (physical AirPods; must be connected), --output NAME (exact output
#   device; wins over everything), --as <persona> (role-play + tag rounds for Holdmate training),
#   --queue N (simulate a queue of N, 1-99; default is a random short one),
#   --quiet (type + read instead of speak + listen), --sound (force sound on),
#   --floor (level the system volume first; default leaves it untouched),
#   --busy (delay-notice welcome instead of the plain one),
#   --spark (rescue word-step misses with one Muse Spark call; keyless runs skip it).
# Output pick order: --output > $TALK_OUTPUT > .talk-output (holdmate menu) >
#   AirPods auto-follow > IVR_Agent_Speakers. Aggregate names overridable:
#   OUTPUT_SPEAKERS / OUTPUT_AIRPODS env. --lang=en|sv (default en, shared
#   .menu-lang memory with holdmate.sh). --call en|sv (default sv): the whole
#   call runs in that language (en lines, en ears, English TTS voice).
# The quiet/sound choice is remembered in .talk-quiet; flags override it and save.
# Env: ROKSOLANA_FORGIVING=1 enables Roksolana's bad memory (learned aliases, unrealistic).
#   QUEUE_TICK seconds between queue numbers (default 8).
# Keys during record/playback: any key skips ahead, 0 jumps to the English
# menu (full call-5 path on DTMF digits), a toggles speakers/AirPods output,
# t toggles quiet mode (hushes in-flight audio at once), + / - adjusts volume
# (0.1-4.0, 1 = normal; the board slider writes the same .talk-volume file).
# Each round records ~5s from the MacBook mic, transcribes with whisper.cpp,
# and the robot answers aloud (Alva). Output goes through the chosen device
# (default IVR_Agent_Speakers = speakers + BlackHole); everything is switched back on exit.
# Transfer asks for identification (faked test number, human in the loop),
# then the call lands in the simulated queue. Ctrl+C ends the loop.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
ROOT="$(cd "$HERE/.." && pwd)"
MENU_LANG="en"
VERBOSE=0
vrun() { [ "$VERBOSE" = 1 ] && run "$1"; }
vok() { [ "$VERBOSE" = 1 ] && ok "$1"; }
vinfo() { [ "$VERBOSE" = 1 ] && info "$1"; }
vstep() { [ "$VERBOSE" = 1 ] && step "$1"; }
vwhat() { [ "$VERBOSE" = 1 ] && what "$1"; }
vwarn() { [ "$VERBOSE" = 1 ] && warn "$1"; }
vsect() { [ "$VERBOSE" = 1 ] && sect "$1"; }
vnote() { [ "$VERBOSE" = 1 ] && note "$1"; }
T() { # $1 = key; prints the string for $MENU_LANG (en default, sv optional)
  case "$1" in
    sect_tools) _e="Tools"; _s="Verktyg" ;;
    sect_audio) _e="Audio"; _s="Ljud" ;;
    sect_data) _e="Data"; _s="Data" ;;
    sect_call) _e="Call"; _s="Samtal" ;;
    model) _e="Whisper model:"; _s="Whisper-modell:" ;;
    phrase) _e="phrasebooks:"; _s="frasböcker:" ;;
    out_dev) _e="output device:"; _s="utdata:" ;;
    out_chosen) _e="(chosen, auto-follow off)"; _s="(vald, autofölj av)" ;;
    auto_spk) _e="auto output: speakers (no AirPods connected)"; _s="auto: högtalare (inga AirPods anslutna)" ;;
    auto_pods) _e="auto output: AirPods connected, using them"; _s="auto: AirPods anslutna, använder dem" ;;
    toggle) _e="toggle target:"; _s="växlingsmål:" ;;
    press_a) _e="(press a during the call)"; _s="(tryck a under samtalet)" ;;
    no_pods) _e="no AirPods connected (mid-call a-key stays put)"; _s="inga AirPods anslutna (a-tangenten gör inget)" ;;
    not_found) _e="not found"; _s="hittades inte" ;;
    akey_put) _e="(mid-call a-key stays put)"; _s="(a-tangenten gör inget under samtalet)" ;;
    muted) _e="macOS output is MUTED (unmute to hear Roksolana)"; _s="macOS-ljudet är TYST (slå på för att höra Roksolana)" ;;
    lowvol_a) _e="macOS system volume is"; _s="macOS-volymen är" ;;
    lowvol_b) _e="(raise it to hear Roksolana well)"; _s="(höj för att höra Roksolana bra)" ;;
    floor_would) _e="check: talk mode would unmute + raise below"; _s="koll: samtalsläget skulle slå på ljudet + höja under" ;;
    floor_to) _e="to"; _s="till" ;;
    now_is) _e="now"; _s="nu" ;;
    floor_off) _e="check: talk mode leaves the system volume untouched (use --floor to level it first)"; _s="koll: samtalsläget lämnar volymen (använd --floor för att nivellera först)" ;;
    quiet_on) _e="quiet mode: type + read, t toggles sound back on"; _s="tyst läge: skriv + läs, t sätter på ljudet" ;;
    mic) _e="mic:"; _s="mic:" ;;
    mic_idx) _e="ffmpeg mic index:"; _s="ffmpeg-micindex:" ;;
    rec_to) _e="Recordings go to:"; _s="Inspelningar hamnar i:" ;;
    plays_a) _e="plays at volume"; _s="spelar på volym" ;;
    plays_b) _e="(1 = normal, up to 4 = boost; + / - during the call or the board slider)"; _s="(1 = normalt, upp till 4 = boost; + / - under samtalet eller boardreglaget)" ;;
    misses_a) _e="Misses are logged to"; _s="Missar loggas till" ;;
    misses_b) _e="(teach them with sh/learn-words.sh)"; _s="(lär ut dem med sh/learn-words.sh)" ;;
    rounds_a) _e="Every round is logged to"; _s="Varje runda loggas till" ;;
    rounds_b) _e="(Holdmate's training data)"; _s="(Holdmates träningsdata)" ;;
    mem_on) _e="bad memory ON: Roksolana accepts learned aliases (unrealistic practice)"; _s="dåligt minne PÅ: Roksolana accepterar inlärda alias (orealistisk träning)" ;;
    mem_off) _e="bad memory off: Roksolana only knows exact The Castle words (realistic)"; _s="dåligt minne av: Roksolana kan bara exakta The Castle-ord (realistiskt)" ;;
    q_at) _e="queue starts at"; _s="kön börjar på" ;;
    q_every) _e="ticks every"; _s="tickar var" ;;
    q_hurry) _e="(any key hurries)"; _s="(valfri tangent påskyndar)" ;;
    q_rand) _e="queue starts at random 2-5,"; _s="kön börjar på slumpmässiga 2-5," ;;
    title_talk) _e="Talk to the robot"; _s="Prata med roboten" ;;
    step_pre) _e="Preflight"; _s="Förkoll" ;;
    what_pre) _e="Check tools, model, phrasebooks and audio devices before touching anything."; _s="Kolla verktyg, modell, frasböcker och ljudenheter innan något ändras." ;;
    check_only) _e="Check only: nothing changed"; _s="Endast koll: inget ändrades" ;;
    keys_hint) _e="Keys: any key skips, q quits, +/- volume"; _s="Tangenter: valfri tangent hoppar över, q avslutar, +/- volym" ;;
    calling) _e="Calling Roksolana..."; _s="Ringer Roksolana..." ;;
    call_lang) _e="call language:"; _s="samtalspråk:" ;;
    you_live) _e="YOU (live):"; _s="DU (live):" ;;
    id_bad) _e="press 1 for BankID or 2 for Freja — other digits don't count"; _s="tryck 1 för BankID eller 2 för Freja — andra siffror räknas inte" ;;
  esac
  if [ "$MENU_LANG" = "sv" ]; then printf '%s' "$_s"; else printf '%s' "$_e"; fi
}
sect() { printf '%s%s── %s ──%s\n' "$D" '' "$1" "$X"; }

MODE="talk"
CALL_LANG="sv"
AUDIO_DEGRADED=0 # check mode: 1 once a missing device downgrades a fail to a warn
AIRPODS=0
PERSONA=""
QUIET=0
QUIET_FORCED=""
FLOOR=0
BUSY=0
SPARK=0
QUEUE_START=""
while [ $# -gt 0 ]; do
  case "$1" in
    check|--check) MODE="check"; VERBOSE=1 ;;
    --airpods) AIRPODS=1 ;;
    --output)
      TALK_OUTPUT="${2:-}"
      [ -n "$TALK_OUTPUT" ] || fail "--output needs a device name (see SwitchAudioSource -a)"
      shift
      ;;
    --mic)
      MIC_FLAG="${2:-}"
      [ -n "$MIC_FLAG" ] || fail "--mic needs a device name (see SwitchAudioSource -a -t input)"
      MIC_GIVEN=1
      shift
      ;;
    --call)
      CALL_LANG="${2:-}"
      case "$CALL_LANG" in en|sv) ;; *) fail "--call needs en or sv" ;; esac
      shift
      ;;
    --lang=*) MENU_LANG="${1#--lang=}"; LANG_GIVEN=1 ;;
    --lang) fail "--lang needs a value: --lang=en or --lang=sv" ;;
    -v|--verbose) VERBOSE=1 ;;
    --quiet) QUIET=1; QUIET_FORCED=1 ;;
    --sound) QUIET=0; QUIET_FORCED=0 ;;
    --floor) FLOOR=1 ;;
    --busy) BUSY=1 ;;
    --spark) SPARK=1 ;;
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
    *) fail "Unknown argument: $1 (use: check, --airpods, --output NAME, --mic NAME, --lang=en|sv, --call en|sv, -v, --as <persona>, --queue N, --quiet, --sound, --floor, --busy, --spark)" ;;
  esac
  shift
done
case "$MENU_LANG" in en|sv) ;; *) fail "--lang must be en or sv" ;; esac
if [ -f "$ROOT/.menu-lang" ] && [ "${LANG_GIVEN:-0}" != 1 ]; then
  _lang_remembered="$(cat "$ROOT/.menu-lang" 2>/dev/null)"
  case "$_lang_remembered" in en|sv) MENU_LANG="$_lang_remembered" ;; esac
fi

OUTPUT_SPEAKERS="${OUTPUT_SPEAKERS:-IVR_Agent_Speakers}" # MacBook speakers + BlackHole (default)
OUTPUT_AIRPODS="${OUTPUT_AIRPODS:-IVR_Agent_Airpods}" # AirPods + BlackHole aggregate
NORMAL_OUTPUT="Högtalare i MacBook Pro" # physical fallback (also the AirPods-off target)
_MIC_ENV="${MIC:-}"
MIC="MacBook Pro-mikrofon"
if [ -f "$ROOT/.talk-input" ]; then
  _mic_remembered="$(cat "$ROOT/.talk-input" 2>/dev/null)"
  [ -n "$_mic_remembered" ] && MIC="$_mic_remembered" # menu pick wins over default
fi
[ -n "$_MIC_ENV" ] && MIC="$_MIC_ENV" # $MIC env wins over the menu pick
[ "${MIC_GIVEN:-0}" = 1 ] && MIC="$MIC_FLAG" # --mic wins over everything
RECORD_SECONDS="${RECORD_SECONDS:-5}"
MIC_INDEX="${MIC_INDEX:-}"             # empty = auto-detect; set to force an avfoundation index
_VOICE_ENV="${VOICE:-}"
VOICE="${VOICE:-Alva}"
FLOOR_LEVEL=70                        # with --floor, talk mode raises a quieter output to this (merged devices can't be raised later); default leaves it untouched
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
QUIET_FILE="${TALK_QUIET_FILE:-$ROOT/.talk-quiet}"
save_quiet() { printf '%s' "$QUIET" > "$QUIET_FILE"; }
if [ -n "$QUIET_FORCED" ]; then
  QUIET="$QUIET_FORCED"                   # flags win for the session and are remembered
  save_quiet
elif [ -f "$QUIET_FILE" ] && grep -Eq '^[01]$' "$QUIET_FILE"; then
  QUIET="$(cat "$QUIET_FILE")"            # remembered t-toggle/flag from last run
fi
ROKSOLANA_FORGIVING="${ROKSOLANA_FORGIVING:-0}"     # 1 = Roksolana's bad memory (learned aliases); 0 = exact The Castle words
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

apply_call_voice() {
  # English call with no explicit VOICE: switch to an English TTS voice.
  if [ "${CALL_LANG:-sv}" != "en" ] || [ -n "${_VOICE_ENV:-}" ]; then
    return 0
  fi
  _found="$(say -v '?' 2>/dev/null | grep -oE '^(Samantha|Karen|Moira|Daniel|Tessa|Fiona|Serena)' | head -1)"
  VOICE="${_found:-$VOICE}"
}
apply_call_voice

MULTI_OUTPUT="$OUTPUT_SPEAKERS"
AUTO_PODS="$(find_airpods)"
if [ -n "${TALK_OUTPUT:-}" ]; then
  MULTI_OUTPUT="$TALK_OUTPUT" # explicit --output/env wins over auto-follow
else
  _remembered=""
  [ -f "$ROOT/.talk-output" ] && _remembered="$(cat "$ROOT/.talk-output" 2>/dev/null)"
  if [ -n "$_remembered" ] && SwitchAudioSource -a -t output 2>/dev/null | grep -Fxq "$_remembered"; then
    MULTI_OUTPUT="$_remembered" # menu choice from holdmate.sh
  elif [ "$AIRPODS" = 1 ]; then
    if [ -n "$AUTO_PODS" ]; then
      MULTI_OUTPUT="$AUTO_PODS"
    elif [ "$MODE" = "check" ]; then
      AUDIO_DEGRADED=1
      warn "No AirPods found among output devices (check continues on $OUTPUT_SPEAKERS)"
    else
      fail "No AirPods found among output devices (connect them first, then retry)"
    fi
  elif [ -n "$AUTO_PODS" ]; then
    MULTI_OUTPUT="$AUTO_PODS"
  fi
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
  command -v osascript >/dev/null 2>&1 || { vwarn "osascript missing, skipping volume floor"; return 0; }
  _vol="$(osascript -e 'output volume of (get volume settings)' 2>/dev/null || true)"
  _muted="$(osascript -e 'output muted of (get volume settings)' 2>/dev/null || true)"
  case "$_vol" in
    '' | *[!0-9]*) vwarn "could not read system volume, skipping floor"; return 0 ;;
  esac
  ORIG_SYS_VOL="$_vol"
  ORIG_SYS_MUTED="$_muted"
  if [ "$_muted" = "true" ]; then
    osascript -e 'set volume output muted false' 2>/dev/null || true
    FLOOR_CHANGED=1
    vinfo "unmuted $1 (was muted)"
  fi
  if [ "$_vol" -lt "$FLOOR_LEVEL" ]; then
    osascript -e "set volume output volume $FLOOR_LEVEL" 2>/dev/null || true
    FLOOR_CHANGED=1
    vinfo "raised $1 system volume $_vol -> $FLOOR_LEVEL (merged device can't be raised later)"
  else
    vok "system volume $1: $_vol (floor $FLOOR_LEVEL)"
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
  vinfo "system volume restored: $FLOOR_TARGET -> $ORIG_SYS_VOL"
}

wintitle "talk to Roksolana"
[ "$VERBOSE" = 1 ] && title "$(T title_talk) ($MODE)"

vstep "$(T step_pre)"
vwhat "$(T what_pre)"
vsect "$(T sect_tools)"
for tool in ffmpeg ffprobe whisper-cli say afplay SwitchAudioSource python3; do
  command -v "$tool" >/dev/null 2>&1 || fail "$tool is missing (brew install $tool)"
done
ok "tools: ffmpeg, ffprobe, whisper-cli, say, afplay, SwitchAudioSource, python3"
[ -f "$MODEL" ] || fail "Whisper model not found: $MODEL (see docs/recording-setup.md, step 7)"
vok "$(T model) $MODEL"
[ -f "$PHRASEBOOKS" ] || fail "Phrasebooks not found: $PHRASEBOOKS"
vok "$(T phrase) $PHRASEBOOKS"
vsect "$(T sect_audio)"
OUTPUT_LIST="$(SwitchAudioSource -a -t output 2>/dev/null)" \
  || fail "Could not list output devices (SwitchAudioSource errored — broken audio setup?)"
OUTPUT_OK=1
if printf '%s\n' "$OUTPUT_LIST" | grep -Fxq "$MULTI_OUTPUT"; then
  vok "$(T out_dev) $MULTI_OUTPUT"
  if [ -n "${TALK_OUTPUT:-}" ] || [ -n "${_remembered:-}" ]; then
    vinfo "$(T out_dev) $MULTI_OUTPUT $(T out_chosen)"
  fi
elif [ "$MODE" = "check" ]; then
  OUTPUT_OK=0
  AUDIO_DEGRADED=1
  warn "Output device '$MULTI_OUTPUT' not found — clean machine? (create it in Audio MIDI Setup; talk mode needs it)"
else
  fail "Output device '$MULTI_OUTPUT' not found (open Audio MIDI Setup and check the Multi-Output device)"
fi
if [ "$AIRPODS" = 0 ] && [ "$OUTPUT_OK" = 1 ]; then
  if [ "$MULTI_OUTPUT" = "$OUTPUT_SPEAKERS" ]; then
    vinfo "$(T auto_spk)"
  else
    vinfo "$(T auto_pods)"
  fi
fi
if [ "$MULTI_OUTPUT" = "$OUTPUT_SPEAKERS" ]; then
  ALT_CHECK="$(find_airpods)"
  if [ -n "$ALT_CHECK" ]; then
    vok "$(T toggle) $ALT_CHECK $(T press_a)"
  else
    vwarn "$(T no_pods)"
  fi
elif SwitchAudioSource -a -t output | grep -Fxq "$OUTPUT_SPEAKERS"; then
  vok "$(T toggle) $OUTPUT_SPEAKERS $(T press_a)"
else
  vwarn "$(T toggle) '$OUTPUT_SPEAKERS' $(T not_found) $(T akey_put)"
fi
if command -v osascript >/dev/null 2>&1; then
  SYS_VOL="$(osascript -e "get volume settings" 2>/dev/null || true)"
  case "$SYS_VOL" in
    *"output muted:true"*) vwarn "$(T muted)" ;;
  esac
  SYS_LEVEL="$(printf '%s' "$SYS_VOL" | sed -n 's/.*output volume:\([0-9][0-9]*\).*/\1/p')"
  case "$SYS_LEVEL" in
    '' | *[!0-9]*) ;;
    *) if [ "$SYS_LEVEL" -lt 40 ]; then vwarn "$(T lowvol_a) $SYS_LEVEL $(T lowvol_b)"; fi ;;
  esac
fi
if [ "$MODE" = "check" ]; then
  if [ "$FLOOR" = 1 ]; then
    vnote "$(T floor_would) $FLOOR_LEVEL $(T floor_to) $FLOOR_LEVEL ($(T now_is): ${SYS_LEVEL:-unknown})"
  else
    vnote "$(T floor_off)"
  fi
fi
if [ "$QUIET" = 1 ]; then
  vinfo "$(T quiet_on)"
fi
INPUT_LIST="$(SwitchAudioSource -a -t input 2>/dev/null)" \
  || fail "Could not list input devices (SwitchAudioSource errored — broken audio setup?)"
MIC_OK=1
if printf '%s\n' "$INPUT_LIST" | grep -Fxq "$MIC"; then
  vok "$(T mic) $MIC"
elif [ "$MODE" = "check" ]; then
  MIC_OK=0
  AUDIO_DEGRADED=1
  warn "Mic '$MIC' not found — clean machine? (check System Settings -> Sound -> Input; talk mode needs it)"
else
  fail "Mic '$MIC' not found (check System Settings -> Sound -> Input)"
fi
if [ -z "$MIC_INDEX" ] && [ "$MIC_OK" = 1 ]; then
  MIC_INDEX="$(audio_index_for "$MIC")"
  [ -n "$MIC_INDEX" ] || fail "Could not find '$MIC' in the ffmpeg device list (first run may need mic permission: allow Terminal, then re-run)"
fi
if [ "$MIC_OK" = 1 ]; then
  vok "$(T mic_idx) $MIC_INDEX"
else
  warn "ffmpeg mic index: skipped (no mic '$MIC' to match)"
fi
vsect "$(T sect_data)"
mkdir -p "$REC_DIR"
vnote "$(T rec_to) $REC_DIR"
vnote "$(T misses_a) $MISS_FILE $(T misses_b)"
vnote "$(T rounds_a) $ROUNDS_FILE $(T rounds_b)"
vsect "$(T sect_call)"
vnote "Roksolana $(T plays_a) $TALK_VOLUME $(T plays_b)"
if [ "$ROKSOLANA_FORGIVING" = "1" ]; then
  vwarn "$(T mem_on)"
else
  vinfo "$(T mem_off)"
fi
vinfo "$(T call_lang) $CALL_LANG (voice: $VOICE)"
if [ "$SPARK" = "1" ]; then
  info "Spark fallback ON: one Muse Spark call rescues each word-step miss (skipped when keyless)"
fi
case "$QUEUE_TICK" in
  '' | *[!0-9]*) fail "QUEUE_TICK must be whole seconds" ;;
esac
if [ -n "$QUEUE_START" ]; then
  vinfo "$(T q_at) $QUEUE_START, $(T q_every) ${QUEUE_TICK}s $(T q_hurry)"
else
  vinfo "$(T q_rand) $(T q_every) ${QUEUE_TICK}s $(T q_hurry)"
fi

if [ "$MODE" = "check" ]; then
  if [ "$AUDIO_DEGRADED" = 1 ]; then
    title "Check only: nothing changed (audio devices missing — see warnings; talk mode needs them)"
  else
    title "$(T check_only)"
  fi
  exit 0
fi

vstep "Switch audio"
vwhat "Route audio through $MULTI_OUTPUT (--floor levels the physical output first). Originals are restored on exit."
ORIGINAL_OUTPUT="$(SwitchAudioSource -c -t output)"
case "$ORIGINAL_OUTPUT" in
  Agent_*|_Airpods|IVR_Agent_*) ORIGINAL_OUTPUT="$NORMAL_OUTPUT" ;;
esac
ORIGINAL_INPUT="$(SwitchAudioSource -c -t input)"
switch_back() {
  stty sane 2>/dev/null || true
  SwitchAudioSource -s "$ORIGINAL_OUTPUT" -t output >/dev/null
  SwitchAudioSource -s "$ORIGINAL_INPUT" -t input >/dev/null
  wintitle "done"
  rm -f "$DTMF_FILE"
  vinfo "Audio restored: output='$ORIGINAL_OUTPUT' input='$ORIGINAL_INPUT'"
  restore_system_volume
}
trap switch_back EXIT
trap 'exit 130' INT TERM
if [ "$FLOOR" = 1 ]; then
  if [ "$MULTI_OUTPUT" = "$OUTPUT_SPEAKERS" ]; then _floor_target="$NORMAL_OUTPUT"
  elif [ "$MULTI_OUTPUT" = "$OUTPUT_AIRPODS" ] && [ -n "$AUTO_PODS" ]; then _floor_target="$AUTO_PODS"
  else _floor_target="$MULTI_OUTPUT"; fi
  if [ "$(SwitchAudioSource -c -t output)" != "$_floor_target" ]; then
    SwitchAudioSource -s "$_floor_target" -t output >/dev/null \
      || fail "Could not switch output to $_floor_target"
    vok "output -> $_floor_target (level check)"
  fi
  floor_system_volume "$_floor_target"
else
  vinfo "system volume left untouched (use --floor to level it first)"
fi
SwitchAudioSource -s "$MULTI_OUTPUT" -t output >/dev/null
[ "$(SwitchAudioSource -c -t output)" = "$MULTI_OUTPUT" ] \
  || fail "Could not switch output to $MULTI_OUTPUT"
vok "output -> $MULTI_OUTPUT"
SwitchAudioSource -s "$MIC" -t input >/dev/null
[ "$(SwitchAudioSource -c -t input)" = "$MIC" ] || fail "Could not switch input to $MIC"
vok "input -> $MIC"

if [ -n "$PERSONA" ]; then
  vstep "Role card"
  vwhat "Show who you are calling as, so you can speak from that errand."
  vrun "read $PERSONA from role-phrasebooks.json"
  if ! PYTHONPATH="$ROOT/src" python3 - "$PERSONA" "$PHRASEBOOKS" <<'CARD'
import json
import sys
import textwrap
roles = json.load(open(sys.argv[2], encoding="utf-8"))["roles"]
persona = next((r for r in roles if r["id"] == sys.argv[1]), None)
if persona is None:
    sys.exit(1)
print(f"── Role: {persona['label']} ──")
print(f"Errand: {persona['errand']}")
for line in textwrap.wrap("Words: " + ", ".join(persona["vocabulary"]), width=84):
    print(line)
print("Checklist (guidance, not legal advice):")
for i, item in enumerate(persona.get("checklist", []), 1):
    for line in textwrap.wrap(f"Say: {item['say']}", width=78,
                              initial_indent=f"  {i}. ",
                              subsequent_indent="     "):
        print(line)
    for line in textwrap.wrap(f"Why: {item['why']}", width=78,
                              initial_indent="     ",
                              subsequent_indent="     "):
        print(line)
CARD
  then
    info "valid persona ids:"
    PYTHONPATH="$ROOT/src" python3 -c "import json; [print(' - ' + r['id']) for r in json.load(open('$PHRASEBOOKS'))['roles']]"
    fail "Unknown persona '$PERSONA'"
  fi
  vok "rounds will be tagged: $PERSONA"
fi

CALL_STAMP="$(date +%Y%m%d-%H%M%S)"
MISSES=0
TURNS_FILE="$REC_DIR/talk-$CALL_STAMP-turns.jsonl"
BOARD_FILE="$ROOT/ui/board/public/board-state.json"
AUDIO_DIR="$ROOT/ui/board/public/audio"
VOLUME_FILE="$ROOT/.talk-volume"
DTMF_FILE="$ROOT/.talk-dtmf"

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
  save_quiet
  if [ -n "${1:-}" ]; then kill "$1" 2>/dev/null; return 0; fi
  return 1
}

drain_keys() {
  # Drop stale buffered stdin bytes (leftover Enter etc.) so a fresh wait starts clean.
  [ -t 0 ] || return 0
  while read -t 0 -n 1 -s _drain_key; do :; done
}

poll_dtmf() { # web keypad digit: sets DTMF_DIGIT, consumes file
  # No Mac beep here: the browser already beeps instantly (else it sounds twice).
  # The board server writes $STATE_DIR/dtmf; local .talk-dtmf also works.
  DTMF_DIGIT=""
  [ -n "${CALL_STAMP:-}" ] || return 1
  _dtmf=""
  for _cand in "$DTMF_FILE" "${STATE_DIR:-/tmp/holdmate}/dtmf"; do
    if [ -f "$_cand" ]; then _dtmf="$_cand"; break; fi
  done
  [ -n "$_dtmf" ] || return 1
  _d="$(cat "$_dtmf" 2>/dev/null)" || return 1
  rm -f "$_dtmf"
  case "$_d" in
    [0-9*#]) ;;
    *) return 1 ;;
  esac
  DTMF_DIGIT="$_d"
  return 0
}

wait_keys() { # $1 seconds, $2 pid to watch (or ""); 0 = skip, 1 = time out, 2 = quit
  drain_keys
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
    if poll_dtmf; then
      KEY_PRESSED="$DTMF_DIGIT"
      return 0
    fi
  done
  return 1
}

wait_digit() { # $1 seconds; 0 = digit in DIGIT, 1 = silence, 2 = quit
  drain_keys
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
    if poll_dtmf; then
      case "$DTMF_DIGIT" in
        [0-9]) DIGIT="$DTMF_DIGIT"; return 0 ;;
      esac
      info "web key $DTMF_DIGIT is no choice here"
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
      vinfo "boost x$TALK_VOLUME (ffmpeg gain)"
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
      vinfo "skipped ahead"
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

roksolana_says() {
  # $1 = opening|round|identified|queue|english|officer, $2 = transcript (round only),
  # $3 = aiff file, $4 = caller wav (round only), $5 = voice override (or "").
  # Speaks Roksolana's line, saves the audio, publishes the board state,
  # prints the exchange plus TALK_DONE / TALK_MISSES.
  TALK_ROOT="$ROOT" TALK_TXT="${2:-}" TALK_AIFF="$3" TALK_VOICE="${5:-$VOICE}" TALK_MISSES="$MISSES" \
    TALK_CALL="$CALL_STAMP" TALK_ROUND="${ROUND:-0}" \
    TALK_WAV="${4:-}" TALK_TURNS_FILE="$TURNS_FILE" TALK_BOARD_FILE="$BOARD_FILE" \
    TALK_AUDIO_DIR="$AUDIO_DIR" TALK_MISS_FILE="$MISS_FILE" TALK_LEARNED_FILE="$LEARNED_FILE" \
    TALK_ROUNDS_FILE="$ROUNDS_FILE" TALK_PERSONA="$PERSONA" TALK_FORGIVING="$ROKSOLANA_FORGIVING" \
    TALK_QUEUE_START="$QUEUE_START" TALK_BUSY="$BUSY" TALK_SPARK="$SPARK" TALK_PLACE="${PLACE:-}" TALK_TOTAL="${START:-}" \
    TALK_CALL_LANG="$CALL_LANG" \
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
    build_coverage,
    build_live_board,
    carry_board_lines,
    line_translations,
    translate_robot,
    write_captions,
)
from adaptive_ivr_agent.intent import SparkFallback, maybe_spark_normalizer
from adaptive_ivr_agent.reactive import ReactiveRobot
from adaptive_ivr_agent.robot import SAY_VOICE, load_indexed_lines, opening_cache_path
from adaptive_ivr_agent.talk import RoksolanaCall, with_aliases

root = os.environ["TALK_ROOT"]
voice = os.environ.get("TALK_VOICE", SAY_VOICE)
call_lang = os.environ.get("TALK_CALL_LANG", "sv")
lines = load_indexed_lines(os.path.join(root, "data/doorkeeper-lines.json"),
                            lang=call_lang)
translations = line_translations(os.path.join(root, "data/doorkeeper-lines.json"))
if os.environ.get("NO_COLOR"):
    _G = _Y = _X = ""
else:
    _G, _Y, _X = "\033[36m", "\033[2m", "\033[0m"


EN_BITS = ["For English, press 0."]
TALK_JSON = os.environ.get("TALK_JSON") == "1"


def _wrap(text, width=84):
    import textwrap
    return textwrap.wrap(text, width=width) or [""]


def _sentences(text):
    import re
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def _is_option(sentence):
    import re
    return re.search(r"\b(press|tryck)\s+\d", sentence, re.IGNORECASE) is not None


SPEAKER_NAME = os.environ.get("TALK_SPEAKER_NAME", "Roksolana")


def show_robot(text, suffix=""):
    """Bilingual turn: one sentence per line, digit options highlighted."""
    if TALK_JSON:
        print(json.dumps({"speaker": "robot", "sv": text,
                          "en": translate_robot(text, translations),
                          "note": suffix.strip()},
                         ensure_ascii=False))
        return
    sv = text
    for bit in EN_BITS:
        sv = sv.replace(bit, "")
    sv = " ".join(sv.split())
    en = translate_robot(text, translations)
    opt = "\033[1;33m" if not os.environ.get("NO_COLOR") else ""
    print(f"── {SPEAKER_NAME} ──{suffix}")
    for sentence in _sentences(sv):
        color = opt if _is_option(sentence) else _G
        for line in _wrap(sentence):
            print(f"{color}{line}{_X}")
    if en != text:
        print("── English ──")
        for sentence in _sentences(en):
            color = opt if _is_option(sentence) else _Y
            for line in _wrap(sentence):
                print(f"{color}{line}{_X}")
ears = ReactiveRobot.from_phrasebooks(
    os.path.join(root, "data/role-phrasebooks.json"), lang=call_lang)
learned_path = os.environ["TALK_LEARNED_FILE"]
forgiving = os.environ.get("TALK_FORGIVING") == "1"
if forgiving and os.path.exists(learned_path):
    aliases = json.load(open(learned_path, encoding="utf-8"))
else:
    aliases = {}
base_respond = with_aliases(ears.respond, aliases)
spark_fallback = None
if os.environ.get("TALK_SPARK") == "1":
    with open(os.path.join(root, "data/role-phrasebooks.json"), encoding="utf-8") as handle:
        talk_roles = json.load(handle)["roles"]
    talk_vocab = list(dict.fromkeys(
        word for role in talk_roles for word in role["vocabulary"]))
    spark_normalizer = maybe_spark_normalizer(True)
    if spark_normalizer is None:
        print("spark: no key, fallback skipped (keyless run)", file=sys.stderr)
    else:
        spark_fallback = SparkFallback(base_respond, spark_normalizer, talk_vocab)
        base_respond = spark_fallback.respond
forced_start = os.environ.get("TALK_QUEUE_START", "").strip()
forced = int(forced_start) if forced_start.isdigit() else None
# Full verbatim L01: the English sentence is spoken by an English voice.
# --busy swaps in the L44 delay notice with language choice only (call 5
# part 3); press 0 reaches the English menu, other input reprompts as usual.
busy = os.environ.get("TALK_BUSY") == "1"
welcome = lines["L44"] if busy else lines["L01"]
# L30: Rickard's pick 1 Nov (UNVERIFIED memory). Replace with verbatim
# from Monday's sampling.
SERVED_LINE = lines["L30"]
roksolana = RoksolanaCall(
    opening=welcome if busy else f"{welcome} {lines['L02']}",
    examples=lines["L03"],
    yesno=lines["L22"],
    yesno_reprompt=lines["L41"],
    transfer=lines["L19"],
    identify_line=f"{lines['L43']} {lines['L09']}",
    identified_line=lines["L11"],
    failed_line=lines["L12"],
    served_line=SERVED_LINE,
    queue_line=lines["L13"],
    place_template=lines["L29"],
    respond=base_respond,
    queue_place=(lambda: forced) if forced else None,
    english_menu=lines["L17"],
    yesno_words=("yes", "no") if call_lang == "en" else ("ja", "nej"),
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
                              turn.get("queue_place"), turn.get("queue_total"),
                              spark=turn.get("spark"))
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
    try:
        with open(os.path.join(root, "data/holdmate-knowledge.json"),
                  encoding="utf-8") as handle:
            known = json.load(handle)
    except (OSError, ValueError):
        known = None
    if known:
        board["lessons"] = known.get("lessons", [])
        board["words"] = {
            word: {"tries": entry["tries"], "transfers": entry["transfers"]}
            for word, entry in known.get("words", {}).items()
        }
        try:
            with open(os.path.join(root, "data/role-phrasebooks.json"),
                      encoding="utf-8") as handle:
                all_roles = json.load(handle)["roles"]
        except (OSError, ValueError, KeyError):
            all_roles = []
        if all_roles:
            board["coverage"] = build_coverage(all_roles, known.get("words", {}))
    board = carry_board_lines(board, os.environ["TALK_BOARD_FILE"])
    with open(os.environ["TALK_BOARD_FILE"], "w", encoding="utf-8") as handle:
        handle.write(json.dumps(board, ensure_ascii=False))


if sys.argv[1] == "opening":
    marker = "For English, press 0."
    out_aiff = os.environ["TALK_AIFF"]
    en_voice = os.environ.get("TALK_EN_VOICE", voice)
    cached = opening_cache_path(
        os.path.join(root, "data/recordings/.opening-cache"),
        voice, en_voice, roksolana.opening)
    if cached.exists() and cached.stat().st_size > 0:
        shutil.copy(cached, out_aiff)
    elif marker in roksolana.opening:
        sv1, _, rest = roksolana.opening.partition(marker)
        sv1_aiff, en_aiff, sv2_aiff = out_aiff + ".sv1", out_aiff + ".en", out_aiff + ".sv2"
        subprocess.run(["say", "-v", voice, "-o", sv1_aiff, sv1.strip()], check=True)
        subprocess.run(["say", "-v", en_voice, "-o", en_aiff, marker], check=True)
        subprocess.run(["say", "-v", voice, "-o", sv2_aiff, rest.strip()], check=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", sv1_aiff, "-i", en_aiff, "-i", sv2_aiff,
                        "-filter_complex", "[0:a][1:a][2:a]concat=n=3:v=0:a=1",
                        out_aiff], check=True)
        os.remove(sv1_aiff)
        os.remove(en_aiff)
        os.remove(sv2_aiff)
        shutil.copy(out_aiff, cached)
    else:
        render_reply(roksolana.opening)
        shutil.copy(out_aiff, cached)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r0"
    roksolana_name, roksolana_vtt = f"{base}-roksolana.mp3", f"{base}-roksolana.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, roksolana_name))
    write_captions(os.path.join(audio_dir, roksolana_vtt), roksolana.opening, duration_of(aiff))
    call = LiveCall()
    call.add_turn("", roksolana.opening, False, "open_question",
                  robot_audio=f"audio/{roksolana_name}", robot_captions=f"audio/{roksolana_vtt}",
                  robot_en=translate_robot(roksolana.opening, translations))
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    show_robot(roksolana.opening)
elif sys.argv[1] == "round":
    heard = open(os.environ["TALK_TXT"], encoding="utf-8").read()
    answer = roksolana.reply_to(heard, int(os.environ["TALK_MISSES"]))
    log_round(heard, answer.matched)
    if answer.matched is None:
        log_miss(heard)
    render_reply(answer.reply)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r{os.environ['TALK_ROUND']}"
    you_name, roksolana_name = f"{base}-you.wav", f"{base}-roksolana.mp3"
    you_vtt, roksolana_vtt = f"{base}-you.vtt", f"{base}-roksolana.vtt"
    wav = os.environ["TALK_WAV"]
    aiff = os.environ["TALK_AIFF"]
    shutil.copy(wav, os.path.join(audio_dir, you_name))
    to_mp3(aiff, os.path.join(audio_dir, roksolana_name))
    write_captions(os.path.join(audio_dir, you_vtt), heard, duration_of(wav))
    write_captions(os.path.join(audio_dir, roksolana_vtt), answer.reply, duration_of(aiff))
    call = load_call()
    spark = spark_fallback.last if spark_fallback is not None else None
    call.add_turn(heard.strip(), answer.reply, answer.matched is not None,
                  state_after(answer.done, answer.misses, answer.identify),
                  robot_en=translate_robot(answer.reply, translations),
                  caller_audio=f"audio/{you_name}", robot_audio=f"audio/{roksolana_name}",
                  caller_captions=f"audio/{you_vtt}", robot_captions=f"audio/{roksolana_vtt}",
                  queue_place=answer.queue_place, spark=spark)
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    print(f"YOU:   {heard.strip()}")
    show_robot(answer.reply, f" (matched: {answer.matched})")
    if spark is not None:
        print(f"TALK_SPARK={spark['word']} {spark['confidence']}")
    else:
        print("TALK_SPARK=")
    print(f"TALK_DONE={'yes' if answer.done else 'no'}")
    print(f"TALK_MISSES={answer.misses}")
    print(f"TALK_IDENTIFY={'yes' if answer.identify else 'no'}")
elif sys.argv[1] == "identified":
    ok = os.environ.get("TALK_ID_OK", "1") == "1"
    answer = roksolana.after_identified(int(os.environ["TALK_MISSES"]), ok=ok)
    render_reply(answer.reply)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r{os.environ['TALK_ROUND']}id"
    roksolana_name, roksolana_vtt = f"{base}-roksolana.mp3", f"{base}-roksolana.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, roksolana_name))
    write_captions(os.path.join(audio_dir, roksolana_vtt), answer.reply, duration_of(aiff))
    call = load_call()
    call.add_turn("", answer.reply, False, "queue",
                  robot_audio=f"audio/{roksolana_name}", robot_captions=f"audio/{roksolana_vtt}",
                  queue_place=answer.queue_place, queue_total=answer.queue_place,
                  robot_en=translate_robot(answer.reply, translations))
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    show_robot(answer.reply)
    print(f"TALK_PLACE={answer.queue_place}")
    print("TALK_DONE=no")
elif sys.argv[1] == "idline":
    line_id = os.environ["TALK_ID_LINE"]
    text = lines[line_id]
    render_reply(text)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r{os.environ['TALK_ROUND']}{line_id.lower()}"
    roksolana_name, roksolana_vtt = f"{base}-roksolana.mp3", f"{base}-roksolana.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, roksolana_name))
    write_captions(os.path.join(audio_dir, roksolana_vtt), text, duration_of(aiff))
    call = load_call()
    call.add_turn("", text, False, "identification",
                  robot_audio=f"audio/{roksolana_name}", robot_captions=f"audio/{roksolana_vtt}",
                  robot_en=translate_robot(text, translations))
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    show_robot(text)
    print("TALK_DONE=no")
elif sys.argv[1] == "queue":
    answer = roksolana.queue_tick(int(os.environ["TALK_PLACE"]), int(os.environ["TALK_MISSES"]))
    render_reply(answer.reply)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = f"talk-{os.environ['TALK_CALL']}-r{os.environ['TALK_ROUND']}q{answer.queue_place}"
    roksolana_name, roksolana_vtt = f"{base}-roksolana.mp3", f"{base}-roksolana.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, roksolana_name))
    write_captions(os.path.join(audio_dir, roksolana_vtt), answer.reply, duration_of(aiff))
    call = load_call()
    call.add_turn("", answer.reply, False, "queue",
                  robot_audio=f"audio/{roksolana_name}", robot_captions=f"audio/{roksolana_vtt}",
                  queue_place=answer.queue_place,
                  queue_total=int(os.environ["TALK_TOTAL"]),
                  robot_en=translate_robot(answer.reply, translations))
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    show_robot(answer.reply)
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
    roksolana_name, roksolana_vtt = f"{base}-roksolana.mp3", f"{base}-roksolana.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, roksolana_name))
    write_captions(os.path.join(audio_dir, roksolana_vtt), text, duration_of(aiff))
    call = load_call()
    place = os.environ.get("TALK_EN_PLACE", "")
    total = os.environ.get("TALK_EN_TOTAL", "")
    call.add_turn(heard, text, bool(digit), state,
                  robot_audio=f"audio/{roksolana_name}", robot_captions=f"audio/{roksolana_vtt}",
                  queue_place=int(place) if place else None,
                  queue_total=int(total) if total else None,
                  robot_en=translate_robot(text, translations))
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    print(f"YOU:   {heard}")
    show_robot(text)
    if place:
        print(f"TALK_PLACE={place}")
    print(f"TALK_DONE={'yes' if os.environ.get('TALK_EN_DONE', '') == '1' else 'no'}")
elif sys.argv[1] == "officer":
    text = lines[os.environ["TALK_OFF_ID"]]
    render_reply(text)
    audio_dir = os.environ["TALK_AUDIO_DIR"]
    os.makedirs(audio_dir, exist_ok=True)
    base = os.environ["TALK_OFF_BASE"]
    roksolana_name, roksolana_vtt = f"{base}-roksolana.mp3", f"{base}-roksolana.vtt"
    aiff = os.environ["TALK_AIFF"]
    to_mp3(aiff, os.path.join(audio_dir, roksolana_name))
    write_captions(os.path.join(audio_dir, roksolana_vtt), text, duration_of(aiff))
    call = load_call()
    call.add_turn("", text, False, "officer",
                  robot_audio=f"audio/{roksolana_name}", robot_captions=f"audio/{roksolana_vtt}",
                  speaker=os.environ.get("TALK_OFF_SPEAKER") or None,
                  robot_en=translate_robot(text, translations))
    with open(os.environ["TALK_TURNS_FILE"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(call.turns[-1], ensure_ascii=False) + "\n")
    write_board(call)
    show_robot(text)
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

digit_or_wait() { # a digit pressed during playback counts; else wait 12 s
  case "${KEY_PRESSED:-}" in
    [0-9])
      DIGIT="$KEY_PRESSED"; KEY_PRESSED=""
      vinfo "using pressed digit $DIGIT"
      return 0
      ;;
  esac
  wait_digit 12
}

en_turn() {
  # $1 caller, $2 line ids, $3 digit sub (or ""), $4 state, $5 audio base,
  # $6 place (or ""), $7 total (or ""), $8 done 1/0, $9 digit (or "").
  EN_AIFF="$REC_DIR/talk-$CALL_STAMP-e$5.aiff"
  EN_ROBOT="Roksolana ($EN_VOICE)"
  EN_OUT="$(TALK_MAP=english TALK_ROBOT_NAME="$EN_ROBOT" \
    TALK_EN_CALLER="$1" TALK_EN_IDS="$2" TALK_EN_SUB="$3" TALK_EN_STATE="$4" \
    TALK_EN_BASE="talk-$CALL_STAMP-e$5" TALK_EN_PLACE="$6" TALK_EN_TOTAL="$7" \
    TALK_EN_DONE="$8" TALK_EN_DIGIT="$9" \
    roksolana_says english "" "$EN_AIFF" "" "$EN_VOICE")" || fail "Roksolana failed in English ($4)"
  printf '%s\n' "$EN_OUT" | grep -v '^TALK_'
  [ -s "$EN_AIFF" ] || fail "English audio missing: $EN_AIFF"
  [ -s "$AUDIO_DIR/talk-$CALL_STAMP-e$5-roksolana.mp3" ] || fail "English board audio missing: e$5"
  [ -s "$AUDIO_DIR/talk-$CALL_STAMP-e$5-roksolana.vtt" ] || fail "English board captions missing: e$5"
  ok "English turn on board: e$5 ($4)"
  vrun "Roksolana speaks English"
  play_skippable "$EN_AIFF"
}

run_english() {
  wintitle "English menu"
  title "English menu (pressed 0)"
  what "Full call-5 path: key menu, sub-menu, SMS offer, identification, queue. Digits answer; silence moves on."
  EN_VOICE="$(pick_english_voice)"
  vinfo "English voice: $EN_VOICE"
  en_turn "(pressed 0)" "L17" "" english_menu e01 "" "" 0 0
  run "wait for 1/2/4 (12 s, silence moves on)"
  digit_or_wait; digit_caller $?
  en_turn "$DC_CALLER" "L18" "" english_submenu e02 "" "" 0 "$DC_DIGIT"
  run "wait for 1/2 (12 s, silence moves on)"
  digit_or_wait; digit_caller $?
  en_turn "$DC_CALLER" "L31" "" sms e03 "" "" 0 "$DC_DIGIT"
  run "wait for 1 (12 s, silence moves on)"
  digit_or_wait; digit_caller $?
  en_turn "$DC_CALLER" "L32" "" identification e04 "" "" 0 "$DC_DIGIT"
  vrun "wait for BankID 1 / Freja 2 (12 s)"
  digit_or_wait; EN_RC=$?
  if [ "$EN_RC" = 2 ]; then quit_call; fi
  if [ "$EN_RC" = 0 ]; then
    METHOD_OK=1; ID_CALLER="(pressed $DIGIT)"; ID_DIGIT="$DIGIT"
  else
    en_turn "(silence)" "L33" "" identification e05 "" "" 0 ""
    vrun "wait again for 1/2 (12 s)"
    digit_or_wait; EN_RC=$?
    if [ "$EN_RC" = 2 ]; then quit_call; fi
    if [ "$EN_RC" = 0 ]; then
      METHOD_OK=1; ID_CALLER="(pressed $DIGIT)"; ID_DIGIT="$DIGIT"
    else
      METHOD_OK=0; ID_CALLER="(silence)"; ID_DIGIT=""
    fi
  fi
  if [ -n "$QUEUE_START" ]; then PLACE="$QUEUE_START"; else PLACE=$((RANDOM % 4 + 2)); fi
  START="$PLACE"
  if [ "$METHOD_OK" = 1 ]; then
    # Choosing a method is not approving: confirm in the app first (L42).
    en_turn "$ID_CALLER" "L42" "" identification e06 "" "" 0 "$ID_DIGIT"
    run "wait for in-app approval, press 1 (20 s)"
    digit_or_wait; EN_RC=$?
    if [ "$EN_RC" = 2 ]; then quit_call; fi
    if [ "$EN_RC" = 0 ] && [ "$DIGIT" = 1 ]; then
      en_turn "(pressed 1)" "L38 L35 L36" "$PLACE" queue e07 "$PLACE" "$START" 0 1
    else
      en_turn "(silence)" "L34 L35 L36" "$PLACE" queue e07 "$PLACE" "$START" 0 ""
    fi
  else
    en_turn "$ID_CALLER" "L34 L35 L36" "$PLACE" queue e07 "$PLACE" "$START" 0 ""
  fi
  while [ "$PLACE" -gt 0 ]; do
    title "Queue: place $PLACE of $START (any key hurries, q quits, +/- volume)"
    wintitle "queue $PLACE of $START"
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
  # Klara answers, unless Roksolana already uses her voice.
  if [ "$VOICE" != "Klara" ] && say -v '?' 2>/dev/null | grep -q '^Klara '; then
    printf 'Klara'
  else
    printf '%s' "$VOICE"
  fi
}

pick_en_officer() {
  # First installed English voice that is not Roksolana's English voice.
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
    OFF_MAP="english"; OFF_SPEAKER="Officer Erik ($OFF_VOICE)"
  else
    OFF_VOICE="$(pick_sv_officer)"; OFF_ID="L39"; OFF_BASE="osv"
    OFF_MAP="swedish"; OFF_SPEAKER="Handläggare ($OFF_VOICE)"
  fi
  vinfo "officer voice: $OFF_VOICE"
  vstep "Connecting"
  vwhat "Touch-tone beeps while the call goes through, then the officer answers."
  if [ "$QUIET" = 1 ]; then
    vinfo "(quiet: beeps muted)"
  else
  BEEPS_WAV="$REC_DIR/talk-$CALL_STAMP-beeps.wav"
  vrun "write DTMF beeps to $BEEPS_WAV"
  PYTHONPATH="$ROOT/src" python3 - "$BEEPS_WAV" <<'EOF' || fail "Could not make beeps"
import sys
from adaptive_ivr_agent.tones import write_beeps
write_beeps(sys.argv[1])
EOF
  [ -s "$BEEPS_WAV" ] || fail "Beeps missing: $BEEPS_WAV"
  vrun "play beeps (any key skips, q quits, +/- volume)"
  play_skippable "$BEEPS_WAV"
  fi
  OFF_AIFF="$REC_DIR/talk-$CALL_STAMP-officer.aiff"
  vrun "render officer ($OFF_VOICE)"
  OFF_OUT="$(TALK_MAP="$OFF_MAP" TALK_OFF_ID="$OFF_ID" \
    TALK_OFF_BASE="talk-$CALL_STAMP-$OFF_BASE" TALK_OFF_SPEAKER="$OFF_SPEAKER" \
    TALK_SPEAKER_NAME="$OFF_SPEAKER" \
    roksolana_says officer "" "$OFF_AIFF" "" "$OFF_VOICE")" || fail "Officer failed to answer"
  printf '%s\n' "$OFF_OUT" | grep -v '^TALK_'
  [ -s "$OFF_AIFF" ] || fail "Officer audio missing: $OFF_AIFF"
  [ -s "$AUDIO_DIR/talk-$CALL_STAMP-$OFF_BASE-roksolana.mp3" ] || fail "Officer board audio missing"
  vok "officer on board: $OFF_BASE"
  vrun "Officer speaks"
  if [ -t 1 ]; then
    pacman_loop & _PACMAN=$!
    play_skippable "$OFF_AIFF"
    kill "$_PACMAN" 2>/dev/null
    wait "$_PACMAN" 2>/dev/null
    printf '\r%50s\r' ''
  else
    play_skippable "$OFF_AIFF"
  fi
}

pacman_loop() { # ping-pong pacman while the officer talks (killed after)
  _x=0; _d=1; _f=0
  while true; do
    if [ "$_d" = 1 ]; then
      if [ "$_f" = 0 ]; then _m="C>"; else _m="c>"; fi
    else
      if [ "$_f" = 0 ]; then _m="<C"; else _m="<c"; fi
    fi
    printf '\r    %*s%s' "$_x" '' "$_m"
    _f=$((1 - _f))
    _x=$((_x + _d))
    if [ "$_x" -ge 28 ]; then _d=-1; elif [ "$_x" -le 0 ]; then _d=1; fi
    sleep 0.12
  done
}

title "$(T calling)"
info "$(T keys_hint)"
rm -f "$DTMF_FILE"
vrun "render opening ($VOICE + English voice)"
OPENING_AIFF="$REC_DIR/talk-$CALL_STAMP-robot0.aiff"
EN_OPEN_VOICE="$(pick_english_voice)"
vinfo "English voice: $EN_OPEN_VOICE"
TALK_EN_VOICE="$EN_OPEN_VOICE" roksolana_says opening "" "$OPENING_AIFF" || fail "Roksolana failed to speak the opening"
[ -s "$OPENING_AIFF" ] || fail "Opening audio missing: $OPENING_AIFF"
vok "opening saved: $OPENING_AIFF"
OPENING_MP3="$AUDIO_DIR/talk-$CALL_STAMP-r0-roksolana.mp3"
[ -s "$OPENING_MP3" ] || fail "Opening board audio missing: $OPENING_MP3"
vok "opening on board: $OPENING_MP3"
vrun "Roksolana speaks"
play_skippable "$OPENING_AIFF"
if [ "${KEY_PRESSED:-}" = "0" ]; then
  info "pressed 0: switching to the English menu"
  run_english
fi

id_say_line() { # $1 = L10|L12: Roksolana speaks it and boards it
  IDLINE_AIFF="$REC_DIR/talk-$CALL_STAMP-$1.aiff"
  OUTL="$(TALK_ID_LINE="$1" roksolana_says idline "" "$IDLINE_AIFF")" || fail "Roksolana failed ($1)"
  printf '%s\n' "$OUTL" | grep -v '^TALK_'
  [ -s "$IDLINE_AIFF" ] || fail "ID line audio missing: $IDLINE_AIFF"
  vrun "Roksolana speaks"
  play_skippable "$IDLINE_AIFF"
}

run_identification() {
  wintitle "identification"
  [ "$VERBOSE" = 1 ] && title "Identification (faked, human in the loop)"
  vwhat "BankID (1) or Freja (2) first, then the TEST number. Enter uses it; anything else reprompts and digits are never logged."
  vrun "wait for BankID 1 / Freja 2 (12 s)"
  digit_or_wait; ID_RC=$?
  if [ "$ID_RC" = 2 ]; then quit_call; fi
  ID_OK=0
  if [ "$ID_RC" = 0 ]; then
    case "$DIGIT" in 1|2) ID_OK=1;; *) warn "$(T id_bad)";; esac
  fi
  if [ "$ID_OK" != 1 ]; then
    id_say_line L10
    vrun "wait again for 1/2 (12 s)"
    digit_or_wait; ID_RC=$?
    if [ "$ID_RC" = 2 ]; then quit_call; fi
    if [ "$ID_RC" = 0 ]; then
      case "$DIGIT" in 1|2) ID_OK=1;; *) warn "$(T id_bad)";; esac
    fi
  fi
  if [ "$ID_OK" = 1 ]; then
    while true; do
      printf 'Personnummer [%s] (Enter = test number, q quits): ' "$FAKE_PERSONNUMMER"
      read -r typed || typed=""
      if [ "$typed" = "q" ] || [ "$typed" = "Q" ]; then quit_call; fi
      if [ -z "$typed" ] || [ "$typed" = "$FAKE_PERSONNUMMER" ]; then break; fi
      warn "only the test number is accepted (nothing real ever flows)"
    done
    vok "identified with test number"
  else
    ID_OK=0
    id_say_line L12
  fi
  vrun "render confirmation ($VOICE)"
  ID_AIFF="$REC_DIR/talk-$CALL_STAMP-rid.aiff"
  OUT2="$(TALK_ID_OK="$ID_OK" roksolana_says identified "" "$ID_AIFF")" || fail "Roksolana failed after identification"
  printf '%s\n' "$OUT2" | grep -v '^TALK_'
  [ -s "$ID_AIFF" ] || fail "Confirmation audio missing: $ID_AIFF"
  ID_MP3="$AUDIO_DIR/talk-$CALL_STAMP-r${ROUND}id-roksolana.mp3"
  [ -s "$ID_MP3" ] || fail "Confirmation board audio missing: $ID_MP3"
  vok "confirmation on board: $ID_MP3"
  vrun "Roksolana speaks"
  play_skippable "$ID_AIFF"
  START="$(printf '%s\n' "$OUT2" | sed -n 's/^TALK_PLACE=//p')"
  case "$START" in
    '' | *[!0-9]*) fail "Lost track of the queue place" ;;
  esac
  PLACE="$START"
  while [ "$PLACE" -gt 0 ]; do
    title "Queue: place $PLACE of $START (any key hurries, q quits, +/- volume)"
    wintitle "queue $PLACE of $START"
    if [ -t 0 ]; then
      wait_keys "$QUEUE_TICK" ""; RC=$?
      [ "$RC" = 2 ] && quit_call
    else
      sleep "$QUEUE_TICK"
    fi
    run "render queue number ($VOICE)"
    Q_AIFF="$REC_DIR/talk-$CALL_STAMP-q$PLACE.aiff"
    OUT3="$(roksolana_says queue "" "$Q_AIFF")" || fail "Roksolana failed in the queue"
    printf '%s\n' "$OUT3" | grep -v '^TALK_'
    [ -s "$Q_AIFF" ] || fail "Queue audio missing: $Q_AIFF"
    PLACE="$(printf '%s\n' "$OUT3" | sed -n 's/^TALK_PLACE=//p')"
    case "$PLACE" in
      '' | *[!0-9]*) fail "Lost track of the queue place" ;;
    esac
    Q_MP3="$AUDIO_DIR/talk-$CALL_STAMP-r${ROUND}q${PLACE}-roksolana.mp3"
    [ -s "$Q_MP3" ] || fail "Queue board audio missing: $Q_MP3"
    ok "queue number on board: $Q_MP3"
    vrun "Roksolana speaks"
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
  wintitle "talk round $ROUND"
  WAV="$REC_DIR/talk-$CALL_STAMP-r$ROUND.wav"
  TXT="${WAV%.wav}.txt"
  ROBOT_AIFF="${WAV%.wav}-robot.aiff"
  if [ "$QUIET" = 1 ]; then
    printf 'Type now (q quits, /sound for sound, empty skips): '
    read -r typed || typed=""
    if [ "$typed" = "q" ] || [ "$typed" = "Q" ]; then quit_call; fi
    if [ "$typed" = "/sound" ]; then QUIET=0; save_quiet; info "sound on"; continue; fi
    if [ -z "${typed//[[:space:]]/}" ]; then warn "nothing typed, skipping this round"; continue; fi
    printf '%s\n' "$typed" > "$TXT"
    vrun "ffmpeg silent stand-in $WAV"
    ffmpeg -hide_banner -loglevel error -f lavfi -i anullsrc=r=16000:cl=mono -t 0.5 -y "$WAV" \
      || fail "Could not write silent audio"
  else
  vrun "ffmpeg ... -t $RECORD_SECONDS $WAV"
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
  vok "recorded: $WAV"
  if ! "$HERE/check-recording.sh" "$WAV" >/dev/null 2>&1; then
    warn "silent recording, counts as no answer"
    printf '(silence)\n' > "$TXT"
  else
    vrun "sh/transcribe-latest.sh $WAV"
    WHISPER_LOG="/tmp/whisper-err.log"
    if [ "$VERBOSE" = 1 ]; then
      WHISPER_LANG="${WHISPER_LANG:-sv}" "$HERE/transcribe-latest.sh" "$WAV" >/dev/null \
        || fail "Transcription failed for $WAV"
    else
      WHISPER_LANG="${WHISPER_LANG:-sv}" "$HERE/transcribe-latest.sh" "$WAV" >/dev/null 2>"$WHISPER_LOG" \
        || { cat "$WHISPER_LOG" >&2; fail "Transcription failed for $WAV"; }
    fi
    [ -f "$TXT" ] || fail "Transcript missing: $TXT"
    if ! grep -q '[^[:space:]]' "$TXT"; then
      warn "nothing heard, counts as no answer"
      printf '(silence)\n' > "$TXT"
    fi
  fi
  fi
  vrun "render reply ($VOICE)"
  OUT="$(roksolana_says round "$TXT" "$ROBOT_AIFF" "$WAV")" || fail "Roksolana failed to answer"
  printf '%s\n' "$OUT" | grep -v '^TALK_'
  MISSES="$(printf '%s\n' "$OUT" | sed -n 's/^TALK_MISSES=//p')"
  case "$MISSES" in
    '' | *[!0-9]*) fail "Lost track of the miss count" ;;
  esac
  [ -s "$ROBOT_AIFF" ] || fail "Robot audio missing: $ROBOT_AIFF"
  vok "robot reply saved: $ROBOT_AIFF"
  MP3="$AUDIO_DIR/talk-$CALL_STAMP-r$ROUND-roksolana.mp3"
  [ -s "$MP3" ] || fail "Board audio missing: $MP3"
  vok "board audio: $MP3"
  VTT="$AUDIO_DIR/talk-$CALL_STAMP-r$ROUND-roksolana.vtt"
  [ -s "$VTT" ] || fail "Board captions missing: $VTT"
  vok "board captions: $VTT"
  [ -f "$ROUNDS_FILE" ] || fail "Rounds log missing: $ROUNDS_FILE"
  vok "round logged for Holdmate training"
  [ -f "$BOARD_FILE" ] || fail "Board state missing: $BOARD_FILE"
  vok "board updated: $BOARD_FILE"
  vrun "Roksolana speaks"
  play_skippable "$ROBOT_AIFF"
  if [ "${KEY_PRESSED:-}" = "0" ]; then
    info "pressed 0: switching to the English menu"
    run_english
  fi
  if printf '%s\n' "$OUT" | grep -qx 'TALK_IDENTIFY=yes'; then
    run_identification
  fi
  if printf '%s\n' "$OUT" | grep -qx 'TALK_DONE=yes'; then
    title "Call over — Roksolana transferred you. Your audio setup is restored on exit."
    exit 0
  fi
done
warn "Round cap reached; stopping anyway (audio setup is restored on exit)"
