# DESIGN-FN-REQ-IVR-029: Tag evidence levels in the map

- REQ ticket: [`### FN-REQ-IVR-029 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/menu-map/spec.md`](../../specs/menu-map/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`map`), D3
- Priority: post (after hackathon)

## New or changed parts

- CHANGED `map`: every entry tagged `observed` / `inferred` / `untested` + source step; counter-evidence revises or rejects. (State identity open – OQ-18.)

## Tests

- Unit: tag transitions; counter-evidence revises, never silently overwrites.
- Client-style: map dump shows tags + sources.
- Integration: explorer observations arrive tagged.
