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

run_all() {
  step "Board + talk"
  what "Start the server, open the page, then talk. Server stops when this ends."
  trap stop_server EXIT INT TERM
  start_server
  open_board
  "$HERE/talk.sh"
}

talk_menu() {
  while true; do
    title "Talk options"
    info "1) talk to Agda"
    info "2) talk with AirPods"
    info "3) sound check only"
    info "4) talk as persona"
    info "b) back"
    printf 'Choose: '
    read -r choice || { echo; exit 0; }
    case "$choice" in
      1) "$HERE/talk.sh"; return 0 ;;
      2) "$HERE/talk.sh" --airpods; return 0 ;;
      3) "$HERE/talk.sh" check; return 0 ;;
      4)
        printf 'Persona id: '
        read -r persona || { echo; exit 0; }
        if [ -z "$persona" ]; then
          warn "type a persona id (see data/role-phrasebooks.json)"
        else
          "$HERE/talk.sh" --as "$persona"; return 0
        fi
        ;;
      b|B) return 0 ;;
      *) warn "pick 1, 2, 3, 4 or b" ;;
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
  title "Holdmate menu"
  info "1) board + talk (start server, open page, talk)"
  info "2) talk options (server already runs)"
  info "3) teach Agda words"
  info "q) quit"
  printf 'Choose: '
  read -r choice || { echo; exit 0; }
  case "$choice" in
    1) run_all ;;
    2) talk_menu ;;
    3) "$HERE/learn-words.sh" ;;
    q|Q) title "Bye"; exit 0 ;;
    *) warn "pick 1, 2, 3 or q" ;;
  esac
done
