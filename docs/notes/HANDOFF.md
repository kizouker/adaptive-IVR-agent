# Handoff — read this + state.json first (2026-11-04 ~21:30 CET)

Rickard ran /clear. Long session behind; everything below is verified this session.

## Main (submit from here)
- Merged today: #227 replay, R1 #231, R2 #232, R3 #233, #225 STT, #226 Spark cap, #234 Upptaget-nod, #243 EN lessons, #244 Claude video-link, #245 female EN voice. Suite 310+ green, CI green. v0.4.2 amiga shipped; v0.4.3 amiga500 milestone (#13) open, #132 closed in it.
- Rule (Rickard-approved): green = merge, red = fix first, unfinished = draft.

## Audio (the hard part)
- Chain proven: pure BlackHole 2ch clean (-91 dB floor, ping -10.6 dB). Real call records with sound (-31.6 dB).
- #237 OPEN (call audio never reaches BlackHole reliably) blocks #236.
- #236 draft (t2): record-call IVR + call_cli, CI green, DO NOT MERGE until #237 done.
- #239 verdict posted (no main→t2 merge); Rickard closes.
- Device scheme: IVR_Output_Speakers / IVR_Input_Record (NOT OUT_BH_MBP; #235 holds that proposal).

## In flight (unfinished!)
- /tmp/devnames worktree (from main ed2d3c8): device renames talk.sh+audio.py+tests. EDITS DONE, NOT verified/committed/PR'd. Verify: shellcheck + pytest tests/test_talk_startup.py tests/test_airpods.py tests/test_audio.py, then PR.
- Fresh record-call branch from main (Claude's simpler option): NOT started. Would supersede #236 (needs Rickard's word to close #236).
- t2 tree: working tree = savepoint content; remote savepoint t2-savepoint-20261104 has it all. Local t2 1 ahead of origin/t2 (intentional, keeps #236 scope).

## Standing rules
- Swedish in chat, code/comments English. Max ~10 lines per reply.
- Click-copy-code: one command per bash block, real values, repo root, bash tag.
- No ticket no work. Nothing merges/tags without his explicit word. No Docker.
- AgentChute: I'm muse (meta). Claude lane stale/gone; file handoffs in docs/talk/ work.
- Tired mode was ON: Rickard exhausted, keep replies minimal.
