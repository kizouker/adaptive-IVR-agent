#!/bin/bash
# Holdmate launcher: board server + talk from one menu, runnable from anywhere.
# Runs on: Rickard's Mac (M4). Modes: menu (default) | check. Direct: 1, 2, 3.
# 1 = start the board server, open the page, and talk. 2 = talk options.
# 3 = teach Agda words. Runs from any folder; paths resolve from this script.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
ROOT="$(cd "$HERE/.." && pwd)"
MODE="menu"
for arg in "$@"; do
  case "$arg" in
    check|--check) MODE="check" ;;
    1|2|3) MODE="direct-$arg" ;;
    *) fail "Unknown argument: $arg (use: check, 1, 2, 3)" ;;
  esac
done

BOARD_DIR="$ROOT/ui/board"
BOARD_LOG="/tmp/holdmate-board.log"
PORT="${PORT:-5173}"
URL="http://localhost:$PORT"
STARTED_BY_ME=0
SERVER_PID=""

title "Holdmate ($MODE)"

step "Preflight"
what "Check node, board files and whether the server already runs."
for tool in node npm curl; do
  command -v "$tool" >/dev/null 2>&1 || fail "$tool is missing (brew install $tool)"
done
ok "tools: node, npm, curl"
[ -f "$BOARD_DIR/package.json" ] || fail "Board not found: $BOARD_DIR"
if [ -d "$BOARD_DIR/node_modules" ]; then
  ok "board deps installed"
else
  if [ "$MODE" = "check" ]; then
    fail "board deps missing (run without check to install them)"
  fi
  run "npm ci --prefix $BOARD_DIR"
  npm ci --prefix "$BOARD_DIR" || fail "Could not install board deps"
  [ -d "$BOARD_DIR/node_modules" ] || fail "node_modules still missing after install"
  ok "board deps installed"
fi
if curl -sf -o /dev/null --max-time 2 "$URL"; then
  ok "board server already up: $URL"
else
  info "board server not running (choice 1 starts it)"
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
    ok "opened $URL in your browser"
  else
    info "open this in your browser: $URL"
  fi
}

cleanup() {
  tput cnorm 2>/dev/null || true
  stop_server
}
trap cleanup EXIT INT TERM

can_fancy() {
  [ -t 0 ] && [ -t 2 ] && command -v tput >/dev/null 2>&1 && tput sgr0 >/dev/null 2>&1
}

choose() { # options as args; echoes 1-based index, or "q" on Esc/EOF
  if ! can_fancy; then
    i=1
    for opt in "$@"; do info "$i) $opt"; i=$((i + 1)); done
    printf 'Type a number: '
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
    for opt in "$@"; do
      if [ "$k" = "$sel" ]; then
        printf '%s> %s%s\n' "$(tput rev)" "$opt" "$(tput sgr0)" >&2
      else
        printf '  %s\n' "$opt" >&2
      fi
      k=$((k + 1))
    done
  }
  draw "$@"
  while true; do
    IFS= read -rsn1 key || { tput cnorm >&2; printf 'q\n'; return 0; }
    case "$key" in
      "$ESC")
        if read -rsn2 -t 0.2 rest; then
          if [ "$rest" = "[A" ] && [ "$sel" -gt 1 ]; then sel=$((sel - 1)); fi
          if [ "$rest" = "[B" ] && [ "$sel" -lt "$count" ]; then sel=$((sel + 1)); fi
        else
          tput cnorm >&2; printf 'q\n'; return 0
        fi
        ;;
      "")
        tput cnorm >&2; printf '%s\n' "$sel"; return 0
        ;;
    esac
    tput cuu "$count" >&2
    draw "$@"
  done
}

run_all() {
  step "Board + talk"
  what "Start the server, open the page, then talk. Server stops when this ends."
  start_server
  open_board
  "$HERE/talk.sh"
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
  OPTS+=("back")
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
    title "Talk options (arrows + Enter, Esc goes back)"
    choice="$(choose \
      "talk to Agda" \
      "talk with AirPods" \
      "sound check only" \
      "talk as persona" \
      "back")"
    case "$choice" in
      1) "$HERE/talk.sh"; return 0 ;;
      2) "$HERE/talk.sh" --airpods; return 0 ;;
      3) "$HERE/talk.sh" check; return 0 ;;
      4)
        persona="$(pick_persona)"
        if [ -n "$persona" ] && [ "$persona" != "q" ]; then
          "$HERE/talk.sh" --as "$persona"; return 0
        fi
        ;;
      5|q|Q|b|B) return 0 ;;
      *) warn "pick with arrows + Enter (or type 1-5)" ;;
    esac
  done
}

if [ "$MODE" = "check" ]; then
  run "sh/talk.sh check"
  "$HERE/talk.sh" check || fail "talk check failed"
  title "Check only: nothing changed"
  exit 0
fi

case "$MODE" in
  direct-1) run_all; exit 0 ;;
  direct-2) "$HERE/talk.sh"; exit 0 ;;
  direct-3) "$HERE/learn-words.sh"; exit 0 ;;
esac

while true; do
  title "Holdmate menu (arrows + Enter, Esc quits)"
  choice="$(choose \
    "board + talk (start server, open page, talk)" \
    "talk options (server already runs)" \
    "teach Agda words" \
    "quit")"
  case "$choice" in
    1) run_all ;;
    2) talk_menu ;;
    3) "$HERE/learn-words.sh" ;;
    4|q|Q) title "Bye"; exit 0 ;;
    *) warn "pick with arrows + Enter (or type 1-4)" ;;
  esac
done
