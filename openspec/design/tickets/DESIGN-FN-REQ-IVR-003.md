# DESIGN-FN-REQ-IVR-003: Save each call as steps

- REQ ticket: [`### FN-REQ-IVR-003 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/menu-map/spec.md`](../../specs/menu-map/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`steps`), D2
- Priority: v1 (Thu 29 Oct)

## New or changed parts

- `steps.Step` / `StepFile` exist (v1) – keep the shape.
- NEW: `STEPS_DIR = data/steps/` constant (Assumption A2).

## Tests

- Unit: save/load round-trip (exists).
- Client-style: one mini-robot run creates one step file.
- Integration: robot run → step file with FN-REQ-IVR-006.
