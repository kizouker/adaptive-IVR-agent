# DESIGN-FN-REQ-IVR-027: Probe recovery behaviour

- REQ ticket: [`### FN-REQ-IVR-027 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/exploration/spec.md`](../../specs/exploration/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`explorer, map`)
- Priority: post (after hackathon)

## New or changed parts

- CHANGED `explorer`: probe plan – no-input vs no-match, correction recovery, loops/dead ends/fallbacks.
- CHANGED `map`: marks fallback paths, loops and dead ends.

## Tests

- Unit: probe matrix recorded per prompt.
- Client-style: scripted probe run on the practice robot.
- Integration: robot → explorer → map fallback paths.
