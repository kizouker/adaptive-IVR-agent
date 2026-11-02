# Holdmate — 3-min submission video production plan

Companion to [video-script-draft.md](video-script-draft.md). All commands run
from the repo root on Rickard's Mac. Stills land in `docs/images/` (does not
exist yet — step 0 creates it). Screenshots already in repo: only
`docs/multioutput.png`; everything below is captured fresh.

## 0. Setup (once)

```bash
mkdir -p docs/images
./sh/demo-queue.sh check
```

Close Slack/Discord, silence notifications except the demo alert, set
Terminal to 120x36 with 18pt font, Chrome to 1440x900, board server up:

```bash
./sh/holdmate.sh 1
```

## 1. Shot list (10 shots, mapped to script timestamps)

Source key: STILL = `screencapture` png into `docs/images/`;
CAPTURE = live screen recording (`.mov`); VO = Rickard voiceover only.

| # | Script time | Shot | Source |
|---|-------------|------|--------|
| S1 | 0:00–0:20 Problem | Title card: Terminal showing `./start.sh` banner + board open behind | STILL `docs/images/shot-title.png` + VO (script problem quote) |
| S2 | 0:20–1:10 Talk | `./sh/talk.sh` live call: Agda (Alva) greets, keyword, route; show `0` English menu + `t` quiet toggle | CAPTURE `clip-talk.mov` (50s) + live audio, VO intro line |
| S3 | 1:10–1:25 Board turns | Browser board: turns, keywords with why, queue place | CAPTURE `clip-board.mov` (15s) + VO |
| S4 | 1:25–1:40 Board map | `watch-map.sh` graphical map with position marker, then `./sh/show-map.sh` menu map | STILL `docs/images/shot-map.png` + VO; `./sh/show-call.sh` output as cutaway STILL `docs/images/shot-call.png` |
| S5 | 1:40–2:05 Queue | `demo-queue.sh` countdown 5→0 on board; iPhone/Watch on camera beside the Mac | CAPTURE `clip-queue.mov` (30s) + phone footage, VO |
| S6 | 2:05–2:20 Alert+sound | `./sh/alert-demo.sh 2` Mac notification fires; `holdmate.sh` menu item 5 sound switch | STILL `docs/images/shot-alert.png` + CAPTURE `clip-sound.mov` (10s), VO |
| S7 | 2:20–2:32 Tech explorer | `./sh/explore-demo.sh` map growing per call | CAPTURE `clip-explore.mov` (12s), VO tech quote |
| S8 | 2:32–2:42 Tech headless | `./sh/holdmate-call.sh --depth 1` headless self-call | STILL `docs/images/shot-headless.png` + VO |
| S9 | 2:42–2:50 Tech words+route | `./sh/learn-words.sh` alias teaching, then `./sh/route-demo.sh` loop-free route | STILL `docs/images/shot-learn.png`, STILL `docs/images/shot-route.png` + VO |
| S10 | 2:50–3:10 Next steps + close | 46elks dashboard in browser; iPhone-on-speakerphone photo; end card "Holdmate waits on hold, so you don't have to." | STILL `docs/images/shot-elks.png` + photo + VO (script next-steps quote + close line) |

Shot count: 10 (6 stills batches + 4 capture clips + phone photo, VO throughout).

## 2. Exact capture commands

Run each, then capture. Stills first (fast), clips second.

```bash
# S1 title: start the app, wait for board + talk banner, then shoot
./start.sh
screencapture -x -m docs/images/shot-title.png
```

```bash
# S4 map + silent call cutaway
./sh/watch-map.sh &
screencapture -x -m docs/images/shot-map.png
kill %1
./sh/show-call.sh
screencapture -x -m docs/images/shot-call.png
```

```bash
# S6 alert still (fires a real Mac notification for place 2)
./sh/alert-demo.sh 2
screencapture -x -m docs/images/shot-alert.png
```

```bash
# S8 headless + S9 words/route stills
./sh/holdmate-call.sh --depth 1
screencapture -x -m docs/images/shot-headless.png
./sh/learn-words.sh
screencapture -x -m docs/images/shot-learn.png
./sh/route-demo.sh
screencapture -x -m docs/images/shot-route.png
```

```bash
# S10 46elks dashboard: open https://46elks.com in Chrome, log in, then shoot
screencapture -x -m docs/images/shot-elks.png
```

Screen recordings (`-v` video, `-T` seconds, needs macOS Sonoma+;
fallback: QuickTime Player → File → New Screen Recording):

```bash
# S2 talk clip: start recording, then in a second Terminal run the call
screencapture -v -T 50 clip-talk.mov &
./sh/talk.sh
```

```bash
# S3 board clip: board in Chrome, live turns
screencapture -v -T 15 clip-board.mov
```

```bash
# S5 queue clip: short countdown take (5 ticks x 5s = 25s + lesson run)
QUEUE_START=5 QUEUE_DELAY=5 ./sh/demo-queue.sh check
screencapture -v -T 60 clip-queue.mov &
QUEUE_START=5 QUEUE_DELAY=5 ./sh/demo-queue.sh
```

```bash
# S6 sound clip + S7 explorer clip
screencapture -v -T 10 clip-sound.mov &
./sh/holdmate.sh  # then press 5, pick speakers
screencapture -v -T 12 clip-explore.mov &
./sh/explore-demo.sh
```

Phone photo (S5/S10): iPhone on speakerphone next to the Mac showing the
queue ticket; take 3 photos, keep the sharpest as `docs/images/shot-iphone.jpg`.

## 3. Recording checklist for Rickard

- Mic: AirPods OFF for VO (use MacBook mic or USB mic 15cm away); AirPods
  ON only for the S6 sound-switch demo. Test: record 5s, play back, no hiss.
- Quiet: windows closed, washing machine off, phone on Do Not Disturb
  (except the demo iPhone), one quiet room, no keyboard typing during VO.
- Takes: 2 full VO takes of each script block (problem / talk intro /
  board / queue / tech / next steps / close line); clap once before each
  take so the spike marks the sync point. Keep take 2 unless it has a flub.
- VO pace: ~130 words/min; the script blocks are timed — if a take runs
  long, trim words, never speed up the audio past 1.05x.
- Live audio: S2 talk clip keeps its real Agda/call audio under the VO;
  duck live audio to −12dB wherever VO speaks.
- After every capture: replay the file once before moving on; re-shoot
  immediately if text is blurry or a notification leaked in.

## 4. Assembly order (iMovie or DaVinci Resolve, 1080p, target 3:00–3:10)

1. Timeline: S1 (12s, fade in) → S2 (50s) → S3 (15s) → S4 (15s: map 10s,
   call cutaway 5s) → S5 (25s) → S6 (15s: alert 5s, sound 10s) →
   S7 (12s) → S8 (10s) → S9 (8s: 4s + 4s) → S10 (18s: elks 8s,
   iPhone photo 5s, end card 5s with close line).
2. Lay VO takes under each shot; cut video to VO, not the reverse.
3. Title lower-third on S1: "Holdmate — an adaptive IVR agent".
4. End card: white text on black, "Holdmate waits on hold, so you
   don't have to." + repo URL `github.com/kizouker/adaptive-IVR-agent`.
5. Export 1080p H.264, watch once end-to-end, check total ≤ 3:10,
   then upload.
