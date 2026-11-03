# What

One or two sentences: what changes, and which slice (v1…v5) it belongs to.

## Så testar du (Rickard)

Concrete commands + what good looks like. No PR without this section filled.

## REQ links

- Design ticket(s): `openspec/design/tickets/DESIGN-<REQ-ID>.md`
- Requirement ticket(s): `### <REQ-ID>` in `openspec/tickets.md`

## Checks

- [ ] `pytest -q` green
- [ ] `./sh/check-reqs.sh` green
- [ ] No hardcoded literals in logic (constants + data structures)
- [ ] No personal data in recordings, logs or demo (NF-REQ-IVR-002)
- [ ] Tests only touch the practice robot (NF-REQ-IVR-003)
