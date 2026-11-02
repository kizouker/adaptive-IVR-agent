#!/bin/bash
# Keep the Mac awake overnight so agents keep running.
# Runs on: Rickard's Mac (M4). Modes: run (default) | check.
# Lid must stay OPEN (caffeinate cannot stop lid-close sleep); charger in.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"

title "Keep awake ($MODE)"
step "Preflight"
what "Charger connected and lid open; caffeinate present."
command -v caffeinate >/dev/null || fail "caffeinate missing (macOS provides it)"
if pmset -g batt | grep -q "AC Power"; then ok "charger connected"; else fail "connect the charger first"; fi
ok "caffeinate present (lid must stay open)"

[ "$MODE" = "check" ] && {
  title "Check only: nothing started"
  info "would run: caffeinate -i (prevents idle sleep until Ctrl-C)"
  exit 0
}

step "Stay awake"
what "Block idle sleep until you press Ctrl-C. Leave this terminal open."
run "caffeinate -i"
caffeinate -i
