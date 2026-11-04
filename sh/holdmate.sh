#!/bin/bash
# Holdmate launcher: board server + talk from one menu, runnable from anywhere.
# Runs on: Rickard's Mac (M4). Modes: menu (default) | check. Direct: 1, 2, 3, 4.
# 1 = start the board server, open the page, and talk. 2 = talk options.
# 3 = misc menu (Teach Roksolana parked). 4 = lessons submenu (silent/spoken, one/all).
# Runs from any folder; paths resolve from this script.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
ROOT="$(cd "$HERE/.." && pwd)"
MODE="menu"
VERBOSE=0
SOUND="speakers"
vstep() { [ "$VERBOSE" = 1 ] && step "$1"; }
vwhat() { [ "$VERBOSE" = 1 ] && what "$1"; }
vok() { [ "$VERBOSE" = 1 ] && ok "$1"; }
vinfo() { [ "$VERBOSE" = 1 ] && info "$1"; }
vrun() { [ "$VERBOSE" = 1 ] && run "$1"; }
MENU_LANG="en"
T() { # $1 = key; prints the string for $MENU_LANG (en default, sv optional)
  case "$1" in
    tagline) _e="waits on hold, so you don't have to"; _s="väntar i kö, så du slipper" ;;
    menu_title) _e="Holdmate menu (arrows + Enter, Esc quits)"; _s="Holdmate-meny (pilar + Enter, Esc avslutar)" ;;
    m_board) _e="Board + talk (server, page, call)"; _s="Tavla + samtal (server, sida, samtal)" ;;
    m_talk) _e="Talk options (server runs already)"; _s="Samtalsval (servern kör redan)" ;;
    m_misc) _e="Misc..."; _s="Övrigt..." ;;
    m_lessons) _e="Holdmate phones Roksolana alone (BFS)"; _s="Holdmate ringer Roksolana själv (BFS)" ;;
    m_sound) _e="Sound"; _s="Ljud" ;;
    m_change) _e="(change...)"; _s="(ändra...)" ;;
    m_github) _e="GitHub (repo, site, pulls...)"; _s="GitHub (repo, sajt, pulls...)" ;;
    m_lang) _e="Language: English (change)"; _s="Språk: svenska (ändra)" ;;
    m_quit) _e="Quit"; _s="Avsluta" ;;
    back) _e="Back"; _s="Tillbaka" ;;
    bye) _e="Bye"; _s="Hej då" ;;
    type_num) _e="Type a number: "; _s="Skriv ett nummer: " ;;
    gh_title) _e="GitHub (arrows + Enter, Esc goes back)"; _s="GitHub (pilar + Enter, Esc tillbaka)" ;;
    gh_repo) _e="Open repo"; _s="Öppna repo" ;;
    gh_site) _e="Open live site (Pages)"; _s="Öppna sajten (Pages)" ;;
    gh_pulls) _e="Open pull requests"; _s="Öppna pull requests" ;;
    gh_issues) _e="Open issues"; _s="Öppna issues" ;;
    gh_actions) _e="Open Actions"; _s="Öppna Actions" ;;
    out_title) _e="Output (now:"; _s="Utdata (nu:" ;;
    speakers) _e="Speakers"; _s="Högtalare" ;;
    vol_title) _e="Volume (now:"; _s="Volym (nu:" ;;
    louder) _e="Louder (+)"; _s="Högre (+)" ;;
    quieter) _e="Quieter (-)"; _s="Lägre (-)" ;;
    snd_title) _e="Sound (now:"; _s="Ljud (nu:" ;;
    snd_output) _e="Output:"; _s="Utdata:" ;;
    snd_volume) _e="Volume:"; _s="Volym:" ;;
    snd_quiet) _e="Quiet:"; _s="Tyst:" ;;
    quiet_word) _e="Quiet"; _s="Tyst" ;;
    on) _e="on"; _s="på" ;;
    off) _e="off"; _s="av" ;;
    talk_title) _e="Talk options (arrows + Enter, Esc goes back)"; _s="Samtalsval (pilar + Enter, Esc tillbaka)" ;;
    t_talk) _e="Talk to Roksolana"; _s="Prata med Roksolana" ;;
    t_airpods) _e="Talk with AirPods"; _s="Prata med AirPods" ;;
    t_check) _e="Sound check only"; _s="Endast ljudkoll" ;;
    t_persona) _e="Talk as persona"; _s="Prata som persona" ;;
    t_quiet) _e="Talk quietly (type + read)"; _s="Prata tyst (skriv + läs)" ;;
    lsn_title) _e="Holdmate phones Roksolana alone (arrows + Enter, Esc goes back)"; _s="Holdmate ringer Roksolana själv (pilar + Enter, Esc tillbaka)" ;;
    lsn_silent) _e="All personas, silent (space = more, q = stop)"; _s="Alla personas, tyst (mellanslag = mer, q = stopp)" ;;
    lsn_spoken) _e="All personas, spoken (Oskar + Alva, Ctrl+C = stop)"; _s="Alla personas, tal (Oskar + Alva, Ctrl+C = stopp)" ;;
    lsn_one) _e="One persona, spoken (pick..., Ctrl+C = stop)"; _s="En persona, tal (välj..., Ctrl+C = stopp)" ;;
    stopped) _e="stopped early, partial knowledge saved (back to menu)"; _s="stoppade tidigt, delkunskap sparad (tillbaka till menyn)" ;;
    ended) _e="lessons ended early (see above)"; _s="lektionerna slutade tidigt (se ovan)" ;;
    misc_title) _e="Misc (arrows + Enter, Esc goes back)"; _s="Övrigt (pilar + Enter, Esc tillbaka)" ;;
    teach) _e="Teach Roksolana new words (disabled)"; _s="Lär Roksolana nya ord (avstängt)" ;;
    teach_off) _e="Teach Roksolana is disabled for now (Roksolana stays dumb; Holdmate is the learner)"; _s="Lär Roksolana är avstängt (Roksolana förblir dum; Holdmate är eleven)" ;;
    step_board) _e="Board + talk"; _s="Tavla + samtal" ;;
    what_board) _e="Start the server, open the page, then talk. Server stops when this ends."; _s="Starta servern, öppna sidan, prata sedan. Servern stoppas när detta slutar." ;;
    opened) _e="opened"; _s="öppnade" ;;
    in_browser) _e="in your browser"; _s="i webbläsaren" ;;
    open_this) _e="open this"; _s="öppna detta" ;;
    vol_word) _e="volume"; _s="volym" ;;
    vol_used) _e="(used by the next talk)"; _s="(används av nästa samtal)" ;;
    snd_word) _e="sound"; _s="ljud" ;;
    auto_pick) _e="Auto-follow (AirPods when worn)"; _s="Autofölj (AirPods när de bärs)" ;;
    auto_on) _e="output: auto-follow on"; _s="utdata: autofölj på" ;;
  esac
  if [ "$MENU_LANG" = "sv" ]; then printf '%s' "$_s"; else printf '%s' "$_e"; fi
}
pickmsg() { # $1 = "1-N"; invalid-choice hint for $MENU_LANG
  if [ "$MENU_LANG" = "sv" ]; then warn "välj med pilar + Enter (eller skriv $1)";
  else warn "pick with arrows + Enter (or type $1)"; fi
}
SOUND_DIRTY=0
sync_sound() {
  # Follow AirPods when worn (current output OR just connected) until
  # Rickard picks sound explicitly (#191).
  if [ "$SOUND_DIRTY" = 1 ]; then return 0; fi
  if command -v SwitchAudioSource >/dev/null 2>&1; then
    if SwitchAudioSource -c -t output 2>/dev/null | grep -qi 'airpods' \
      || SwitchAudioSource -a -t output 2>/dev/null | grep -qi 'airpods'; then
      SOUND="airpods"
      return 0
    fi
  fi
  SOUND="speakers"
}
sound_label() {
  case "$SOUND" in
    airpods) printf 'AirPods' ;;
    quiet) T quiet_word ;;
    *) T speakers ;;
  esac
}
sync_sound
if [ -f "$ROOT/.talk-quiet" ] && [ "$(cat "$ROOT/.talk-quiet" 2>/dev/null)" = "1" ]; then
  SOUND="quiet"; SOUND_DIRTY=1    # remembered from the last talk (t-toggle/--quiet)
fi
for arg in "$@"; do
  case "$arg" in
    check|--check) MODE="check"; VERBOSE=1 ;;
    -v|--verbose) VERBOSE=1 ;;
    --lang=*) MENU_LANG="${arg#--lang=}" ;;
    --lang) fail "--lang needs a value: --lang=en or --lang=sv" ;;
    1|2|3|4) MODE="direct-$arg" ;;
    *) fail "Unknown argument: $arg (use: check, -v, --lang=en|sv, 1, 2, 3, 4)" ;;
  esac
done
case "$MENU_LANG" in en|sv) ;; *) fail "--lang must be en or sv" ;; esac
if [ -f "$ROOT/.menu-lang" ] && ! printf '%s' "$*" | grep -q -- "--lang"; then
  remembered="$(cat "$ROOT/.menu-lang" 2>/dev/null)"
  case "$remembered" in en|sv) MENU_LANG="$remembered" ;; esac
fi
# The call follows the menu language (Holdmate runs fully in English or Swedish).
export TALK_CALL_LANG="$MENU_LANG"

BOARD_DIR="$ROOT/ui/board"
BOARD_LOG="/tmp/holdmate-board.log"
VOLUME_FILE="$ROOT/.talk-volume"
PORT="${PORT:-5173}"
URL="http://localhost:$PORT"
STARTED_BY_ME=0
SERVER_PID=""

[ "$VERBOSE" = 1 ] && title "Holdmate ($MODE)"

vstep "Preflight"
vwhat "Check node, board files and whether the server already runs."
for tool in node npm curl; do
  command -v "$tool" >/dev/null 2>&1 || fail "$tool is missing (brew install $tool)"
done
vok "tools: node, npm, curl"
[ -f "$BOARD_DIR/package.json" ] || fail "Board not found: $BOARD_DIR"
if [ -d "$BOARD_DIR/node_modules" ]; then
  vok "board deps installed"
else
  if [ "$MODE" = "check" ]; then
    fail "board deps missing (run without check to install them)"
  fi
  vrun "npm ci --prefix $BOARD_DIR"
  npm ci --prefix "$BOARD_DIR" || fail "Could not install board deps"
  [ -d "$BOARD_DIR/node_modules" ] || fail "node_modules still missing after install"
  vok "board deps installed"
fi
if [ "$MODE" = "check" ]; then
  step "Python env"
  what "Create .venv with pytest so the test suite runs keyless."
  if [ -x "$ROOT/.venv/bin/python" ] \
    && "$ROOT/.venv/bin/python" -m pytest --version >/dev/null 2>&1; then
    ok "venv ready: .venv with pytest"
  else
    command -v python3 >/dev/null 2>&1 \
      || fail "python3 is missing (brew install python)"
    run "python3 -m venv $ROOT/.venv"
    python3 -m venv "$ROOT/.venv" \
      || fail "Could not create .venv (macOS: brew install python)"
    run "$ROOT/.venv/bin/pip install pytest"
    "$ROOT/.venv/bin/pip" install -q pytest \
      || fail "Could not install pytest (need network for PyPI)"
    "$ROOT/.venv/bin/python" -m pytest --version >/dev/null 2>&1 \
      || fail "pytest still missing after install"
    ok "venv ready: .venv with pytest"
  fi
fi
if curl -sf -o /dev/null --max-time 2 "$URL"; then
  vok "board server already up: $URL"
else
  vinfo "board server not running (choice 1 starts it)"
fi

server_up() {
  curl -sf -o /dev/null --max-time 2 "$URL" 2>/dev/null
}

refresh_url() {
  # vite drifts to 5174+ when the port is taken; follow the real URL from the log
  _found="$(grep -o 'http://localhost:[0-9][0-9]*' "$BOARD_LOG" 2>/dev/null | head -1)"
  [ -n "$_found" ] && URL="$_found"
}

start_server() {
  if server_up; then
    ok "reusing running server: $URL"
    return 0
  fi
  run "npm run dev --prefix ui/board (log: $BOARD_LOG)"
  npm run dev --prefix "$BOARD_DIR" > "$BOARD_LOG" 2>&1 &
  SERVER_PID=$!
  STARTED_BY_ME=1
  _waited=0
  while [ "$_waited" -lt 25 ]; do
    refresh_url
    if server_up; then
      ok "board up: $URL"
      return 0
    fi
    sleep 1
    _waited=$((_waited + 1))
  done
  fail "board did not answer at $URL (see $BOARD_LOG)"
}

stop_server() {
  if [ "$STARTED_BY_ME" = "1" ] && [ -n "$SERVER_PID" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
    info "board server stopped"
  fi
}

open_board() {
  if command -v open >/dev/null 2>&1; then
    open "$URL"
    ok "$(T opened) $URL $(T in_browser)"
  else
    info "$(T open_this) $(T in_browser): $URL"
  fi
}

open_link() { # $1 = url
  if command -v open >/dev/null 2>&1; then
    open "$1"
    ok "$(T opened) $1 $(T in_browser)"
  else
    info "$(T open_this) $(T in_browser): $1"
  fi
}

github_menu() {
  GH="https://github.com/kizouker/adaptive-IVR-agent"
  PAGES="https://kizouker.github.io/adaptive-IVR-agent/"
  while true; do
    wintitle "github"
    title "$(T gh_title)"
    choice="$(choose \
      "$(T gh_repo)" \
      "$(T gh_site)" \
      "$(T gh_pulls)" \
      "$(T gh_issues)" \
      "$(T gh_actions)" \
      "$(T back)")"
    case "$choice" in
      1) open_link "$GH" ;;
      2) open_link "$PAGES" ;;
      3) open_link "$GH/pulls" ;;
      4) open_link "$GH/issues" ;;
      5) open_link "$GH/actions" ;;
      6|q|Q|b|B) return 0 ;;
      *) pickmsg "1-6" ;;
    esac
  done
}

cleanup() {
  tput cnorm 2>/dev/null || true
  wintitle "done"
  stop_server
}
trap cleanup EXIT INT TERM

can_fancy() {
  [ -t 0 ] && [ -t 2 ] && command -v tput >/dev/null 2>&1 && tput sgr0 >/dev/null 2>&1
}

choose() { # options as args; echoes 1-based index, or "q" on Esc/EOF
  if ! can_fancy; then
    i=1
    for opt in "$@"; do info "[$i] $opt" >&2; i=$((i + 1)); done
    printf '%s' "$(T type_num)" >&2
    read -r line || line="q"
    printf '%s\n' "$line"
    return 0
  fi
  ESC="$(printf '\033')"
  tput civis >&2
  sel=1
  count=$#
  draw() {
    k=1
    width=0
    for opt in "$@"; do [ "${#opt}" -gt "$width" ] && width=${#opt}; done
    for opt in "$@"; do
      printf -v padded "%-${width}s" "$opt"
      if [ "$k" = "$sel" ]; then
        printf '%s%s> [%s] %s%s\n' "$B" "$C" "$k" "$padded" "$X" >&2
      else
        printf '%s  [%s] %s%s\n' "$D" "$k" "$padded" "$X" >&2
      fi
      k=$((k + 1))
    done
  }
  draw "$@"
  while true; do
    IFS= read -rsn1 key || { tput cnorm >&2; printf 'q\n'; return 0; }
    case "$key" in
      "$ESC")
        if read -rsn2 -t 1 rest; then
          if [ "$rest" = "[A" ] && [ "$sel" -gt 1 ]; then sel=$((sel - 1)); fi
          if [ "$rest" = "[B" ] && [ "$sel" -lt "$count" ]; then sel=$((sel + 1)); fi
        else
          tput cnorm >&2; printf 'q\n'; return 0
        fi
        ;;
      "")
        tput cnorm >&2; printf '%s\n' "$sel"; return 0
        ;;
      [1-9])
        if [ "$key" -le "$count" ]; then
          tput cnorm >&2; printf '%s\n' "$key"; return 0
        fi
        ;;
      q|Q)
        tput cnorm >&2; printf 'q\n'; return 0
        ;;
    esac
    tput cuu "$count" >&2
    draw "$@"
  done
}

talk_sound() {
  # Talk with the menu sound choice (speakers/AirPods/quiet) + extra args.
  case "$SOUND" in
    airpods) "$HERE/talk.sh" --airpods "$@" ;;
    quiet) "$HERE/talk.sh" --quiet "$@" ;;
    *) "$HERE/talk.sh" "$@" ;;
  esac
}

talk_volume() { # talk level (0.7 unless remembered in .talk-volume)
  if [ -f "$VOLUME_FILE" ] && grep -Eq '^(0\.[0-9]+|[1-3](\.[0-9]+)?|4(\.0+)?)$' "$VOLUME_FILE"; then
    cat "$VOLUME_FILE"
  else
    printf '0.7'
  fi
}

volume_menu_step() { # $1 = +0.2|-0.2 (same clamp as talk.sh)
  _v="$(talk_volume)"
  _v="$(LC_ALL=C awk -v v="$_v" -v d="$1" 'BEGIN { n = v + d; if (n < 0.1) n = 0.1; if (n > 4) n = 4; printf "%.1f", n }')"
  printf '%s' "$_v" > "$VOLUME_FILE"
  info "$(T vol_word) $_v $(T vol_used)"
}

output_menu() {
  while true; do
    title "$(T out_title) $(sound_label))"
    DEVS=""
    if command -v SwitchAudioSource >/dev/null 2>&1; then
      DEVS="$(SwitchAudioSource -a -t output 2>/dev/null | grep -v '^\s*$')"
    fi
    if [ -z "$DEVS" ]; then
      choice="$(choose "$(T speakers)" "AirPods" "$(T back)")"
      case "$choice" in
        1) SOUND="speakers"; SOUND_DIRTY=1; rm -f "$ROOT/.talk-output"; info "$(T snd_word): $(sound_label)"; return 0 ;;
        2) SOUND="airpods"; SOUND_DIRTY=1; rm -f "$ROOT/.talk-output"; info "$(T snd_word): AirPods"; return 0 ;;
        *) return 0 ;;
      esac
    fi
    OPTS=()
    while IFS= read -r dev; do [ -n "$dev" ] && OPTS+=("$dev"); done <<EOF
$DEVS
EOF
    OPTS+=("$(T auto_pick)" "$(T back)")
    choice="$(choose "${OPTS[@]}")"
    case "$choice" in
      q|Q|b|B) return 0 ;;
      '' | *[!0-9]*) pickmsg "1-${#OPTS[@]}"; continue ;;
    esac
    if [ "$choice" -ge 1 ] && [ "$choice" -le "${#OPTS[@]}" ]; then
      picked="${OPTS[$((choice - 1))]}"
      if [ "$picked" = "$(T back)" ]; then return 0; fi
      if [ "$picked" = "$(T auto_pick)" ]; then
        rm -f "$ROOT/.talk-output"; SOUND_DIRTY=0
        info "$(T auto_on)"
      else
        printf '%s' "$picked" > "$ROOT/.talk-output"; SOUND_DIRTY=1
        case "$picked" in
          *[Aa]ir[Pp]ods*) SOUND="airpods" ;;
          *) SOUND="speakers" ;;
        esac
        info "$(T snd_word): $picked"
      fi
      return 0
    fi
    pickmsg "1-${#OPTS[@]}"
  done
}

volume_menu() {
  while true; do
    title "$(T vol_title) $(talk_volume), 0.1-4.0)"
    choice="$(choose \
      "$(T louder)" \
      "$(T quieter)" \
      "$(T back)")"
    case "$choice" in
      1) volume_menu_step +0.2 ;;
      2) volume_menu_step -0.2 ;;
      3|q|Q|b|B) return 0 ;;
      *) pickmsg "1-3" ;;
    esac
  done
}

sound_menu() {
  while true; do
    wintitle "sound"
    if [ "$SOUND" = "quiet" ]; then QUIET_STATE="$(T on)"; else QUIET_STATE="$(T off)"; fi
    title "$(T snd_title) $(sound_label), $(T vol_word) $(talk_volume))"
    choice="$(choose \
      "$(T snd_output) $(sound_label) $(T m_change)" \
      "$(T snd_volume) $(talk_volume) $(T m_change)" \
      "$(T snd_quiet) $QUIET_STATE $(T m_change)" \
      "$(T back)")"
    case "$choice" in
      1) output_menu ;;
      2) volume_menu ;;
      3) if [ "$SOUND" = "quiet" ]; then SOUND="speakers"; else SOUND="quiet"; fi
        SOUND_DIRTY=1; info "$(T snd_word): $(sound_label)" ;;
      4|q|Q|b|B) return 0 ;;
      *) pickmsg "1-4" ;;
    esac
  done
}

run_all() {
  step "$(T step_board)"
  wintitle "board + talk"
  what "$(T what_board)"
  start_server
  open_board
  talk_sound
}

pick_persona() { # arrow-pick a persona; echoes its id, or "q" to go back
  MAP="$(PYTHONPATH="$ROOT/src" python3 -c "
import json, sys
raw = json.load(open('$ROOT/data/role-phrasebooks.json'))
for r in raw['roles']:
    print(r['id'] + '|' + r['label'])
")" || fail "Could not read personas"
  IDS=()
  OPTS=()
  while IFS='|' read -r pid plabel; do
    [ -n "$pid" ] || continue
    IDS+=("$pid")
    OPTS+=("$plabel")
  done <<EOF
$MAP
EOF
  OPTS+=("$(T back)")
  sel="$(choose "${OPTS[@]}")"
  case "$sel" in
    q|Q) printf 'q\n'; return 0 ;;
  esac
  case "$sel" in
    '' | *[!0-9]*) printf 'q\n'; return 0 ;;
  esac
  if [ "$sel" -ge 1 ] && [ "$sel" -le "${#IDS[@]}" ]; then
    printf '%s\n' "${IDS[$((sel - 1))]}"
  else
    printf 'q\n'
  fi
}

talk_menu() {
  while true; do
    wintitle "talk options"
    title "$(T talk_title)"
    choice="$(choose \
      "$(T t_talk)" \
      "$(T t_airpods)" \
      "$(T t_check)" \
      "$(T t_persona)" \
      "$(T t_quiet)" \
      "$(T back)")"
    case "$choice" in
      1) talk_sound; return 0 ;;
      2) "$HERE/talk.sh" --airpods; return 0 ;;
      3) "$HERE/talk.sh" check; return 0 ;;
      4)
        persona="$(pick_persona)"
        if [ -n "$persona" ] && [ "$persona" != "q" ]; then
          talk_sound --as "$persona"; return 0
        fi
        ;;
      5) "$HERE/talk.sh" --quiet; return 0 ;;
      6|q|Q|b|B) return 0 ;;
      *) pickmsg "1-6" ;;
    esac
  done
}

page() { # stdin pager: one screen, space = more, q quits (stays put)
  if command -v less >/dev/null 2>&1; then less -RX; else cat; fi
}

lessons_stopped() { # $1 = producer rc; an INT stop was already noted
  trap - INT
  if [ "${LESSON_STOP:-0}" = 1 ]; then
    info "$(T stopped)"
  elif [ "${1:-0}" != 0 ]; then
    warn "$(T ended)"
  fi
  return 0
}

lessons_menu() {
  while true; do
    wintitle "lessons"
    title "$(T lsn_title)"
    choice="$(choose \
      "$(T lsn_silent)" \
      "$(T lsn_spoken)" \
      "$(T lsn_one)" \
      "$(T back)")"
    case "$choice" in
      1) trap 'LESSON_STOP=1' INT; LESSON_STOP=0
        HOLDEMATE_COLOR=1 "$HERE/holdmate-call.sh" --all 2>&1 | page
        lessons_stopped "${PIPESTATUS[0]}"
        return 0
        ;;
      2) trap 'LESSON_STOP=1' INT; LESSON_STOP=0
        "$HERE/holdmate-call.sh" --all --speak
        lessons_stopped "$?"
        return 0
        ;;
      3)
        persona="$(pick_persona)"
        if [ -n "$persona" ] && [ "$persona" != "q" ]; then
          trap 'LESSON_STOP=1' INT; LESSON_STOP=0
          "$HERE/holdmate-call.sh" --as "$persona" --speak
          lessons_stopped "$?"
          return 0
        fi
        ;;
      4|q|Q|b|B) return 0 ;;
      *) pickmsg "1-4" ;;
    esac
  done
}

misc_menu() {
  while true; do
    wintitle "misc"
    title "$(T misc_title)"
    choice="$(choose \
      "$(T teach)" \
      "$(T back)")"
    case "$choice" in
      1) info "$(T teach_off)" ;;
      2|q|Q|b|B) return 0 ;;
      *) pickmsg "1-2" ;;
    esac
  done
}

if [ "$MODE" = "check" ]; then
  run "sh/talk.sh check"
  "$HERE/talk.sh" check || fail "talk check failed"
  run "sh/holdmate-call.sh check"
  "$HERE/holdmate-call.sh" check || fail "holdmate-call check failed"
  title "Check only: nothing changed"
  exit 0
fi

case "$MODE" in
  direct-1) run_all; exit 0 ;;
  direct-2) "$HERE/talk.sh"; exit 0 ;;
  direct-3) info "$(T teach_off)"; exit 0 ;;
  direct-4) "$HERE/holdmate-call.sh"; exit 0 ;;
esac

banner() { # glowing HOLDMATE + Diesel the supervisor cat (#189)
  printf '%s%s%s\n' "$B" "$C" ' _   _  ___  _     ____  __  __    _  _____ _____'
  printf '%s%s%s\n' "$B" "$C" '| | | |/ _ \| |   |  _ \|  \/  |  / \|_   _| ____|'
  printf '%s%s%s\n' "$B" "$C" '| |_| | | | | |   | | | | |\/| | / _ \ | | |  _|'
  printf '%s%s%s\n' "$B" "$C" '|  _  | |_| | |___| |_| | |  | |/ ___ \| | | |___'
  printf '%s%s%s\n' "$B" "$C" '|_| |_|\___/|_____|____/|_|  |_/_/   \_\_| |_____|'
  printf '%s%s%s\n' "$D" '' "   $(T tagline)"
  printf '%s%s%s\n' "$D" '' "   board: $URL"
  printf '%s%s%s\n' "$Y" '' '   /\_/\  Diesel supervises'
  printf '%s%s%s\n' "$Y" '' '  ( o.o )'
  printf '%s%s%s\n' "$Y" '' '   > ^ <'
  printf '%s' "$X"
}
while true; do
  clear
  banner
  sync_sound
  wintitle "menu"
  title "$(T menu_title)"
  choice="$(choose \
    "$(T m_board)" \
    "$(T m_talk)" \
    "$(T m_misc)" \
    "$(T m_lessons)" \
    "$(T m_sound): $(sound_label) $(T m_change)" \
    "$(T m_github)" \
    "$(T m_lang)" \
    "$(T m_quit)")"
  case "$choice" in
    1) run_all ;;
    2) talk_menu ;;
    3) misc_menu ;;
    4) lessons_menu ;;
    5) sound_menu ;;
    6) github_menu ;;
    7) if [ "$MENU_LANG" = "sv" ]; then MENU_LANG="en"; else MENU_LANG="sv"; fi
       export TALK_CALL_LANG="$MENU_LANG"
       printf '%s' "$MENU_LANG" > "$ROOT/.menu-lang" ;;
    8|q|Q) title "$(T bye)"; exit 0 ;;
    *) pickmsg "1-8" ;;
  esac
done
