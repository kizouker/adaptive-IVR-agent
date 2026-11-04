# Movie script — what to say (v5, from the talk)

Same cut as `data/video/cut/silent.mp4` (2:55). Picture and timing stay;
only the words change. Built from `docs/purpose.md` and the Keynote
`docs/talk/holdmate-talk.key`.

**Rule for names:** Holdmate = the *agent* (your side).
Roksolana = the *practice copy* of the phone robot. Never mix the words.

Speed: about 2–2.5 words per second. Shorter is fine; silence is fine.

---

| Time | Seg | Picture | Say |
|---|---|---|---|
| 0:00–0:15 | A1 | Title card | Built from scratch for this hackathon, October 26 to November 4. I called the Swedish unemployment office to sign up. The robot didn't understand me, and tried to send me to parental leave. |
| 0:15–0:25 | B1 | `holdmate.sh` menu starts | So I built Holdmate: an agent that learns these phone menus. One command starts it. |
| 0:25–0:55 | B2 | Typed call: miss, then "aktivitetsrapport" | The robot only understands exact words. In AI terms it's partially observable — you never see the menu — and non-deterministic: it hears my Skåne dialect differently every time. Here I answer in my own words, and it misses. Holdmate knows the word that works: aktivitetsrapport. And I'm through. |
| 0:55–1:10 | B3 | Board follows the call | The board follows the call live: where you are in the menu, and your place in the queue. |
| 1:10–1:20 | B4 | Queue counts down, officer | Holdmate keeps track of your place in the queue. When a person answers, you take over. |
| 1:20–1:25 | B5–B6 | Watch | Mute the call. Your place in line, on your wrist. |
| 1:25–1:35 | B7 | iPhone countdown | You get a notification when it's your turn. If it's hard for me, imagine the immigrants who don't speak the exact Swedish it expects. |
| 1:35–1:50 | C1 | Holdmate practice call | I can't call the real line a hundred times. So I built Roksolana, an IVR simulator made from my real calls. Holdmate practices on her to learn the keywords. |
| 1:50–2:15 | C2 | Muse Spark live | The whole menu is a state machine: open question, options, yes or no, where you can get stuck for good, then transfer, identification, and the queue. Holdmate maps it as a rational agent, Russell and Norvig, chapter two. Meta's Muse Spark understands what the caller means. |
| 2:15–2:27 | D1 | Eval | We measure it: how often it picks the right word. |
| 2:27–2:37 | D2 | Tests | Over two hundred tests, green. |
| 2:37–2:45 | D3 | Call map | This is the map it learned: every state, and the loops you can't get out of. |
| 2:45–2:55 | E1 | End card | Today it's a simulator and an agent that learns from it. Next: a real phone line. Holdmate waits on hold, so you don't have to. |

---

## Open

- [x] Provenance line spoken + on screen in the first 10 s (Judging Workflow: disqualification risk).

- [ ] Closing line: keep "Holdmate waits on hold, so you don't have to"?
- [ ] Read it aloud once with a timer; cut words where you run over.
- [ ] Then: update captions in `data/video/cut/build_cut.py` to match.
