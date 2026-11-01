# DESIGN-FN-REQ-IVR-009: Try words and fill the map

- REQ ticket: [`### FN-REQ-IVR-009 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/exploration/spec.md`](../../specs/exploration/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`explorer, map, knowledge`), D3
- Priority: v4 (Sun 1 Nov)

## New or changed parts

- NEW `knowledge.py`: target model – candidate words/states (hypotheses, never facts).
- CHANGED `explorer`: after each reply, append steps and add the observation to `map`.

## Tests

- Unit: one observation grows the map by one edge.
- Client-style: explore run; map file is bigger after every call.
- Integration: line → steps → map chain on the practice robot.
