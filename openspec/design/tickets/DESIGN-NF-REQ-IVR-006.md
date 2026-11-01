# DESIGN-NF-REQ-IVR-006: Real-system experiments stay harmless

- REQ ticket: [`### NF-REQ-IVR-006 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/safety/spec.md`](../../specs/safety/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`guard`), D9
- Priority: always (when real-line work starts)

## New or changed parts

- CHANGED `guard`: experiment-plan review – a plan that can reach a human agent or disrupt service is rejected; call count within the approved limit.

## Tests

- Unit: agent-reaching plan → rejected; over-limit run → refused.
- Client-style: plan review passes only for harmless plans.
