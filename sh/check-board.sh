#!/bin/bash
# Board-server preflight for the iPhone/Watch apps: is board-state.json
# reachable on localhost AND on LAN (.local) with valid JSON?
# Runs on: Rickard's Mac (M4). Modes: run (default) | check (same, read-only).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"

PORT="${PORT:-5173}"
HOST="$(scutil --get LocalHostName 2>/dev/null || hostname -s 2>/dev/null || echo "")"

title "Board preflight ($MODE)"

step "Preflight"
what "Check tools and resolve the LAN hostname before probing anything."
command -v curl >/dev/null 2>&1 || fail "curl is missing"
command -v python3 >/dev/null 2>&1 || fail "python3 is missing"
[ -n "$HOST" ] || fail "could not resolve LAN hostname (scutil/hostname failed)"
ok "tools: curl, python3; LAN host: $HOST.local"

check_url() { # $1 = url, $2 = label; ok on valid JSON, warn + return 1 if not
  _body="$(curl -sf --max-time 4 "$1" 2>/dev/null)" || { warn "$2 unreachable: $1"; return 1; }
  _keys="$(printf '%s' "$_body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(','.join(sorted(d.keys())))" 2>/dev/null)" || { warn "$2 returned bad JSON"; return 1; }
  ok "$2 OK: $1 (keys: $_keys)"
}

step "Local probe"
what "Board must answer on localhost (the page you see in the browser)."
LOCAL_OK=0
check_url "http://localhost:$PORT/board-state.json" "local" && LOCAL_OK=1

step "LAN probe"
what "iPhone/Watch reach the board over LAN (.local); server listens on LAN by config."
LAN_OK=0
check_url "http://$HOST.local:$PORT/board-state.json" "LAN" && LAN_OK=1

title "Verdict"
if [ "$LAN_OK" = 1 ]; then
  ok "devices can reach the board at http://$HOST.local:$PORT"
  exit 0
fi
if [ "$LOCAL_OK" = 1 ]; then
  fail "board answers locally but not on LAN: old server still running — quit the menu (6), then start"
fi
fail "board is down: start"
