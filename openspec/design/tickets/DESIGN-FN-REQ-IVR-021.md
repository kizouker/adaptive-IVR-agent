# DESIGN-FN-REQ-IVR-021: Real calls with the caller present

- REQ ticket: [`### FN-REQ-IVR-021 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/real-line-calling/spec.md`](../../specs/real-line-calling/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`line, guard, voice`), D4, D9
- Priority: future (after hackathon)

## New or changed parts

- NEW `line.RealLineAdapter`: phone-service API (46elks is an option, OQ-15) behind the `line` interface.
- CHANGED `guard`: real-line budget check before every call (NF-REQ-IVR-003).

## Tests

- Unit: adapter maps speak/listen (mock service).
- Client-style: scripted call against the mock.
- No CI integration test against the real line – manual checklist: user present + disclosure + user identity check.
