# Commands #command

## Senaste (läs uppifrån)

```bash
./sh/board-stack.sh up      # starta containern detached + vänta tills frisk
./sh/board-stack.sh test    # e2e mot containern (rätt port automatiskt)
./sh/board-stack.sh status  # monitor: container + alla endpoints svarar?
./sh/board-stack.sh down    # stoppa allt
BOARD_URL=http://localhost:8081 ./sh/board-e2e.sh  # e2e mot vald port (kolla docker ps)
./sh/board-docker.sh test   # röktest: startsida + ködata + version + volym-API
docker ps --format '{{.Names}} {{.Ports}}'  # vilken port tog containern?
OPENWEIGHT_API_KEY=... ./sh/submission-check.sh check  # gate inkl partnerkoll
az account show --query "{name:name, user:user.name}" -o table  # vem är inloggad?
```

## Basen

```bash
./sh/holdmate.sh                 # huvudmeny, 1 startar server+board
QUEUE_START=50 ./sh/demo-queue.sh  # nedräkningsdemo
PYTHONPATH=src pytest -q         # full testsvit
OPENWEIGHT_MODEL=muse-glimmer:30b-mlx PYTHONPATH=src python3 eval/llm_intent_eval.py --openweight
```

## Portar

5173 = vite dev (vanliga boarden), 8080+ = Docker, 5199 = e2e preview.

## Bevaka

```bash
watch -n 60 ./sh/board-stack.sh status  # kräver: brew install watch
while true; do ./sh/board-stack.sh status; sleep 60; done  # utan watch
```

## Cron

```bash
0 9 * * * .../sh/azure-killswitch.sh >> /tmp/holdmate-kill.log 2>&1  # raderar RG efter 3 dec
```
