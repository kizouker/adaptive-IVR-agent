# DESIGN-FN-REQ-IVR-016: Identity-check ping

- REQ ticket: [`### FN-REQ-IVR-016 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/assisted-calling/spec.md`](../../specs/assisted-calling/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`handover`)
- Priority: post (after hackathon)

## New or changed parts

- NEW `handover.ping_identity()`: pings the caller, waits for approval. No code path may approve – assert this.

## Tests

- Unit: ping fires at the identity step; run blocks until approval.
- Client-style: simulated approve → run resumes.
- Safety test: no auto-approve path exists (static check + test).
