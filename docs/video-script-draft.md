# Holdmate — 3-minute video script v3 (shot list for piecewise recording)

Manuscript lives here: `docs/video-script-draft.md`. Total ≤ 2:55, English
voiceover + burned-in captions. Film one shot at a time, I assemble.
Rule source: `Judging Workflow.md` (provenance ≤10s, Meta calls visible,
benchmarks before 2:55, nothing after).

## 0:00–0:15 Hook & provenance

- SHOT 1 (15s): title card + spoken provenance.
- SAY: "Sweden's voice-menu maze only understands exact words. Holdmate
  learns them for you. Built from scratch Oct 26 to Nov 4 — repo predates
  the window with audio experiments only."
- SHOW: card with the same sentence on screen for the first 10 seconds.

## 0:15–1:35 Live walkthrough

- SHOT 2 board-server start (15s): terminal, `./sh/holdmate.sh` → menu 1.
  SAY: "One command starts everything."
- SHOT 3 talk flow (25s): live call vs Roksolana: open question → keyword
  → yes/no → ID → queue ticket counting down → handover beeps.
  SAY: "She asks, I answer, the ticket counts down, a human takes over."
- SHOT 4 training (15s): `./sh/holdmate.sh` lessons running headless.
  SAY: "Overnight it phones the copy by itself and learns the words."
- SHOT 5 iPhone (10s): queue mirrors to iPhone over LAN.
- SHOT 6 Watch (10s): YOUR TURN blink + beep on the Watch.

## 1:35–2:15 Meta AI architecture

- SHOT 7 telemetry (25s): board telemetry panel with live rows.
  SAY: "Every Meta call is logged — model, runtime, latency — visible here."
- SHOT 8 eval (15s): `eval/llm_intent_eval.py --live` tail (4x speed ok).
  SAY: "Spark normalizes noisy speech onto the closed vocabulary."

## 2:15–2:45 Benchmarks & proof

- SHOT 9 numbers (15s): pytest tail + Actions green + e2e vs Docker.
  SAY: "Two hundred tests green, safety eval holds, one-command replay."
- SHOT 10 Azure (15s): `BOARD_URL=https://... ./sh/board-e2e.sh` green.
  SAY: "Same suite, against the cloud."

## 2:45–2:55 Summary & clean stop

- SHOT 11 card (10s): repo URL, models, headline metrics.
  SAY: "Holdmate waits on hold, so you don't have to."
- Stop at 2:55. Nothing after — playback cuts at 3:00.

## Recording tips

- Lines: read from this file on a second screen/phone; or record video
  muted and dub the voiceover after (cleaner audio, easier retakes).
- Clean screen: fullscreen terminal, Cmd-+ twice, quit other apps, hide
  the dock (Settings → Dock → autohide), Do Not Disturb on.
- Focus: one window per shot; move the mouse out of frame before recording.
- Save each .mov as `data/video/shot-NN-<name>.mov`; I assemble + caption.
