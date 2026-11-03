# v0.4.2 "amiga" — DRAFT release notes (2026-11-04)

> **DRAFT — do not treat as released.** Nothing here is merged to a release
> branch and nothing is tagged. Milestone:
> https://github.com/kizouker/adaptive-IVR-agent/milestone/12
> (freeze Wed Nov 4 9:00 PM EST = Thu Nov 5 03:00 CET).
> This file lives on branch `release-notes-draft` only.
> Previous release: `v0.3.4`.

## Merged since v0.3.4

- **#212 — Spark live: muse-spark-1.3 + conf gate + eval numbers (#204)**
  (merged 2026-11-03, `204-spark-live` → main). First real Muse Spark run
  wired into the eval: default model `muse-spark-1.3`, base URL
  `https://api.meta.ai/v1`, 20 s timeout (30 s + `SPARK_TIMEOUT` override
  after review), 0.8 min-confidence gate, hardened prompt, temperature 0.
  Closes #204; covers #211 code items 1/2/4.
- **#215 — Clean-clone check: board deps + venv bootstrap (partial #206)**
  (merged 2026-11-03, `206-clean-clone-fix` → main). `check` now installs
  board deps and bootstraps the venv, so a keyless fresh clone gets green
  pytest. Partial: #206 stays open (NFR-006 box unticked), talk.sh audio
  gap split out as #213.

## Proposed for v0.4.2 (open PRs, unmerged at draft time)

| PR | Branch | Ticket(s) | What |
|----|--------|-----------|------|
| #217 | `205-spark-talk-fallback` | #205 | Spark fallback in talk loop: opt-in `--spark` flag, one normalizer call per word-step miss, "Muse Spark ▸ word conf" board badge. Keyless runs unaffected. |
| #218 | `208-209-deps-prov` | #208, #209 | Menu deps (`rich` + `simple-term-menu`) declared in pyproject; intent tests redirected to tmp provenance (no more `x.test` rows in the real log). |
| #219 | `207-readme-refresh` | #207, #211 (docs) | README refresh: true test count, v0.3.4, honest Meta text, `MODEL_API_KEY` export docs (#211 item 5). |
| #220 | `214-prior-work` | #214 | Prior-work note in README: what existed pre-hackathon (3 commits, Git lab) and that it is unused. Jury transparency. |
| #221 | `effort-levels` | #211 (code) | Reasoning effort medium by default in Spark calls; `SPARK_EFFORT`/`MODEL_API_EFFORT` or `--effort high` override. Live-verified. |

## Features (amiga judging-prep)

- Meta visible: live Muse Spark intent normalization (opt-in) + A/B eval
  harness (`eval/llm_intent_eval.py --live`), keyless sim by default.
- Talk loop Spark fallback + board badge (#205, via #217 when merged).
- Clean-clone keyless path: board deps + venv bootstrap (#206 partial,
  via #215).
- Provenance evidence: real `api.meta.ai` rows with non-zero latency in
  `data/provenance.jsonl`; committed sample
  `docs/evals/spark-live-provenance-2026-11-03.jsonl`.
- Docs for the jury: README refresh, prior-work note, `MODEL_API_KEY`
  setup (via #219/#220 when merged).

## Test evidence

| Check | Result | Source |
|-------|--------|--------|
| Spark live eval `--live` | rescue 3/3, abstain 9–10/10, exact 3/3, SAFETY OK; p95 ~13–20 s/call | `docs/evals/spark-live-2026-11-03.md` (#204) |
| Focused pytest (#212) | 17 passed (`test_intent.py` + `test_secrets.py`) | PR #212 |
| Clean-clone keyless pytest (#215) | 221 passed + 2 (skipped/xfail) in /tmp clone | PR #215 |
| Autoscore heuristic (unofficial) | 7.2 / 10 | `docs/evals/autoscore-2026-11-03.md` |
| Open PRs #217–#221 | Per-PR "Så testar du" steps; CI status to confirm at merge time | PR bodies |

## Known gaps (must resolve or accept before freeze)

- **#210 — 9 deleted files under `data/video/`** (holdmate-v1.mp4,
  narration mp3s, IMG_5667.MOV…). Needs Rickard's call: restore or
  deliberately commit the deletion. Undecided at draft time.
- **#213 — `talk.sh check` hard-fails without audio devices.**
  Blocks #206/NFR-006 on any machine without the Mac aggregate device.
  Fix: warn + skip (exit 0), still fail loudly on broken devices.
- **#216 — 11 Linux test failures in Docker** (likely macOS-only
  talk tests). Judges may run Linux containers: pass, skip cleanly with
  reason, or document as macOS-only before freeze.
- **Video v2 not recorded.** Attempt 1 draft exists
  (https://youtu.be/6KtzT4xfa5k, unlisted, v1); final must follow
  `docs/video-script-draft.md` + `docs/video-plan.md` (≤ 3:00, provenance
  line in first 10 s, 80%+ live product, Meta calls visible, English
  audio + captions, NFR-001…005).
- **X post TBD** (#174): post video on X before Nov 4, paste URL into
  `docs/submission-draft.md`. Scored on Likes + Reposts + Comments.
- **NFR-006 box unticked** in `docs/submission-draft.md` (#206 open).
- **#211 remaining**: README export step lands via #219; verify all model
  calls read `MODEL_API_KEY` at runtime with no key in logs/Git.
- **Dependabot vite 8** (#148/#149): known red, do NOT merge.

## Milestone tickets

Milestone v0.4.2 amiga: 1 closed (#204), 10 open (#205–#211, #213, #214,
#216). See https://github.com/kizouker/adaptive-IVR-agent/milestone/12

## To finalize

1. Merge or drop #217–#221 (record decision per PR).
2. Close or accept #210, #213, #216 + video v2 + X post.
3. Re-run gates on main (`pytest -q`, board build, `./sh/check-reqs.sh`),
   update this file with final numbers.
4. Rename to release notes final, merge, tag `v0.4.2` — only after freeze
   checklist in `docs/submission-draft.md` is green.
