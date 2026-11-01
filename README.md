# Holdmate — an adaptive IVR agent that practices on AF Agda

Holdmate learns to phone robot operators like the Swedish Public Employment
Service (Arbetsförmedlingen). It practices against AF Agda, a scripted copy of
the real IVR line built from recorded calls, so the real line is never touched
during training. Swedish voices on macOS: Agda speaks as Alva, the caller as
Oskar, the officer as Klara.

## Quick start

Run the launcher (works from any folder) and pick with arrows + Enter:

```bash
~/kod/001_Meta_Hackathon_w44_26_oct_to_3_nov/adaptive-IVR-agent/sh/holdmate.sh
```

Menu: 1 = board + talk, 2 = talk options, 3 = teach Agda words,
4 = Holdmate calls by itself, 5 = sound (speakers/AirPods/quiet), 6 = quit.

## Scripts (`sh/`)

Every script runs directly (executable bit + bash shebang) and from any folder.
Most follow `modes`: default run plus `check` (verifies, changes nothing).

| Script | What it does |
|---|---|
| `holdmate.sh` | Main menu: board server + talk + sound + lessons. Direct: `holdmate.sh 1` (board+talk), `2` (talk), `3` (teach), `4` (BFS lessons). |
| `talk.sh` | Talk to Agda with your own voice. Flags: `--airpods`, `--as <persona>`, `--queue N`, `--quiet`. See keys below. |
| `holdmate-call.sh` | Holdmate phones Agda by itself: BFS lessons per persona, headless. `--as <id>`, `--depth 0..2`, `--speak`, `--fresh`. |
| `learn-words.sh` | Review words Agda failed to hear; teach aliases (Agda's bad memory, off by default). |
| `demo-all.sh` | Full demo in one command: speaking call, keywords, queue, explorer, routing, snapshots. |
| `demo-call.sh` | Speaking demo: one persona phones Agda aloud, tries 3 keywords. |
| `demo-dialogue.sh` | Two-voice demo: Agda (Alva) vs caller (Oskar). |
| `demo-robot.sh` | Agda speaks the first 3 documented lines. |
| `show-call.sh` | Silent demo call: prints turns, keywords with why, and the map. |
| `show-map.sh` | Menu map with position marker. `show-map.sh [swedish\|english] [position]`. |
| `explore-demo.sh` | Explorer tries a persona's words; the map grows per call. |
| `route-demo.sh` | Loop-free route to the queue on both maps. |
| `find-queue.sh` | Find queue numbers in five sample lines. |
| `alert-demo.sh` | Fire the Mac queue alert for a place. |
| `classify-calls.sh` | Classify our lines on the Russell & Norvig ch.2 axes. |
| `record-call.sh` | Record robot voice from BlackHole (checks the sound chain first). |
| `transcribe-latest.sh` | Transcribe the newest recording with whisper.cpp. |
| `play-latest.sh` | Play the newest recording. |
| `check-recording.sh` | Check if a recording has sound or is silent. |
| `watch-board.sh` | Feed the React board live, turn by turn. |
| `watch-calls.sh` | Live call board in the browser (reloads every 3 s). |
| `watch-map.sh` | Live graphical call map (reloads every 2 s). |
| `check-reqs.sh` | Verify requirement ID coverage (specs, features, tickets). |
| `check-structure.sh` | Verify repo layout, test mirror, hygiene. |
| `check-security.sh` | Secrets, keys, dangerous patterns. |
| `pre-push.sh` | Local gate before pushing: coverage, lint, tests. |

Helpers, not run directly: `ui.sh` (shared output functions), `switchaudio.sh`
(notes), `make-tickets.sh` + `apply-names.sh` (one-shot repo chores).

## Keys during a talk call

Any key skips ahead. `0` jumps to the English menu. `a` toggles
speakers/AirPods. `t` toggles quiet mode (type + read). `+`/`-` adjusts her
volume. `q`/Esc quits. At the faked identification, Enter accepts the test
number; typed digits are ignored and never logged.

## Running scripts: no `sh` prefix

`sh/` is the folder name, not a command. Run scripts by their path:

```bash
~/kod/001_Meta_Hackathon_w44_26_oct_to_3_nov/adaptive-IVR-agent/sh/talk.sh --quiet
```

Never `sh sh/talk.sh`: that forces POSIX `sh`, and the scripts need bash
(they say so in their first line). From the repo folder, `./sh/talk.sh`
works too.

## Tests and checks

```bash
PYTHONPATH=src pytest -q
```

```bash
sh/check-reqs.sh && sh/check-structure.sh && sh/check-security.sh
```

Board: `npm run lint --prefix ui/board`, `npm run build --prefix ui/board`.

## Where things live

- `docs/01–05_*` — vision, problem, stories, roadmap, open questions.
- `features/*.feature` — Gherkin scenarios (each maps to pytest).
- `openspec/` — specs, design notes, tickets.
- `data/` — recorded lines, phrasebooks, transcripts, learned knowledge.
- `src/adaptive_ivr_agent/` — agent, robot, maps, board data.
- `ui/board/` — React + Redux live board.
