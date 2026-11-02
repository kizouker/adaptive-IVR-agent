# Release notes (next) — device day

Target tag: `v0.3.0` (last tag `v0.2.0`). Branch: `batch/night-pocs` via PR #147 (+ #142, #56).
Date drafted: 2026-11-02. Status: DRAFT — do not tag until Rickard approves merge.

## Highlights

- iPhone + Watch LAN queue (#146, #153, #100): SwiftUI ticket app polls the
  board over LAN (`.local` URL, 5s), with debug UI and install cheatsheet
  (`docs/iphone-install-cheatsheet.md`). watchOS companion co-designed from
  day one: same ticket model, big glanceable queue place.
- Widget N/A state (#144): macOS floating queue widget never goes blank —
  shows `N/A` + reason (board unreachable / no place) instead of `-`.
- Queue demo (#100): `sh/demo-queue.sh` runs one lesson round to the queue,
  bakes the board, and shows the places iPhone/Watch/widget display.
  `sh/demo-queue.sh check` previews without changing anything.
- Spark live wiring (#145, #129): intent ladder (`intent.py`) wired into the
  live loop (`holdmate.py`); eval baseline rescue 2/3, abstain 10/10, exact 3/3.
- Video script (#132): `docs/video-script-draft.md` — 3-min submission script
  (problem / live demo / tech / next steps).
- Also in the train: caller checklists per persona (#143), 46elks client prep
  + HIL design (#131), CLI round 2 mic/busy/survey (#138–#141, PR #142),
  board wording/keypad/history/maze batch (PR #56, #137).

## Release gates (2026-11-02, working tree on batch/night-pocs @ 2582d9f + uncommitted)

- `PYTHONPATH=src pytest -q` (brew pytest 9.2.0): PASS — 190 passed, 2 skipped.
- `npm --prefix ui/board run build` (vite 5.4.21): PASS — built in ~1s.
- CI on PR #147 / #142 / #56: all checks + CodeQL pass.
- Known red: Dependabot PRs #148/#149 (vite 8 bump) fail build — do NOT merge;
  close or rebase after release.

## Merge + tag commands (need Rickard's explicit word — NOT run)

```bash
git checkout main && git pull
gh pr merge 56 --merge   # board words (oldest first)
gh pr merge 142 --merge  # CLI round 2
gh pr merge 147 --merge  # night PoCs + device day
git pull
git tag -a v0.3.0 -m "Device day: iPhone+Watch LAN queue, widget N/A, queue demo, Spark wiring, video script"
git push origin v0.3.0
gh release create v0.3.0 --title "v0.3.0 device day" --notes-file docs/release-notes-next.md
```

After merge: close the built-but-unmerged issues — Release column #86–#88, #93,
#96, #98, #102, #107–#109, #111, #113, #118, #119, #127, #128 (16; #8, #9, #44
already closed in triage as done-on-main) plus Ready column #138–#141, #143 —
or say the word and the agent closes them with per-issue comments.
