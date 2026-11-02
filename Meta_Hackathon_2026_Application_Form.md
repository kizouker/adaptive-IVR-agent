# Meta Hackathon 2026 — Application Draft

## Event

| Field | Details |
|---|---|
| Organizer | Cerebral Valley |
| Event | [Meta AI Developer Hackathon](https://cerebralvalley.ai/e/meta-ai-developer-hackathon) |
| Deadline | Oct 26, 6:00 PM – Nov 5, 3:00 AM (GMT+1) |

---

## Short Answers

| Question | Answer |
|---|---|
| What's your LinkedIn? | <https://www.linkedin.com/in/rickardaberg> |
| What's your Twitter/X? | — |
| What's your Github? | <https://github.com/kizouker> |
| Where do you live (City, State, Country)? | Malmö, Sweden |
| Startup track or indie dev track? | Indie Dev Track |
| Where do you study or work? | Linnaeus University |

---

## 1. What do you want to build for this hackathon?

### The problem

Government phone lines in Sweden (employment service, social insurance
agency, police non-emergency) are run by voice robots. They only understand
exact words, often in a specific accent, and nobody tells you which words
work. If you say something else, the robot repeats "answer yes or no" again
and again. Then you wait in long queues and have to keep listening so you
don't miss your turn.

This hits the people who need help most: unemployed people under stress,
non-native speakers, people with ADHD or disabilities, and people who can't
speak loudly because of where they are.

### What I want to build

An AI agent that handles these phone lines for you.

1. **Map the menu** — the agent calls the line, tries different answers,
   learns from what happens, and builds a map of the whole menu: what you
   can say and where it leads. This makes a hidden system visible.
2. **Wait for you** — it uses the map to reach the right place and waits in
   the queue. An iPhone app shows your queue number and alerts you when
   you're next, so you can take over the call.
3. **Later: speak for you** — the agent says it's an AI calling on your
   behalf, and you approve it with BankID, Sweden's national digital ID.
   A human stays in the loop.

### What it solves

No more guessing the right words, no more hours of hold music, and equal
access for people who struggle with voice robots.

### How

The calls go through a phone API (46elks, a Swedish telephony service, or
Twilio), which lets the code place calls, hear the audio, and answer with
speech or button presses. I'd use Muse Spark to understand the menu prompts
and decide what to say next, and Meta's speech-to-text for the robot voice.
I already have a recorded call through the full menu to start from.

---

## 2. Tell us about an AI project you recently built

**`swedish-jobs-mcp`** — an MCP server that lets AI assistants
search live Swedish job ads from Arbetsförmedlingen's JobTech API.

- Written in Python, published on PyPI (`v0.1.1`) and open source on GitHub.
- I designed the tools the AI model calls, wrapped the public REST API, and
  handled packaging and release.
- Next step: a Java / Spring Boot version deployed to Azure with
  GitHub Actions.

Links:

- PyPI: `swedish-jobs-mcp v0.1.1`
- GitHub: <https://github.com/kizouker>

---

## Build status (checked 2026-11-01)

What the application promised vs what is built. Evidence links to code,
data, or tickets in this repo.

| # | Application claim | Status | Evidence |
|---|---|---|---|
| 1 | Map the menu: agent calls, tries answers, learns, builds a map | ✅ in sim | `src/adaptive_ivr_agent/explorer.py` (BFS), `menu_map.py` (FSM), `data/holdmate-lessons.jsonl`, coverage matrix (#90), board flow graph |
| 2 | Wait for you: reach the right place via the map, wait in queue | 🟡 partial | `queue.py` + countdown + ticket widget, handover DTMF (`tones.py`); iPhone app is wishlist (#100) |
| 3 | Later: speak for you, BankID approval, human in the loop | ⬜ later | Sim only: faked-ID step + BankID/Freja digits in talk flow; human-in-the-loop at identity by design |
| 4 | Calls via 46elks or Twilio | ⏸ paused | Backlog ticket; sim only for now |
| 5 | Muse Spark understands prompts, decides next answer | 🟡 partial | Exact/keyword matching (`classify.py`); no LLM in the loop yet |
| 6 | Meta speech-to-text for the robot voice | ⬜ not yet | macOS `say` voices only (Alva/Oskar) |
| 7 | A recorded call through the full menu to start from | ✅ have it | `data/call-transcripts/`, `data/doorkeeper-lines.json` L01–L43; more sampling Monday (#106) |
