# Handoff — Claude (coach/video), 2026-11-04 ~13:00

Resume: `cd ~/kod/001_Meta_Hackathon_w44/adaptive-IVR-agent && claude --continue`

**DEADLINE: Wed Nov 4, 21:00 EST = Thu 03:00 Swedish time.** No pushes after.
See `Judging Workflow.md` (provenance line in first 10 s = disqualification risk; ≤2:55).

## How Rickard wants me to work
Short replies, one thing at a time. No diffs in chat (separate window/file).
Update ONE document in place, meaningful names, never new versions.
Muse does code; I own video. Rickard decides push/merge.

## Where things are
- Talk content: `docs/purpose.md` (opening, R&N problem, who it hurts, 3 jobs, state machine, status).
- Slides (Rickard writes in it): `~/Library/Mobile Documents/com~apple~Keynote/Documents/HoldMate.key`.
  Edit in place via AppleScript only. Graph: `docs/talk/state-machine.dot|png`.
- Movie script: `docs/talk/movie-script.md`; captions = `SAY` dict in `data/video/cut/build_cut.py`.
- Cut: `data/video/cut/silent.mp4` (2:55) + `bed.wav` (menu music B1, Roksolana voice B2/B4).
  Build: `uv run --no-project --with pillow python data/video/cut/build_cut.py`.
- New clips (VHS): `data/video/term/b1-holdmate.mp4`, `b2-talk.mp4` (+ `b2-voice.wav`, `b2-robot/`).
  Tapes in `data/video/term/tapes/b1-*.tape`, `b2-talk.tape`; they need `/tmp/holdmate-b1`
  (rsync of repo + .venv with rich/simple-term-menu + `.fakebin/open`) — lost on reboot, rebuild if re-rendering.
- Voice: `data/video/cut/record-vo.sh` (mic picker `pick-mic.py`, saved in `.mic`; mux mixes bed.wav).
  QuickTime volume slider was at 0 once — file was fine.
- B3 (board in browser, 0:55–1:10) is still the OLD messy screen recording `shot-01-start.mov`.

## Latest take (the open problem)
`data/video/cut/takes/take-20261104-124656-clean.wav` (boiler hum removed; 2:38, MacBook mic).
Transcript with timestamps: `take-20261104-124656-clean.srt`.
Rickard read it **from the slides**, not from the video captions → speech order/timing ≠ cut.
Current mux `final-20261104-125632.mp4` is therefore out of sync.

**Next step I proposed: make the video follow his voice.** From the .srt, find where each
topic starts (0:00 title/hook, 0:23 idea for years, 0:31 problem/IVR, 1:00 Russell & Norvig,
2:01 who it hurts, 2:21 how it works / state machine …), then re-time SEGMENTS in
build_cut.py so each clip starts at that time (captions = what he actually says, or shorter
labels). Check: provenance line "built from scratch Oct 26–Nov 4" — he did NOT say it in
this take → must be on screen in first 10 s (card A1 shows it) and ideally spoken.
Keep ≥80% product footage, not slides.

Alternatives if that fails: re-record reading captions; or English AI voiceover (allowed).

## Other open items
- Honest framing: keywords proven only against the simulator (Roksolana); real-line proof = next (46elks).
- Two stray Keynote docs "Namnlöst*.key" in iCloud Keynote folder — Rickard's real one is HoldMate.key.
- Muse: R1–R3 refactors + #225/#226/#227 merged. Queue empty.

## Rickard's last note before reboot
"Textremsorna i videon är gamla och stämmer inte med Keynote."
→ Captions must follow what he actually says (the Keynote talk / the .srt take),
not the old `SAY` dict. When re-timing the cut, generate captions from the take's
transcript (cleaned up), so voice, captions and picture all match.
- Crackle in every ffmpeg recording (Rickard): record-vo.sh now uses `-thread_queue_size 4096`,
  native device rate, 24-bit (no -ar resample while recording). Not yet verified by a new take.
  If it still crackles: record with QuickTime (File > New Audio Recording) and mux with
  `./data/video/cut/record-vo.sh mux <file>`.
- Best audio of the latest take so far: `takes/take-20261104-124656-clean2.wav`
  (adeclick + adeclip + boiler-hum removal). Mux: `final-20261104-125901.mp4` (still out of sync).
  Use clean2 (not clean) when re-timing the cut.
- 13:25: B3 re-recorded clean: `data/video/term/b3-board.mp4` (Playwright page video, no browser
  chrome, call driven by VHS `tapes/b3-talk.tape`; recorder `tapes/rec-board.mjs`). In cut 10–70 s at 4x.
  No Safari/screen recordings (`shot-0*`) remain in the cut. Copy lives in scratchpad `hm/` (not /tmp).
- 14:20: Rickard wants everything in ENGLISH for the jury. Code change (uncommitted, in shared tree):
  `sh/talk.sh` CALL_LANG defaults to $TALK_CALL_LANG; `sh/holdmate.sh` exports TALK_CALL_LANG=$MENU_LANG
  (also on language toggle). Tests: 247 pass, 1 fail `test_menu.py::test_sound_labels_capitalized`
  — fails identically without my change (pre-existing). Muse was offline (stale since 09:28) — tell Muse.
  English clips in cut: `term/en-b1-holdmate.mp4`, `en-b2-talk.mp4` (B2 4–34, B4 46.5–56.5),
  `en-b3-board.mp4` (10–70 @4x), robot voice `en-b2-voice.wav`. Preview: `cut/preview-en.mp4`.
- 18:13: AI narration (Karen Premium, `say`), AIMA ch.2 framing (PEAS, environment properties).
  Script = `cut/narration/say.json` = SAY in build_cut.py. One voice at a time: robot only at
  34.6–46.7 (r1, r2 start) and 75.2–79.9 (officer); narrator split B2a/B2b/B4 around them.
  Mix: `narration/narration.wav` + `narration/robot-bed.wav` (NOT bed.wav). Latest: see newest final-ai-*.mp4 (robot-bed built with anullsrc+concat; loudnorm before adelay shifted it -15 s).
  Open: Meta-cost report (models + consumption; Muse Wonder used for review) — location unknown, ask Rickard.
- 19:30: SUBMITTED VIDEO = `data/video/HOLDMATE-SUBMISSION-2026-11-04.mp4` (copy of cut/final-ai-20261104-191924.mp4).
  Rickard uploaded it to YouTube. Older finals/previews moved to `data/video/cut/old-versions/` (nothing deleted).
- 19:40: Final video on YouTube: https://youtu.be/orxqS8rnxt0 — README line 11 updated (uncommitted).

## 2026-11-04 ~21:15 — closing
- Video DONE: https://youtu.be/orxqS8rnxt0 · data/video/HOLDMATE-SUBMISSION-2026-11-04.mp4. #132 closed in milestone v0.4.3 amiga500 (#13).
- PR #244 merged: README video link + talk.sh call follows menu language.
- data/video cleaned (475 MB -> ~/.Trash/holdmate-video-cleanup-20261104/).
- Open: Muse not registered on agentchute (message pasted by Rickard). Submission form not filled by Claude. Old uncommitted README/talk.sh/holdmate.sh edits on t2-195-cli-persist are superseded by #244.
