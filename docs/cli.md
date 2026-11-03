# CLI reference (sh/)

Every script: preflight, numbered steps, loud failure. run = do it, check = dry run.

## sh/alert-demo.sh

Demo: fire the Mac queue alert for a place (default 2). T-012.

## sh/apply-names.sh

Build docs/*.md from docs/templates/*.md by filling in the code names in docs/names.env.

## sh/azure-killswitch.sh

Azure auto kill-switch: delete holdmate-rg once past KILL_DATE (#169). Safety: only this resource group, only after the date, check mode first. Runs on: Rickard's Mac (M4) via cron. Modes: run | check.

## sh/bake-board.py

Bake doorkeeper lines + telemetry tail into board-state.json (idempotent).


## sh/board-docker.sh

Board over Docker with automatic free-port pick (#169). Probes 8080..8090, runs compose on the first free one. Runs on: Rickard's Mac (M4). Modes: run | check | test.

## sh/board-e2e.sh

E2E runner with preflight: verifies the board answers before Playwright (#169). Local mode (no BOARD_URL) spins the preview server itself; remote mode probes BOARD_URL first and fails with a helpful message instead of socket errors.

## sh/board-stack.sh

Board stack: infra + tests together (#169). up starts the container detached on a free port and waits until healthy; test runs e2e against it; status checks container + endpoints; down stops everything.

## sh/check-board.sh

Board-server preflight for the iPhone/Watch apps: is board-state.json reachable on localhost AND on LAN (.local) with valid JSON? Runs on: Rickard's Mac (M4). Modes: run (default) | check (same, read-only).

## sh/check-prompts.sh

Heuristic prompt-injection self-scan (OWASP LLM01 baseline). Fails loudly. Scans agent instruction files for directives that weaken prompt safety, such as ignore-the-instructions or reveal-the-prompt. CI runs this on

## sh/check-recording.sh

Check if a recording has sound or is silent. No argument = the newest file in data/recordings. Exit code: 0 = has sound, 2 = silent.

## sh/check-reqs.sh

Verify REQ ID coverage: every requirement in openspec/specs must appear as a tag in features/ and as a ticket heading in openspec/tickets.md.

## sh/check-security.sh

Check security basics: secrets, keys, dangerous patterns. Fails loudly. Part of T-051. CI runs this on every push. Full mapping: docs/security-review.md

## sh/check-structure.sh

Check repo structure: required layout, test mirror, hygiene. Fails loudly. Part of T-051. CI runs this on every push.

## sh/classify-calls.sh

Classify our four lines on the ch.2 axes from transcript evidence (T-048). Usage: classify-calls.sh. Evidence is hand-distilled from the call logs.

## sh/demo-all.sh

Full demo in one command: speaking call, keywords, queue, explorer, routing, plus graphic snapshots. Part of T-044 (#46).

## sh/demo-call.sh

Speaking demo call: one persona phones AF Agda ALOUD, tries 3 keywords. Caller words use voice Oskar, robot replies use voice Alva. Mac only. Prints every turn, like show-call.sh. Part of T-046 (#48).

## sh/demo-dialogue.sh

Two-voice demo: AF Agda (Alva) vs the caller (Oskar). Live audio, Mac only. Lines come from data/doorkeeper-lines.json (L01, L02, L03); caller line is the ny-arbetslos role opening. Part of T-039 (#41).

## sh/demo-queue.sh

Demo queue on all screens: run one quick lesson round to the queue, bake the board, then count the latest queue place down slowly so the iPhone/Watch/widget (5s poll) can follow it live to 0.

## sh/demo-robot.sh

Robot speaks the first 3 documented AF Agda lines (Alva). Live audio, Mac only. Part of T-042 (#44). Run from anywhere: sh /path/to/sh/demo-robot.sh

## sh/elks-smoke.sh

46elks smoke test: place one short test call (default: to your own mobile). Runs on: Rickard's Mac (M4). Modes: run (default) | check. Env: ELKS_USER, ELKS_PASS (API creds, never printed), ELKS_FROM (your

## sh/explore-demo.sh

Demo: explorer tries a persona's words, map grows per call (T-009).

## sh/find-queue.sh

Demo: find queue numbers in five sample lines (T-011).

## sh/holdmate-call.sh

Holdmate calls Agda by itself: BFS lessons per persona, headless and fast. Runs on: Rickard's Mac (M4). Modes: run (default) | check. Flags: --as <persona> (one lesson), --all (every persona, default),

## sh/holdmate.sh

Holdmate launcher: board server + talk from one menu, runnable from anywhere. Runs on: Rickard's Mac (M4). Modes: menu (default) | check. Direct: 1, 2, 3, 4. 1 = start the board server, open the page, and talk. 2 = talk options.

## sh/keep-awake.sh

Keep the Mac awake overnight so agents keep running. Runs on: Rickard's Mac (M4). Modes: run (default) | check. Lid must stay OPEN (caffeinate cannot stop lid-close sleep); charger in.

## sh/learn-words.sh

Teach Agda the words it failed to hear. Runs on: Rickard's Mac (M4). Modes: apply (default) | check. Reads data/talk-misses.jsonl, asks what each miss meant (keyword, Enter to

## sh/make-tickets.sh

Create one GitHub issue per ticket in openspec/tickets.md (30 FN-REQ + 6 NF-REQ). Each ticket carries its requirement ID as its name. Idempotent: skips any ID already found in an existing issue title.

## sh/play-latest.sh

Play a recording. No argument = the newest file in data/recordings.

## sh/pre-push.sh

Local gate before pushing: req coverage, shell syntax/lint, tests if present.

## sh/record-call.sh

Record the robot voice from BlackHole. First checks the whole sound chain and shows a checklist. Switches the Mac's audio output and microphone back when the script ends.

## sh/route-demo.sh

Demo: loop-free route to the queue on both maps (T-010).

## sh/show-call.sh

Demo call: one persona phones AF Agda, tries 3 keywords, robot answers. Prints every turn, the used keywords with why (errand), and the map. Usage: show-call.sh [persona-id] (default ny-arbetslos). Part of T-044 (#46).

## sh/show-map.sh

Show the menu map with the position marker (*). Usage: show-map.sh [swedish|english] [position] Examples: show-map.sh swedish 2 / show-map.sh english 3. Part of T-005 (#7).

## sh/submission-check.sh

Submission gate: auto-verify judging NFRs before the freeze (#175). Covers NFR-001 (video length), NFR-006 (keyless repo), NFR-010 (LICENSE), NFR-012 (freeze). Runs on: Rickard's Mac (M4). Modes: run | check.

## sh/switchaudio.sh

(notes file, not an executable script)

## sh/talk.sh

Talk to the practice robot with your own voice (push-to-talk loop). Runs on: Rickard's Mac (M4). Modes: talk (default) | check. Flags: --airpods (physical AirPods; must be connected), --as <persona> (role-play + tag rounds for Holdmate training),

## sh/transcribe-latest.sh

Turn a recording into text with whisper.cpp. No argument = the newest file in data/recordings. The text is saved next to the recording, as a .txt file with the same name.

## sh/watch-board.sh

Feed the React board: two personas phone in turn by turn, writes JSON. Start the dev server first (cd ui/board && npm run dev), then run this. Board polls ui/board/public/board-state.json every 3 s. Part of T-045 (#47).

## sh/watch-calls.sh

Live call board: two personas phone in turn by turn; regenerates the board. Open /tmp/holdmate-board.html in a browser (reloads every 3 s). Usage: watch-calls.sh [persona1] [persona2]. Part of T-045 (#47).

## sh/watch-map.sh

Live graphical call map: walks the chain and re-renders /tmp/karta-live.svg. Open /tmp/karta-live.html in a browser; it reloads every 2 s and the red box moves left to right as the call progresses. Usage: watch-map.sh [swedish|english]

