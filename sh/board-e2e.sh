#!/bin/bash
# E2E runner with preflight: verifies the board answers before Playwright (#169).
# Local mode (no BOARD_URL) spins the preview server itself; remote mode probes
# BOARD_URL first and fails with a helpful message instead of socket errors.
# Runs on: Rickard's Mac (M4). Modes: run | check (probe only).
# Run: ./sh/board-e2e.sh [check]   or   BOARD_URL=http://localhost:8080 ./sh/board-e2e.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"

ROOT="$(cd "$HERE/.." && pwd)"
BOARD_URL="${BOARD_URL:-}"

title "Board e2e ($MODE)"

step "Preflight"
what "Node and the board answers (remote) or can start (local)."
command -v npm >/dev/null 2>&1 || fail "npm is missing"
command -v python3 >/dev/null 2>&1 || fail "python3 is missing"
if [ -z "$BOARD_URL" ]; then
  ok "local mode: Playwright starts its own preview server"
else
  PORT="$(printf '%s' "$BOARD_URL" | python3 -c "import sys,urllib.parse; print(urllib.parse.urlparse(sys.stdin.read().strip()).port or '')" 2>/dev/null)"
  [ -n "$PORT" ] || fail "BOARD_URL has no port: $BOARD_URL (example: http://localhost:8080)"
  if python3 -c "import socket,sys; sys.exit(0 if socket.socket().connect_ex(('127.0.0.1', $PORT)) else 1)" 2>/dev/null; then
    fail "nothing listens on port $PORT. Start the board first: ./sh/board-docker.sh (note its port), then BOARD_URL=http://localhost:<port> ./sh/board-e2e.sh"
  fi
  ok "something answers on port $PORT"
fi

if [ "$MODE" = "check" ]; then
  title "Check only: nothing started"
  ok "preflight holds"
  exit 0
fi

step "Run Playwright"
what "Execute the e2e suite against the verified target."
cd "$ROOT" || fail "cannot cd to $ROOT"
if [ -n "$BOARD_URL" ]; then
  BOARD_URL="$BOARD_URL" npm run test:e2e --prefix ui/board
else
  npm run test:e2e --prefix ui/board
fi
