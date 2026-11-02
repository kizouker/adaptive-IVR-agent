#!/bin/bash
# 46elks smoke test: place one short test call (default: to your own mobile).
# Runs on: Rickard's Mac (M4). Modes: run (default) | check.
# Env: ELKS_USER, ELKS_PASS (API creds, never printed), ELKS_FROM (your
# 46elks number), ELKS_TEST_TO (callee, or pass as $2). Costs apply per
# started minute - hang up promptly. Never place test calls at night.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"
TO="${2:-${ELKS_TEST_TO:-}}"
FROM="${ELKS_FROM:-}"

[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a
TO="${2:-${ELKS_TEST_TO:-}}"
FROM="${ELKS_FROM:-}"

title "46elks smoke test ($MODE)"
step "Preflight"
what "Credentials present (never shown), numbers valid E.164, cost shown."
[ -n "${ELKS_USER:-}" ] || fail "ELKS_USER missing (put it in $ROOT/.env, never commit)"
[ -n "${ELKS_PASS:-}" ] || fail "ELKS_PASS missing (put it in $ROOT/.env, never commit)"
[ -n "$TO" ] || fail "no callee: pass a number or set ELKS_TEST_TO=+4670..."
[ -n "$FROM" ] || fail "ELKS_FROM missing (your 46elks number in E.164)"
COST="$(PYTHONPATH="$ROOT/src" python3 -c "
from adaptive_ivr_agent.elks import estimate_cost_sek, valid_e164
import sys
ok = valid_e164('$TO') and valid_e164('$FROM')
print(f'{estimate_cost_sek(1):.2f}' if ok else 'BADNUM')
")"
[ "$COST" != "BADNUM" ] || fail "bad E.164 number (want +46...): to=$TO from=$FROM"
ok "numbers valid; ~$COST SEK for the first minute"

[ "$MODE" = "check" ] && {
  title "Check only: no call placed"
  info "would call: $TO from $FROM (recordcall=true)"
  exit 0
}

step "Place call"
what "One test call with recording; hang up promptly to save money."
run "ElksClient.place_call(to, from, recordcall=true)"
CALLID="$(PYTHONPATH="$ROOT/src" python3 -c "
from adaptive_ivr_agent.elks import ElksClient
print(ElksClient().place_call('$TO', '$FROM').get('id', 'NOID'))
")"
[ -n "$CALLID" ] && [ "$CALLID" != "NOID" ] || fail "no call id returned (see output above)"
ok "call placed: $CALLID (answer it, then hang up)"

title "Done — remember to hang up"
