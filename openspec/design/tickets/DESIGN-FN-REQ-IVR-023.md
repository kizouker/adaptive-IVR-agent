# DESIGN-FN-REQ-IVR-023: FK, union, police

- REQ ticket: [`### FN-REQ-IVR-023 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/more-agencies/spec.md`](../../specs/more-agencies/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`knowledge, explorer, map`)
- Priority: future

## New or changed parts

- NEW: `SEED_WORDS` constants per line from `schemas/IVR-schema.md`; same train-map-call loop as 019. Never 112 (NF-REQ-IVR-005).

## Tests

- Unit per line: seeds load and train a first map.
- Client-style per line: training, mapping, assisted call work.
- Integration per line on that line's script.
