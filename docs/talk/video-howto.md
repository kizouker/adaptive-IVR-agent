## Submission video — how it was made (2026-11-04)

**Final:** https://youtu.be/orxqS8rnxt0 · file `data/video/HOLDMATE-SUBMISSION-2026-11-04.mp4` (2:55, 1920×1080)
Thumbnail: `data/video/HOLDMATE-THUMBNAIL.jpg`. Older versions: `data/video/cut/old-versions/`.

### Picture — all product footage, no screen recordings
The old hand-made screen recordings (Safari tabs, window switching) were replaced by scripted, repeatable recordings:

| Seg | What | How | Source |
|---|---|---|---|
| B1 | `./sh/holdmate.sh` → menu → [1] Board + talk, English call starts | VHS | `term/tapes/en-b1-holdmate.tape` → `term/en-b1-holdmate.mp4` |
| B2/B4 | English call: own words miss → robot lists words → "activity report" → ID → queue → officer | VHS, `talk.sh --quiet --call en` (typed) | `term/tapes/en-b2-talk.tape` → `term/en-b2-talk.mp4` |
| B3 | Board follows the same call live (no browser chrome) | Playwright page video while B2 runs | `term/tapes/rec-board.mjs` → `term/en-b3-board.mp4` (4× speed) |
| others | eval, tests, Spark live, map, watch/iPhone | earlier VHS / phone clips | `term/*.mp4`, `phone/*.mp4` |

All recordings run in a clean copy of the repo, so no personal tabs or paths leak in.

### Cut
`data/video/cut/build_cut.py` builds `silent.mp4` from the segments, with burned-in captions (`SAY` dict = what is said).
Run: `uv run --no-project --with pillow python data/video/cut/build_cut.py`.

### Sound — one voice at a time
- **Narration:** English AI voice (macOS `say`, Karen Premium; allowed by the rules with burned-in captions).
  Script built on *AI: A Modern Approach* ch. 2: rational agent, PEAS, environment properties.
  Text: `cut/narration/say.json`. Track: `cut/narration/narration.wav`.
- **Robot / officer:** Roksolana's real TTS lines from the recorded call, placed only in the narrator's pauses
  (34.6–46.7 s, 75.2–79.9 s). Menu music low under B1. Track: `cut/narration/robot-bed.wav`.
- Mix: narration + robot bed, loudness-normalized to −19 LUFS, 48 kHz AAC.

### Judging checks
- Provenance line ("built from scratch Oct 26 – Nov 4") spoken and on screen in the first 10 s.
- ≤ 2:55, ≥ 80 % product footage, Meta Muse Spark shown live (C2), benchmarks/tests before 2:45.

### Lessons
- `loudnorm` before `adelay` resets timestamps → clips shift; place clips with `anullsrc` + `concat` instead.
- `loudnorm` upsamples to 96–192 kHz → always `aresample=48000` after it (QuickTime played silence otherwise).
- BlackHole 16ch: sound lands on one channel; `-ac 1` averages all 16 → ~17 dB too quiet.
- ffmpeg mic recordings crackled; `-thread_queue_size 4096` + no resampling while recording; `adeclick` rescues old takes.
- Rickard's own voice takes: background noise (boiler) and talk drifted from the cut → AI narration chosen.

### Also changed (uncommitted, needs review)
`sh/talk.sh` + `sh/holdmate.sh`: the call follows the menu language, so Holdmate runs fully in English.
`README.md` line 11: new video link.
