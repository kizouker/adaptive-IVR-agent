#!/bin/bash
# Azure auto kill-switch: delete holdmate-rg once past KILL_DATE (#169).
# Safety: only this resource group, only after the date, check mode first.
# Runs on: Rickard's Mac (M4) via cron. Modes: run | check.
# Install: 0 9 * * * /Users/raberg/kod/001_Meta_Hackathon_w44/adaptive-IVR-agent/sh/azure-killswitch.sh >> /tmp/holdmate-kill.log 2>&1
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"

RG="${RG:-holdmate-rg}"
KILL_DATE="${KILL_DATE:-2026-12-03}"

title "Azure kill-switch ($MODE)"

step "Preflight"
what "Azure CLI must answer and the group must exist."
command -v az >/dev/null 2>&1 || fail "az CLI is missing"
az account show >/dev/null 2>&1 || fail "az login expired (re-run az login)"
if az group show --name "$RG" >/dev/null 2>&1; then
  ok "group $RG exists"
else
  ok "group $RG already gone; nothing to do"
  exit 0
fi

step "Date guard"
what "Delete only on or after $KILL_DATE."
TODAY="$(date +%F)"
if [[ "$TODAY" < "$KILL_DATE" ]]; then
  ok "today $TODAY < $KILL_DATE; keeping $RG"
  exit 0
fi
warn "today $TODAY >= $KILL_DATE; $RG is due for deletion"

if [ "$MODE" = "check" ]; then
  title "Check only: nothing deleted"
  ok "would delete $RG now"
  exit 0
fi

step "Delete"
what "Remove the whole group; stops all Azure cost."
az group delete --name "$RG" --yes --no-wait || fail "az group delete failed"
ok "deletion started for $RG"

title "Verdict"
ok "kill-switch holds"
