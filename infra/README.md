# Azure deploy (tomorrow, with Rickard)

Cheapest live path is already done: GitHub Pages serves the board at
https://kizouker.github.io/adaptive-IVR-agent/ — that counts as the live app.
Use Azure below only for extra hackathon credit (real container deploy).

## 0. Prereqs (Rickard's terminal)

- `az login` (his Azure account) + a subscription picked.
- Image published to GHCR (needs his `GITHUB_TOKEN` with packages:write;
  never commit it).

## 1. Build + push the image

```sh
docker build -f Dockerfile -t ghcr.io/kizouker/adaptive-ivr-board:v0.3.4 .
echo "$GITHUB_TOKEN" | docker login ghcr.io -u kizouker --password-stdin
docker push ghcr.io/kizouker/adaptive-ivr-board:v0.3.4
```

## 2. Deploy the Bicep stack

```sh
az group create --name holdmate-rg --location swedencentral
az deployment group create --resource-group holdmate-rg \
  --template-file infra/main.bicep \
  --parameters @infra/main.parameters.json
```

## 3. Read the URL

```sh
az deployment group show --resource-group holdmate-rg --name main \
  --query properties.outputs.fqdn.value -o tsv
```

## 4. Cost control

- The app scales to zero when idle (minReplicas 0) and caps at 2 replicas.
- A €5 monthly budget mails `alertEmail` at 50/80/100% — set it in
  `infra/main.parameters.json` before deploying.
- Budgets only mail; they never stop anything. Kill-switch (stops all cost):

```sh
az group delete --name holdmate-rg --yes
```

Run the kill-switch right after judging, and any time a budget mail lands.
