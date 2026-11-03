#!/bin/bash
# Board over Docker with automatic free-port pick (#169).
# Probes 8080..8090, runs compose on the first free one.
# Runs on: Rickard's Mac (M4). Modes: run | check (check prints, starts nothing).
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

step "Serve the board"
what "Build and start; board lands on the picked port."
cd "$ROOT" || fail "cannot cd to $ROOT"
BOARD_PORT="$PORT" docker compose up --build
