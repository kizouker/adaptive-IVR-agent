# Holdmate — 3-minute submission video script (v2, judging blueprint)

Total ≤ 2:55. English voiceover + burned-in captions. Demo voices: Roksolana = Alva,
caller = Oskar, officer = Klara. No slides: 80%+ live product.

## 0:00–0:15 Hook & provenance (15s)

> "Sweden's phone robots only understand exact words — nobody tells you which.
> Holdmate learns them for you. Built from scratch Oct 26 to Nov 4 — repo
> predates the window with audio experiments only."

VISUAL: title card + on-screen provenance callout (same sentence, first 10s).

## 0:15–1:35 Live walkthrough (80s)

One command starts everything: `./sh/holdmate.sh` (menu item 1).

- **Talk (0:15–0:55):** live call against Roksolana (The Castle sim): open
  question → keyword → yes/no → faked ID → queue ticket counting down →
  handover beeps. Show the queue ticket big.
- **Board (0:55–1:15):** every turn lands on the live board: call thread,
  mapped state, learned keywords, queue place. Show telemetry panel: each
  Meta model call with model name + latency, visible on screen.
- **iPhone + Watch (1:15–1:35):** YOUR TURN alert mirrors to iPhone and Watch
  over LAN. Show 0-place blink + beep.

## 1:35–2:15 Meta AI architecture (40s)

> "Under the hood: an intent ladder — exact match, then Muse Spark over
> api.meta.ai for live normalization, then Muse Spark Open as the
> load-bearing open-weight stage, local or partner-hosted. Every call is
> logged with model, runtime, and latency."

VISUAL: block diagram Spark + Spark Open + provenance log tail; eval A/B
`eval/llm_intent_eval.py --live` vs `--openweight` (shortened, 4x SPEED ok).

## 2:15–2:45 Benchmarks & proof (30s)

On-screen cards, read aloud:

- 212 tests green + e2e queue spec, CI + CodeQL passing
- Rescue/abstain safety eval: adversarial cases never mis-transfer
- One-command keyless replay: `./sh/holdmate.sh` (no keys, no login)

VISUAL: pytest tail, eval output, GitHub Actions green.

## 2:45–2:55 Summary & clean stop (10s)

Card: repo URL, models used (Muse Spark + Spark Open), headline metrics.

> "Holdmate waits on hold, so you don't have to."

Stop at 2:55. Nothing after — playback cuts at 3:00.
