# DESIGN-FN-REQ-IVR-017: Handover when a person answers

- REQ ticket: [`### FN-REQ-IVR-017 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/assisted-calling/spec.md`](../../specs/assisted-calling/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`handover, alert`)
- Priority: post (after hackathon)

## New or changed parts

- CHANGED `handover`: buzz text constant ('You are number 3'); handover-or-joint-call flag.
- CHANGED `alert`: queue-number JSON payload for the web widget. iPhone display excluded.

## Tests

- Unit: widget payload shape {line, number, state}.
- Client-style: person answers → buzz + widget data + handover.
- Integration: queue → alert → handover chain.
