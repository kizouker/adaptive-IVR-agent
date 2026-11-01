# DESIGN-FN-REQ-IVR-005: Menu map with position

- REQ ticket: [`### FN-REQ-IVR-005 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/menu-map/spec.md`](../../specs/menu-map/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`map, steps`), D3
- Priority: v3 (Sat 31 Oct)

## New or changed parts

- NEW `map.py`: build states + transitions from step files; state key = normalized prompt text (Assumption A1, OQ-18 open).
- NEW: position marker `*` on the current state; text rendering of the map.

## Tests

- Unit: steps → nodes/edges; `*` sits on the right step.
- Client-style: print the map of a recorded run.
- Integration: steps → map; position follows the practice robot.
