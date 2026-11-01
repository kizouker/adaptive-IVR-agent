# DESIGN-FN-REQ-IVR-018: Handover with a clear question

- REQ ticket: [`### FN-REQ-IVR-018 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/assisted-calling/spec.md`](../../specs/assisted-calling/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`intake, handover`)
- Priority: post (after hackathon)

## New or changed parts

- CHANGED `intake`: `summarise(goal, steps)` → one-line question for the handover. (Calm/no-recall check open – OQ-12.)

## Tests

- Unit: goal + steps → single clear question line.
- Client-style: at handover the question is ready.
- Integration: intake summary reaches the handover.
