# DESIGN-FN-REQ-IVR-008: Pick words from the keyword table

- REQ ticket: [`### FN-REQ-IVR-008 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/exploration/spec.md`](../../specs/exploration/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`explorer, keywords`)
- Priority: v4 (Sun 1 Nov)

## New or changed parts

- NEW `explorer.choose(state, goal)`: reads `keywords`, returns the word for goal X.
- No robot changes; talks through the `line` interface.

## Tests

- Unit: goal X → table word Y; unknown goal → clean miss (no crash).
- Client-style: at a topic step wanting X, Holdmate says Y.
- Integration: explorer + keywords + practice robot reaches the next state.
