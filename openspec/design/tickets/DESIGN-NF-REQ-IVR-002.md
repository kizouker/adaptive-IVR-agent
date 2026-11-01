# DESIGN-NF-REQ-IVR-002: No personal data kept

- REQ ticket: [`### NF-REQ-IVR-002 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/safety/spec.md`](../../specs/safety/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`cutter`), D5, D8
- Priority: always (applies now)

## New or changed parts

- NEW `cutter.cut(wav, staff_at)`: cuts staff audio before storing.
- NEW: PII pattern list (ID numbers, staff names) for a repo/log/demo scan in CI.

## Tests

- Unit: cut removes everything from the staff timestamp on.
- Client-style: record → cut → store; stored file holds no staff audio.
- Integration: CI scan of logs/demos/repo finds none of the three.
