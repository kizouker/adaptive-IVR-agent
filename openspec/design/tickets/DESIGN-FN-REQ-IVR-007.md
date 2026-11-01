# DESIGN-FN-REQ-IVR-007: Reactive robot

- REQ ticket: [`### FN-REQ-IVR-007 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/practice-robot/spec.md`](../../specs/practice-robot/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`robot, line`), D4
- Priority: v4 (Sun 1 Nov)

## New or changed parts

- NEW `line.py`: `speak` / `listen` / `hangup` interface + fake for tests.
- CHANGED `robot`: script tree (prompt → word/key → next), `not-understood` line, exact `ja`/`nej` at confirm.

## Tests

- Unit: known word/key moves on; unknown → not-understood; ja/nej at confirm.
- Client-style: scripted conversation through the `line` interface.
- Integration: explorer → line → robot round-trip.
