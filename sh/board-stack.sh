#!/bin/bash
# Board stack: infra + tests together (#169). up starts the container
# detached on a free port and waits until healthy; test runs e2e against
# it; status checks container + endpoints; down stops everything.
# The port is remembered between calls.
# Runs on: Rickard's Mac (M4). Run: ./sh/board-stack.sh [up|test|status|down]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-up}"

ROOT="$(cd "$HERE/.." && pwd)"
PORT_FILE="/tmp/holdmate-board.port"

pick_port() {
  for p in 8080 8081 8082 8083 8084 8085 8086 8087 8088 8089 8090; do
    if python3 -c "import socket,sys; sys.exit(0 if socket.socket().connect_ex(('127.0.0.1', $p)) else 1)" 2>/dev/null; then
      printf '%s' "$p"
      return 0
    fi
  done
  return 1
}

title "Board stack ($MODE)"

step "Preflight"
what "Docker and python3 must be ready."
command -v docker >/dev/null 2>&1 || fail "docker CLI is missing (start Docker Desktop)"
docker info >/dev/null 2>&1 || fail "docker daemon is not answering (start Docker Desktop)"
command -v python3 >/dev/null 2>&1 || fail "python3 is missing"
command -v curl >/dev/null 2>&1 || fail "curl is missing"
ok "tools ok"

if [ "$MODE" = "down" ]; then
  step "Stop"
  what "Stop the container and forget the port."
  cd "$ROOT" || fail "cannot cd to $ROOT"
  docker compose down || fail "docker compose down failed"
  rm -f "$PORT_FILE"
  ok "stack stopped"
  exit 0
fi

if [ "$MODE" = "test" ]; then
  step "Target"
  what "Use the remembered port, or BOARD_URL if you set one."
  if [ -n "${BOARD_URL:-}" ]; then
    ok "testing $BOARD_URL"
    cd "$ROOT" || fail "cannot cd to $ROOT"
    BOARD_URL="$BOARD_URL" "$HERE/board-e2e.sh" run
    exit $?
  fi
  [ -f "$PORT_FILE" ] || fail "no remembered port (run ./sh/board-stack.sh up first)"
  PORT="$(cat "$PORT_FILE")"
  ok "testing remembered port $PORT"
  cd "$ROOT" || fail "cannot cd to $ROOT"
  BOARD_URL="http://localhost:$PORT" "$HERE/board-e2e.sh" run
  exit $?
fi

if [ "$MODE" = "status" ]; then
  step "Container"
  what "The board container must exist and run."
  cd "$ROOT" || fail "cannot cd to $ROOT"
  STATE="$(docker compose ps --format '{{.State}}' 2>/dev/null | head -1)"
  [ "$STATE" = "running" ] || fail "container state: ${STATE:-missing} (run ./sh/board-stack.sh up)"
  ok "container running"
  PORT="$(cat "$PORT_FILE" 2>/dev/null || echo 8080)"
  if ! curl -sf --max-time 3 "http://127.0.0.1:$PORT/version.json" >/dev/null 2>&1; then
    warn "remembered port $PORT is silent; scanning 8080-8090"
    PORT=""
    for p in 8080 8081 8082 8083 8084 8085 8086 8087 8088 8089 8090; do
      if curl -sf --max-time 2 "http://127.0.0.1:$p/version.json" >/dev/null 2>&1; then
        PORT="$p"
        break
      fi
    done
    [ -n "$PORT" ] || fail "container runs but no board answers on 8080-8090"
    echo "$PORT" > "$PORT_FILE"
  fi
  ok "board on port $PORT"

  step "Endpoints"
  what "Front page, state, version and volume API must answer."
  for path in "" "board-state.json" "version.json" "api/volume"; do
    curl -sf --max-time 5 "http://127.0.0.1:$PORT/$path" >/dev/null 2>&1 \
      || fail "http://localhost:$PORT/$path does not answer"
  done
  ok "all endpoints answer on http://localhost:$PORT"

  title "Verdict"
  ok "board stack healthy"
  exit 0
fi

if [ "$MODE" != "up" ]; then
  fail "unknown mode: $MODE (use up, test, status or down)"
fi

step "Pick a free port"
what "Try 8080 upward; first free port wins."
PORT="$(pick_port)" || fail "ports 8080-8090 are all busy"
ok "port $PORT"

step "Start detached"
what "Build and start the board in the background."
cd "$ROOT" || fail "cannot cd to $ROOT"
BOARD_PORT="$PORT" docker compose up -d --build || fail "docker compose up failed"
echo "$PORT" > "$PORT_FILE"
ok "container started"

step "Wait until healthy"
what "Poll version.json for up to 60s."
for _ in $(seq 1 30); do
  if curl -sf --max-time 2 "http://127.0.0.1:$PORT/version.json" >/dev/null 2>&1; then
    ok "board healthy on http://localhost:$PORT"
    title "Verdict"
    ok "run ./sh/board-stack.sh test next; stop with down"
    exit 0
  fi
  sleep 2
done
fail "board never became healthy on port $PORT (see docker compose logs)"
