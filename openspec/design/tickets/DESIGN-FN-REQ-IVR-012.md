# DESIGN-FN-REQ-IVR-012: Alert on the Mac near the front

- REQ ticket: [`### FN-REQ-IVR-012 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/queue-alert/spec.md`](../../specs/queue-alert/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`alert, queue`)
- Priority: v2 (Fri 30 Oct)

## New or changed parts

- NEW `alert.notify(n)`: Mac notification via osascript (Assumption A3).
- NEW: `ALERT_AT = 2` threshold constant.

## Tests

- Unit: fires at ≤ 2, silent above (mock the notifier).
- Client-style: queue number 2 → the Mac buzzes.
- Integration: queue → alert chain.
