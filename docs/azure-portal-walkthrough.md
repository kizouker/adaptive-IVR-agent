# Azure portal walkthrough (read after lunch, ~10 min)

Goal: see Holdmate live on Azure, verify it, know where cost lives.
Prereqs done: `az login` (Azure for Students), code on main after PR #187.

---

## Slide 1 — Push the image (your terminal, 5 min)

```sh
git checkout main && git pull
docker build -f Dockerfile -t ghcr.io/kizouker/adaptive-ivr-board:v0.3.4 .
echo "$(gh auth token)" | docker login ghcr.io -u kizouker --password-stdin
docker push ghcr.io/kizouker/adaptive-ivr-board:v0.3.4
```

Verify: https://github.com/kizouker?tab=packages → adaptive-ivr-board v0.3.4.
If login fails: new token at github.com/settings/tokens (packages:write).

---

## Slide 2 — Deploy (your terminal, 5 min)

```sh
az group create --name holdmate-rg --location swedencentral
az deployment group create -g holdmate-rg \
  --template-file infra/main.bicep \
  --parameters @infra/main.parameters.json \
  --parameters alertEmail=riab0007@ad.umu.se \
  image=ghcr.io/kizouker/adaptive-ivr-board:v0.3.4
az deployment group show -g holdmate-rg -n main \
  --query properties.outputs.fqdn.value -o tsv
```

Last command prints the public URL. Save it.

---

## Slide 3 — Portal: resource group (click-path)

1. https://portal.azure.com → search `holdmate-rg` → open it.
2. You should see: Container App `holdmate-board` + managed environment.
3. If red/failed: click the deployment in the bell icon (top right) for the error.

---

## Slide 4 — Portal: the app

1. Inside holdmate-rg → click `holdmate-board`.
2. Overview → copy **Application Url** (= the fqdn from step 2).
3. Open it in a browser: the board loads, queue ticket visible.
4. Left menu → **Log stream**: you should see `holdmate board on :80`.

---

## Slide 5 — Test it (your terminal, 2 min)

```sh
BOARD_URL=https://<fqdn-fran-steg-2> ./sh/board-e2e.sh
```

Green = Azure serves front page + queue data + version. This is the
same suite CI runs locally, now against the cloud.

---

## Slide 6 — Monitoring (portal)

- holdmate-board → **Monitoring → Metrics**: add Requests + Replica Count.
  Idle should show 0 replicas (scale-to-zero = ~€0).
- **Log stream** for live console output.
- Cost: portal search `Cost Management` → scope = your subscription →
  daily cost should read ~€0.00.

---

## Slide 7 — Cost control (already wired)

- €5 monthly budget mails riab0007@ad.umu.se at 50/80/100%.
- Student subscription hard-stops at credit exhaustion (can never overdraw).
- Local kill-switch cron deletes holdmate-rg on 2026-12-03.
- Manual kill-switch (stops all cost now):

```sh
az group delete --name holdmate-rg --yes
```

---

## Slide 8 — When things break

| Symptom | Check |
|---|---|
| Image 404 at deploy | Step 1 re-run; wait 1 min after push |
| Deploy fails on image pull | GHCR package must be public (packages → settings) |
| App 503 / sleeps | Normal cold start (~10s); refresh |
| No fqdn output | `az deployment group show -g holdmate-rg -n main` for error |
