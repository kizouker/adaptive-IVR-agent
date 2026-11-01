# DESIGN-FN-REQ-IVR-013: Queue counts down

- REQ ticket: [`### FN-REQ-IVR-013 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/queue-alert/spec.md`](../../specs/queue-alert/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`queue, alert`)
- Priority: v5 (Mon 2 Nov)

## New or changed parts

- CHANGED `queue`: track the last number across polls; report only on change.
- CHANGED `alert`: expose the current number as display data (for the widget, FN-REQ-IVR-017).

## Tests

- Unit: decreasing polls update; repeats don't re-alert.
- Client-style: simulated countdown 5 → 2 without listening.
- Integration: ears → queue → alert display data.
