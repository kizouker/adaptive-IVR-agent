# DESIGN-FN-REQ-IVR-015: Two ways to start a call

- REQ ticket: [`### FN-REQ-IVR-015 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/assisted-calling/spec.md`](../../specs/assisted-calling/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`intake`)
- Priority: post (after hackathon)

## New or changed parts

- CHANGED `intake`: chat start (014) + menu-tree + Call start (clicked node id → goal). Both yield the same goal type.

## Tests

- Unit: both starts produce equal goals for the same need.
- Client-style ×2: chat start works; tree-click + Call works.
- Integration: either start → explorer steers as far as it can.
