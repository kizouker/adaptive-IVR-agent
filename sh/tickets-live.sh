#!/bin/bash
# Live ticket board: poll the GitHub Project, show status groups + moves (#193).
# Runs on: Rickard's Mac (M4). Run: ./sh/tickets-live.sh [seconds, default 30]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"

INTERVAL="${1:-30}"
SNAP="/tmp/holdmate-ticket-status.json"

printf '\n%s%s_HOLDMATE live tickets%s (every %ss, Ctrl-C stops)\n' "$B" "$C" "$X" "$INTERVAL"
title "Live tickets"

step "Preflight"
what "gh must reach project 40."
command -v gh >/dev/null 2>&1 || fail "gh is missing"
command -v python3 >/dev/null 2>&1 || fail "python3 is missing"
ok "tools ok"

while true; do
  SNAP="$SNAP" gh project item-list 40 --owner kizouker --format json --limit 150 \
    | python3 -c "
import json, os, sys
snap_path = os.environ['SNAP']
d = json.load(sys.stdin)
now = {}
groups = {}
for it in d.get('items', []):
    st = it.get('status') or 'No status'
    num = (it.get('content') or {}).get('number', '?')
    now[str(num)] = st
    groups.setdefault(st, []).append(f'#{num}')
try:
    prev = json.load(open(snap_path))
except (OSError, ValueError):
    prev = {}
moves = [f'{n}: {prev[n]} -> {st}' for n, st in now.items()
         if n in prev and prev[n] != st]
new = [n for n in now if n not in prev]
print('== moves since last poll ==')
print('\n'.join('MOVE ' + m for m in moves) or '(none)')
if new and prev:
    print('NEW ' + ' '.join(f'#{n}' for n in new))
for st in ('Ready', 'Done', 'Backlog', 'Release', 'No status'):
    items = groups.get(st, [])
    if items or st in ('Ready', 'Done'):
        print(f'== {st} ({len(items)}) == ' + ' '.join(items[:20]))
        if len(items) > 20:
            print(f'   ... +{len(items) - 20} more')
json.dump(now, open(snap_path, 'w'))
" || fail "project poll failed"
  echo "--- next poll in ${INTERVAL}s ($(date +%H:%M:%S)) ---"
  sleep "$INTERVAL"
done
