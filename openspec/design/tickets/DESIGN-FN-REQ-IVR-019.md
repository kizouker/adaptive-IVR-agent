# DESIGN-FN-REQ-IVR-019: Any phone line

- REQ ticket: [`### FN-REQ-IVR-019 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/assisted-calling/spec.md`](../../specs/assisted-calling/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`map, knowledge, explorer`)
- Priority: post (after hackathon)

## New or changed parts

- CHANGED: per-line files `data/maps/<line>.json`; `explorer` takes a line parameter. Same train-map-call loop.

## Tests

- Unit: two lines keep separate maps.
- Client-style: newly trained line supports an assisted call.
- Integration: full per-line loop on a second script.
