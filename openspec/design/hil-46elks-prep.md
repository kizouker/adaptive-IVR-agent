# Human-in-the-loop via 46elks (prep for #131)

How a human stays in the loop once Holdmate places real calls.
Code prep: `src/adaptive_ivr_agent/elks.py` (mocked tests, no creds needed).

## Primitives (from 46elks docs + llms.txt)

- `POST /calls` with `from` (our number), `to` (AF), `recordcall=true`,
  `whenhangup=<our-url>` → `{id, state}`. Basic-auth user/pass.
- `whenhangup` callback fields: `id, from, to, created, state, duration`.
- Recordings downloadable per call id (verify exact endpoint Monday).
- Bridge/transfer: connect the live call to Rickard's mobile so he takes
  over (exact action name to verify against call-actions docs Monday).

## HIL flows

1. **Approve identity.** Holdmate reaches the ID step, pauses, pushes
   "approve BankID on your phone" (Mac dialog now, iPhone push later);
   Rickard approves in his own BankID app; Holdmate resumes. No BankID
   API integration needed: the human does the human part.
2. **Take over the call.** At officer-answer (or on Rickard's command),
   bridge the live call to his mobile; he talks, Holdmate logs + learns.
3. **Abort.** Any unknown state: hang up, save transcript, alert.

## Safety rules

- Agent says it is an AI calling on Rickard's behalf (EU AI Act).
- Self-use first (Rickard's own errands, own BankID). Acting for others
  needs power of attorney — out of scope for the hackathon.
- Budget cap per test (per-minute billing); start with sub-minute calls.
- Secrets in `.env` only (see `.env.example`); check-security enforces.

## Monday checklist

- [ ] Account + 10 EUR + number + keys (Rickard).
- [ ] Smoke call to own mobile, recording downloads.
- [ ] Verify bridge/transfer + recording endpoint names with docs/support.
- [ ] First short AF call, human listening, transcript saved.
