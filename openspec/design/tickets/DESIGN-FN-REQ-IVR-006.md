# DESIGN-FN-REQ-IVR-006: Mini robot plays three lines

- REQ ticket: [`### FN-REQ-IVR-006 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/practice-robot/spec.md`](../../specs/practice-robot/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`robot, voice, steps`), D6
- Priority: v1 (Thu 29 Oct)

## New or changed parts

- `robot.PracticeRobot` + `mac_say` exist (v1) – keep.
- No changes; this ticket locks the v1 behaviour other tickets build on.

## Tests

- Unit: plays lines through an injected fake speaker (exists).
- Client-style: `run(path)` plays 3 lines, saves 3 steps.
- Integration: robot run → step file with FN-REQ-IVR-003.
