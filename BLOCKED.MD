# BLOCKED.MD

Log of blocked items. Standing rule from Rickard: when blocked, record it
here (in English), with cause and what is needed to unblock.

## 2026-10-28 — Issue #3 dry test (step 2)

- Status: APPROVED 2026-10-28 — Rickard wrote OK on the issue; gate item
  3 satisfied. Issue stays OPEN during implementation.
- Resolved: Issue #3 now has requirement ID `REQ-001` and four Gherkin
  scenarios tagged `@REQ-001-S01` through `@REQ-001-S04`.
- Note: S05 gap (Done-when item 4 without dedicated scenario) still
  flagged in `docs/process/TEST.MD`; Verifier/design decides proxy or new
  scenario before build.
- Details: GitHub issue #3; `docs/process/TEST.MD` (2026-10-28 re-test section).

## 2026-10-28 — Issue #4 dry test (step 2)

- Status: APPROVED 2026-10-28 — Rickard wrote OK on the issue.
  Verifier re-test mapping remains outstanding. Issue stays OPEN.
- Resolved: Issue #4 now has requirement ID `REQ-002` and five Gherkin
  scenarios tagged `@REQ-002-S01` through `@REQ-002-S05`.
- Remaining cause: Verifier has not yet mapped one test per scenario.
- Needed to unblock: Verifier re-tests per
  `.agents/process/007_TEST.MD` and maps `TC-004-01` ….
- Details: GitHub issue #4; `docs/process/TEST.MD`.

## 2026-10-28 — Issue #4 implementation: gate deviations recorded

- Status: IMPLEMENTED with open gate items (workflow + docs built).
- Deviation 1: no `ROADMAP.md` exists and #4 is not assigned to a sprint
  (gate item 2). Needed: Rickard/PO adds roadmap + sprint.
- Deviation 2: no Gherkin scenarios, REQ IDs, or approval at build time
  (gate item 3). Needed: requirements specialist adds scenarios;
  Rickard approves.
- Deviation 3: e2e verification pending (Done-when item 4). Needed:
  `NTFY_TOPIC` secret set, manual run, test issue opened/closed.
- Details: `.github/workflows/new-issue-notify.yml`, `docs/issue-notify.md`
