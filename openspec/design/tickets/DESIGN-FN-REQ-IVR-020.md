# DESIGN-FN-REQ-IVR-020: Say it is an AI

- REQ ticket: [`### FN-REQ-IVR-020 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/safety/spec.md`](../../specs/safety/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`voice`), D6
- Priority: v5 (Mon 2 Nov)

## New or changed parts

- CHANGED `voice`: `DISCLOSURE_LINE` constant, prepended to every utterance; real-call script uses the same line.

## Tests

- Unit: every `speak()` output contains the disclosure line.
- Client-style: v5 practice run script includes disclosure.
- Integration: voice → line output always discloses.
