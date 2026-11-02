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
docker build -t ghcr.io/kizouker/adaptive-ivr-board:v0.3.2 ui/board
echo "$GITHUB_TOKEN" | docker login ghcr.io -u kizouker --password-stdin
docker push ghcr.io/kizouker/adaptive-ivr-board:v0.3.2
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

Tear down after judging: `az group delete --name holdmate-rg` (stops all cost).
