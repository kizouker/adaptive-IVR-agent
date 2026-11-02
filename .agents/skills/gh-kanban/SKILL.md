---
name: gh-kanban
description: Show the repo's GitHub Project kanban board inline in chat, grouped by Status, without opening a browser.
---

# Show Kanban Inline

Use when Rickard asks to see the board, the kanban, or ticket columns
("visa boarden", "kanbanboarden", "what is in Ready").

Project: user `kizouker`, project number `40`
("Meta Hackathon 2026 - Adaptive IVR-Agent").
Board truth is the `Status` field (Backlog/Ready/Done/Release), not labels.

Run exactly this and paste the compact result (no truncation of Ready/Done):

```sh
gh project item-list 40 --owner kizouker --format json --limit 150 | python3 -c "
import json, sys
d = json.load(sys.stdin)
groups = {}
for it in d.get('items', []):
    st = it.get('status') or 'No status'
    num = (it.get('content') or {}).get('number', '?')
    groups.setdefault(st, []).append(f\"#{num} {it.get('title', '')[:60]}\")
for st in ('Ready', 'Done', 'Backlog', 'Release', 'No status'):
    items = groups.get(st, [])
    if not items and st == 'No status':
        continue
    print(f'== {st} ({len(items)}) ==')
    show = items if st in ('Ready', 'Done') else items[:12]
    print('\n'.join(show) if show else '(empty)')
    if len(items) > len(show):
        print(f'... +{len(items) - len(show)} more')
"
```

Rules: never move or close tickets from this view without his explicit word;
this skill only reads. Keep the reply short: the grouped lists plus one line
for what needs his decision (Ready items awaiting approval).
