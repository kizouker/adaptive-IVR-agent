# Rickard's check-off list #checklist

Updated 2026-11-03. Check, then tell Muse ("done").

## Now
- [ ] PR #187 (e2e remote + killswitch + brain) — say merge when green
- [ ] PR #185 (English calls worker) — review + merge into batch
- [ ] Baseten key → `OPENWEIGHT_API_KEY=... ./sh/submission-check.sh check`
- [ ] `./sh/board-docker.sh test` — /api/volume must answer
- [ ] Video unlisted? Verify https://youtu.be/6KtzT4xfa5k in incognito

## Devices
- [ ] iPhone queue over LAN (menu 1 + demo-queue)
- [ ] Watch queue mirror + YOUR TURN blink

## Azure (after merge)
- [ ] `alertEmail` set, image pushed to GHCR
- [ ] Deploy Bicep, note the fqdn
- [ ] `BOARD_URL=https://<fqdn> npm run test:e2e --prefix ui/board`
- [ ] Cron kill-switch installed (`crontab -l` shows it)

## Before freeze (Thu 03:00)
- [ ] Final video recorded + linked in form
- [ ] X post live + URL in form
- [ ] Ollama/Baseten numbers in README
- [ ] `./sh/submission-check.sh check` fully green
