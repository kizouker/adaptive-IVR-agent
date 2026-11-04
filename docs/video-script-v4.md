# Holdmate — 3-minute video script v4 (edit list on real footage)

Builds on [video-script-draft.md](video-script-draft.md) (v3). Pacing follows
the organizers' blueprint in `Judging Workflow.md` §3: 15 s hook, 80 s live,
40 s Meta, 30 s proof, 10 s close, hard stop 2:55.
Voiceover: Rickard, English, recorded over the silent cut. About 150 words per
minute, so each block lists its word budget. Captions = the SAY line, burned in.

Sources: `data/video/shot-NN-start.mov` (screen recordings 2026-11-03),
`data/video/term/*.mp4` (VHS terminal clips, clean clone),
`data/video/phone/*.mp4` (iPhone + Watch, 1920x1080, padded, silent).
In/out points marked ~ are from contact sheets; trim by eye.

## Production

The silent cut of this script is built and ready for voice:
`data/video/cut/silent.mp4` (2:55). How to record the voice, remux and
rebuild: [data/video/cut/README.md](../data/video/cut/README.md).

## Names (2026-11-03)

- The practice robot is **Roksolana**, role name **the Doorkeeper**. Not "Agda".
- The English-speaking male robot voice is **Porter** ("porter" = doorkeeper).
- Footage still shows the old name: shot-03 terminal lines say "Agda speaks";
  keep VO and captions on the new names, and crop or blur those lines.

## What changed vs v3

- Every shot points at a clip that exists, or is marked **MISSING**.
- Stage 1 pass/fail asks for Meta "meaningfully used at runtime". v3 shot 7
  showed an empty telemetry panel. v4 makes the Meta block conditional on a
  real Spark run (block C), with an honest fallback.
- Bonus categories are named on screen (screeners flag from the video).
- Benchmarks come before 2:45 and are real numbers from the clips.

## A · 0:00–0:15 Hook & provenance (15 s, ≤ 35 words)

- PICTURE: title card (`data/video/auto/shot-01-title.png`) over 2 s of
  shot-03 board, blurred.
- ON SCREEN (first 10 s): "Built Oct 26 – Nov 4, 2026. Repo predates the
  window with audio experiments only."
- SAY: "Swedish government phone lines are voice robots that only understand
  exact words. Holdmate learns those words for you. Everything here was built
  October 26 to November 4."

## B · 0:15–1:35 Live product (80 s, ≤ 190 words)

| Time | Picture | Source (in → out) | SAY |
|---|---|---|---|
| 0:15–0:25 | Menu: HOLDMATE logo, pick "Board + talk" | shot-04 ~0:02 → 0:08 | "One command starts the board and the call." |
| 0:25–0:55 | Live call vs Roksolana (the Doorkeeper): open question → keyword → yes/no → ID | shot-03 ~0:00 → 1:30, cut to 30 s (2x ok) | "I answer in my own words. When the robot misses, Holdmate knows the words that transfer. Identification is faked — a human approves BankID." |
| 0:55–1:10 | Board: process lights up, queue number counts down, "You are number 2 in the queue" | shot-01 ~1:50 → 2:15 | "The board follows the call live, and the queue ticket counts down." |
| 1:10–1:20 | Queue 3 → 2 → 1, officer answers | shot-03 ~1:36 → 2:20, 3x | "A human answers — Holdmate hands the call back to you." |
| 1:20–1:25 | Watch on wrist ticks 44 → 43 live | `phone/watch-tick-44-43.mp4` (2.5 s) + `phone/watch-queue.mp4` 0:02 → 0:05 | "Same ticket on your wrist…" |
| 1:25–1:35 | iPhone ticket 46 → 1 (40x), then green "0 · YOUR TURN — answer now" | `phone/iphone-countdown-8s.mp4` (9 s; 16 s version at 20x also there) | "…and on your phone: when it's your turn, it tells you." |

iPhone source: screen recording 2026-11-02 22:08 (Photos,
`086F956E-…D52801.mp4`, 4:22). YOUR TURN lights at 4:10; 0:23–0:49 is the
camera app (cut out). Watch still shows a static "43" and no YOUR TURN; an
8 s retake during `./sh/demo-queue.sh` (QUEUE_START=3) would close that gap.

## C · 1:35–2:15 Agent + Meta AI (40 s, ≤ 95 words)

| Time | Picture | Source | SAY |
|---|---|---|---|
| 1:35–1:50 | Headless self-call, BFS lessons, "learned without Rickard saying a word" | `term/t1-selfcall.mp4` 2x | "At night Holdmate calls a practice copy of the line by itself. Breadth-first over every answer, 36 words learned, 3 that never work." |
| 1:50–2:15 | **Muse Spark live**: eval `--live` rows + provenance rows (model, latency) | `term/t6-spark-live.mp4` 5.2x (rescue 3/3, abstain 9/10, SAFETY OK, p95 10.9 s) | "When speech is noisy, Muse Spark maps it onto the robot's closed vocabulary — or abstains. Every call is logged with model and latency." |

Fallback if no live Spark run before the freeze: use `term/t4-eval.mp4`
(heuristic baseline) and SAY "This is the keyless baseline; Muse Spark is
the opt-in stage on top" — and accept that Stage 1 may not flag Meta usage.
Do **not** show `data/provenance.jsonl` today: it only has test rows (`x.test`).

## D · 2:15–2:45 Benchmarks & proof (30 s, ≤ 70 words)

| Time | Picture | Source | SAY |
|---|---|---|---|
| 2:15–2:27 | Intent eval: rescue 2/3, abstain 10/10, exact 3/3, SAFETY OK | `term/t4-eval.mp4` | "Safety first: on adversarial input it abstains ten out of ten, and never changes an exact match." |
| 2:27–2:37 | pytest: 223 passed | `term/t5-tests.mp4` 3x | "Over two hundred tests green in CI." |
| 2:37–2:45 | Route + map | `term/t2-show-call.mp4` last 8 s | "And it all replays without any key, from one clone." |

Add the Spark A/B line here (rescue rate Spark vs heuristic, p95 latency)
once block C has a live run — that is the strongest Tech Depth number.

## E · 2:45–2:55 Close (10 s, ≤ 20 words)

- PICTURE: end card `data/video/auto/shot-11-close.png`, add:
  github.com/kizouker/adaptive-IVR-agent · Muse Spark · Best Agentic Use-Case ·
  Best Creative Build.
- SAY: "Holdmate waits on hold, so you don't have to."
- Black from 2:55. Nothing after.

## Checklist against Judging Workflow §1

- [ ] ≤ 2:55 of content (ffprobe the export)
- [ ] Provenance spoken and shown by 0:10
- [ ] ≥ 80 % running product (A card 15 s + E card 10 s = 25 s non-product: OK)
- [ ] A Meta model call visible with its role (block C) — **blocked on live run**
- [ ] English VO + burned-in captions; unlisted YouTube, logged-out playback
- [ ] No personal paths or Claude/Codex names visible (shot-03 shows
      `/Users/raberg/...` paths: blur or crop the top lines)
