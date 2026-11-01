# DESIGN-FN-REQ-IVR-010: Reach the queue without a loop

- REQ ticket: [`### FN-REQ-IVR-010 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/exploration/spec.md`](../../specs/exploration/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`explorer`)
- Priority: v4 (Sun 1 Nov)

## New or changed parts

- CHANGED `explorer`: visited-set + loop guard (new word when a state repeats); exact `ja`/`nej` at confirm.
- No new modules; this is the v4 end-to-end behaviour.

## Tests

- Unit: repeated state → different next word (loop guard).
- Client-style (= integration): full run reaches the queue; no yes/no loop, no name trap.
