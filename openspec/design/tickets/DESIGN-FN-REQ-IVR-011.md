# DESIGN-FN-REQ-IVR-011: Find the queue number

- REQ ticket: [`### FN-REQ-IVR-011 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/queue-alert/spec.md`](../../specs/queue-alert/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`queue, ears`), D7
- Priority: v2 (Fri 30 Oct)

## New or changed parts

- NEW `queue.find_number(text)`: pattern table constant with the 3 known phrasings; returns int or None.
- Input text comes from `ears` transcripts.

## Tests

- Unit: each phrasing → 38/12/47; no match → None.
- Client-style: transcript file → queue number.
- Integration: ears transcript → queue number.
