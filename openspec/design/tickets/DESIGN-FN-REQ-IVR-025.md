# DESIGN-FN-REQ-IVR-025: Cases across agencies

- REQ ticket: [`### FN-REQ-IVR-025 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/agency-mcp/spec.md`](../../specs/agency-mcp/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`mcp, handover`), D11
- Priority: future

## New or changed parts

- CHANGED `mcp`: multi-server session (case moves a-kassa → Försäkringskassan).
- CHANGED `handover`: loops the caller in at the key steps.

## Tests

- Unit: case state survives a server switch (mock servers).
- Client-style: cross-agency case handled; caller looped in.
- Integration: two-mock-server flow end-to-end.
