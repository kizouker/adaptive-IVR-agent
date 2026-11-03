# Commands #command

```bash
./sh/holdmate.sh                 # main menu, 1 starts server+board
QUEUE_START=50 ./sh/demo-queue.sh  # countdown demo
./sh/submission-check.sh check   # NFR gate (video, suite, LICENSE, freeze, partner)
./sh/board-docker.sh test        # smoke-test the container board
PYTHONPATH=src python3 eval/llm_intent_eval.py --openweight  # intent eval vs open weights
PYTHONPATH=src pytest -q         # full suite (runs from repo root)
docker compose up --build        # board on :8080 (or BOARD_PORT)
npm run test:e2e --prefix ui/board  # local e2e (spins preview server)
BOARD_URL=http://localhost:8080 npm run test:e2e --prefix ui/board  # e2e vs Docker
BOARD_URL=https://<azure-fqdn> npm run test:e2e --prefix ui/board  # e2e vs Azure
./sh/board-stack.sh up     # infra+tests: start detached, wait healthy
./sh/board-stack.sh test   # e2e vs the container
./sh/board-stack.sh status # monitor: container + all endpoints
./sh/board-stack.sh down   # stop everything

Ports: 5173 = vite dev (normal board), 8080+ = Docker, 5199 = e2e preview.
```

See also: [[submission]] for portal copy-paste, [[partners]] for env values.
