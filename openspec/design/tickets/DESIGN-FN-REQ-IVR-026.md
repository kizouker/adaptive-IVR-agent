# DESIGN-FN-REQ-IVR-026: Wording for your situation

- REQ ticket: [`### FN-REQ-IVR-026 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/situation-guidance/spec.md`](../../specs/situation-guidance/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`guide, keywords`)
- Priority: future (v2)

## New or changed parts

- NEW `guide.wording(situation)`: situation → script, backed by a process-model data file (programme name open – OQ-10).

## Tests

- Unit: sign-up-again situation → the right wording.
- Client-style: situation in → speakable script out.
- Integration: guide → keywords → explorer uses the wording.
