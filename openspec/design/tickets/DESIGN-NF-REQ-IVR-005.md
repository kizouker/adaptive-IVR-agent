# DESIGN-NF-REQ-IVR-005: Never test against 112

- REQ ticket: [`### NF-REQ-IVR-005 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/safety/spec.md`](../../specs/safety/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`guard`), D9
- Priority: always

## New or changed parts

- NEW `guard.DENYLIST` constant including `112`; checked on every dial.

## Tests

- Unit: 112 refused in every dialling path.
- Repo test: 112 never appears among test targets.
