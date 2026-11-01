# DESIGN-FN-REQ-IVR-028: Verify same-state equivalence

- REQ ticket: [`### FN-REQ-IVR-028 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/exploration/spec.md`](../../specs/exploration/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`map, knowledge`)
- Priority: post (after hackathon)

## New or changed parts

- CHANGED `map`: equivalence sets – synonyms, working routes per state, DTMF ≈ speech.
- CHANGED `knowledge`: equivalence hypotheses to confirm or reject.

## Tests

- Unit: equivalent observations merge to one state.
- Client-style: synonym run reaches the same node.
- Integration: map records the equivalence with evidence.
