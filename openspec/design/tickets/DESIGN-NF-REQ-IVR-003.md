# DESIGN-NF-REQ-IVR-003: Real-line restraint

- REQ ticket: [`### NF-REQ-IVR-003 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/safety/spec.md`](../../specs/safety/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`guard`), D4, D9
- Priority: always

## New or changed parts

- NEW `guard` real-line counter + budget constant (count open – OQ-13).
- CI rule: tests never import the real-line adapter (practice robot only).

## Tests

- Unit: budget exceeded → call refused.
- Repo test: no real-line import anywhere under `tests/`.
