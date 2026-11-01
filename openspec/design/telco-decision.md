# Telco decision: 46elks vs FaceTime/tel: + BlackHole

Decision: **46elks for real calls; FaceTime/tel: only as a human-present demo fallback.**
Context: #131 (Monday real-call test). Researched overnight Nov 1-2.

## FaceTime/tel: + BlackHole path

- `tel:` URLs open FaceTime and can dial via iPhone cellular relay
  (same Apple ID + Wi-Fi + carrier; iPhone nearby and charged).
- BlackHole (already installed) can capture call audio through a
  multi-output device; FaceTime input/output are TWAIN-style pickers.
- **Blockers:** no programmatic dial/answer/hangup API; every dial shows
  a user confirmation; depends on a nearby iPhone; no inbound numbers,
  no DTMF injection, fragile recording.
- Verdict: viable for a hackathon demo **with Rickard present**, not a
  replacement for 46elks. Keep as Plan B for the video if 46elks stalls.

## 46elks path (chosen)

- Real API: outbound calls, inbound numbers, `recordcall=true`,
  `whenhangup` callbacks, per-started-minute billing (~0.30 SEK/min),
  numbers ~12 SEK/month (Nov 2026 pricing, verify Monday).
- Deterministic, scriptable, recordable, bridgeable (human take-over).
- Needs: Rickard creates the account + tops up 10 EUR + provisions a
  number (only he can do this). See `hil-46elks-prep.md`.

## Monday order

1. Rickard: account, top-up, number, API keys into `.env`.
2. Smoke: `elks.py` places a 30s call to Rickard's own mobile.
3. Short AF call with `recordcall=true`, human listening in.
4. Longer queue test only after 1-3 are green.
