# Holdmate shell scripts – run, check, debug (macOS, bash)

All `sh/*.sh` share one shape: preflight, numbered steps, `run | check` modes.

## Install (once)

```bash
chmod +x sh/*.sh   # already set in the repo; rerun after fresh clone
```

## Use

```bash
./sh/submission-check.sh check   # read-only: video length, suite, LICENSE, freeze
./sh/keep-awake.sh               # block sleep; leave window open + lid open + charger
./sh/check-board.sh              # is board-state.json reachable locally + on LAN?
QUEUE_START=50 ./sh/demo-queue.sh  # countdown demo from 50
./sh/holdmate.sh                 # main menu: 1 starts server + board
```

| Flag / env | What it does |
|---|---|
| `check` | Read-only mode, changes nothing |
| `VIDEO=...` | Which video file submission-check measures |
| `QUEUE_START=N` | Demo queue starts at N |
| `PORT=...` | Board port (default 5173) |

## Notes / Gotchas

- `✔ OK` passed, `⚠ WARN` needs your eyes, `✘ FAIL` stopped: fix and rerun.
- Reruns are safe (idempotent).
- `caffeinate` assertions are denied inside agent sandboxes: run keep-awake.sh
  in your own terminal, not via the agent.

## Links

- Submission NFR map: docs/nfr-judging.md
