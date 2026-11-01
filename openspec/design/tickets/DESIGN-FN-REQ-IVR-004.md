# DESIGN-FN-REQ-IVR-004: Keyword table

- REQ ticket: [`### FN-REQ-IVR-004 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/menu-map/spec.md`](../../specs/menu-map/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`keywords`)
- Priority: v1 (Thu 29 Oct)

## New or changed parts

- `keywords.KeywordTable` exists (v1) – keep two-way lookup.
- NEW: save/load the table as JSON so the explorer (FN-REQ-IVR-008) can read it.

## Tests

- Unit: both directions + `KeyError` on unknown (exists).
- Client-style: want X → say Y; said Y → get X.
- Integration: table persists and reloads for the explorer.
