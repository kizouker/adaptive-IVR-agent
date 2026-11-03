#!/bin/bash
# Board over Docker with automatic free-port pick (#169).
# Probes 8080..8090, runs compose on the first free one.
# Runs on: Rickard's Mac (M4). Modes: run | check | test.
# check prints the port and starts nothing; test smoke-tests a running board.
# Run: ./sh/board-docker.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"

ROOT="$(cd "$HERE/.." && pwd)"

title "Board over Docker ($MODE)"

step "Preflight"
what "Docker must answer before probing ports."
command -v docker >/dev/null 2>&1 || fail "docker CLI is missing (start Docker Desktop)"
docker info >/dev/null 2>&1 || fail "docker daemon is not answering (start Docker Desktop)"
command -v python3 >/dev/null 2>&1 || fail "python3 is missing"
ok "docker daemon answers"

step "Pick a free port"
what "Try 8080 upward; first port nobody listens on wins."
PORT=""
for p in 8080 8081 8082 8083 8084 8085 8086 8087 8088 8089 8090; do
  if python3 -c "import socket,sys; sys.exit(0 if socket.socket().connect_ex(('127.0.0.1', $p)) else 1)" 2>/dev/null; then
    PORT="$p"
    break
  fi
done
[ -n "$PORT" ] || fail "ports 8080-8090 are all busy"
if [ "$PORT" = 8080 ]; then ok "port 8080 is free"; else warn "8080 busy, using $PORT instead"; fi

if [ "$MODE" = "check" ]; then
  title "Check only: nothing started"
  ok "would serve the board on http://localhost:$PORT"
  exit 0
fi

if [ "$MODE" = "test" ]; then
  step "Find the running board"
  what "Look for a board answering with version.json on 8080-8090."
  FOUND=""
  for p in 8080 8081 8082 8083 8084 8085 8086 8087 8088 8089 8090; do
    if curl -sf --max-time 2 "http://127.0.0.1:$p/version.json" >/dev/null 2>&1; then
      FOUND="$p"
      break
    fi
  done
  [ -n "$FOUND" ] || fail "no board answering on 8080-8090 (start with ./sh/board-docker.sh)"
  ok "board answers on http://localhost:$FOUND"

  step "Smoke-test the board"
  what "Front page, board state and version must answer with good data."
  curl -sf --max-time 5 "http://127.0.0.1:$FOUND/" | grep -q "Holdmate" || fail "front page missing Holdmate"
  ok "front page serves"
  STATE="$(curl -sf --max-time 5 "http://127.0.0.1:$FOUND/board-state.json")" || fail "board-state.json did not answer"
  printf '%s' "$STATE" | python3 -c "import sys,json; json.load(sys.stdin)" || fail "board-state.json is not valid JSON"
  ok "board-state.json is valid JSON"
  VER="$(curl -sf --max-time 5 "http://127.0.0.1:$FOUND/version.json")" || fail "version.json did not answer"
  printf '%s' "$VER" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('version'), 'no version'" || fail "version.json has no version"
  ok "version.json ok"
  VOL="$(curl -sf --max-time 5 "http://127.0.0.1:$FOUND/api/volume")" || fail "/api/volume did not answer"
  printf '%s' "$VOL" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('volume'), 'no volume'" || fail "/api/volume has no volume"
  ok "/api/volume ok"

  title "Verdict"
  ok "docker board smoke-test holds on port $FOUND"
  exit 0
fi

step "Serve the board"
what "Build and start; board lands on the picked port."
cd "$ROOT" || fail "cannot cd to $ROOT"
BOARD_PORT="$PORT" docker compose up --build
