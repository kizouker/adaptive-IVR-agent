---
name: gh-release-train
description: Run the small-release flow on the GitHub Project board: version + codename, label, milestone, Released column, tag and release.
---

# Release Train

Use when Rickard says new release, release train, "releasa", or names the
next version. Small releases: define scope, work, ship — one at a time.

Project: user `kizouker`, project 40. Repo: kizouker/adaptive-IVR-agent.

## 1. Name it

- Version: next patch/minor from `git tag --sort=creatordate` (ask if unsure).
- Codename: ask Rickard for a category (e.g. his home computers), or pick
  random from the pool below with `shuf -n1`. Format: `vX.Y.Z codename`
  (lowercase, number first). Pool: vic20, spectravideo, c64, amiga500,
  seagate80, c1084s, ibm8080, amiga4000, merlingfx, mbp2013, mbp2019, m1, m4.

## 2. Set up (in this order)

1. Create milestone (open): `gh api repos/.../milestones -f title="vX.Y.Z name"`.
   Record its number. Create label `vX.Y.Z` (color 0E8A16).
2. Assign scoped tickets: `gh issue edit N --add-label vX.Y.Z --milestone
   "vX.Y.Z name"` (use `gh pr edit` for PRs). Milestone flag needs the
   OPEN milestone matched by TITLE (numbers do not resolve).
3. Work, merge to main, verify CI green.
4. Tag + release: `git tag -a vX.Y.Z origin/main`, push tag,
   `gh release create vX.Y.Z --notes-file <notes>`.
5. Move shipped tickets to Status `Released` (item IDs from `gh project
   item-list`), close them with a comment, close the milestone last.

## 3. Gotchas (learned hard)

- NEVER add/rename Status options via `updateProjectV2Field` without first
  snapshotting every item's status to a file — the mutation regenerates
  option IDs and WIPES all values. Restore from the snapshot after.
- `gh issue list` defaults to open only; verify bulk ops with `--state all`.
- Closed milestones cannot receive assignments; reopen, assign, reclose.
- `gh issue edit` fails on PR numbers; route PRs to `gh pr edit`.
- Verify counts after every bulk step; report fails, never silently skip.
