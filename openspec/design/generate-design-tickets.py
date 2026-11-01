#!/usr/bin/env python3
"""Generate one design ticket per requirement ticket (skill: architecture).

Output: openspec/design/tickets/DESIGN-<REQ-ID>.md (35 files).
Regenerate: python3 openspec/design/generate-design-tickets.py
Source of titles/priorities: openspec/tickets.md. Do not edit outputs by hand.
"""

from pathlib import Path

OUT = Path(__file__).parent / "tickets"

TEMPLATE = """# DESIGN-{id}: {title}

- REQ ticket: [`### {id} …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/{cap}/spec.md`](../../specs/{cap}/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`{modules}`){decisions}
- Priority: {priority}

## New or changed parts

{parts}

## Tests

{tests}
"""

TICKETS = [
    dict(id="FN-REQ-IVR-001", title="Record the robot voice", cap="recording",
         priority="done (v0)", modules="cutter (hook point only)",
         decisions=", D8", parts=[
             "- Keep `sh/record-call.sh` as is (done in v0).",
             "- NEW hook point: record the staff-answer timestamp so `cutter` (NF-REQ-IVR-002) can cut later.",
         ], tests=[
             "- Unit: trap restores the audio device on q/Ctrl+C/normal end (mock the switcher).",
             "- Client-style: run the script; dated wav exists, mono 16000 Hz, robot side only.",
             "- Integration: record → transcribe chain with FN-REQ-IVR-002.",
         ]),
    dict(id="FN-REQ-IVR-002", title="Transcribe the newest recording", cap="transcription",
         priority="done (v0)", modules="ears",
         decisions=", D5", parts=[
             "- Keep `sh/transcribe-latest.sh` as is (done in v0).",
             "- NEW `ears.transcribe(path, lang)`: whisper-cli wrapper; `WHISPER_LANG` default `sv`, `en`, `auto` as constants.",
         ], tests=[
             "- Unit: language mapping sv/en/auto (mock whisper-cli).",
             "- Client-style: newest wav → `.txt` next to it, text printed.",
             "- Integration: record → transcribe chain with FN-REQ-IVR-001.",
         ]),
    dict(id="FN-REQ-IVR-003", title="Save each call as steps", cap="menu-map",
         priority="v1 (Thu 29 Oct)", modules="steps",
         decisions=", D2", parts=[
             "- `steps.Step` / `StepFile` exist (v1) – keep the shape.",
             "- NEW: `STEPS_DIR = data/steps/` constant (Assumption A2).",
         ], tests=[
             "- Unit: save/load round-trip (exists).",
             "- Client-style: one mini-robot run creates one step file.",
             "- Integration: robot run → step file with FN-REQ-IVR-006.",
         ]),
    dict(id="FN-REQ-IVR-004", title="Keyword table", cap="menu-map",
         priority="v1 (Thu 29 Oct)", modules="keywords",
         decisions="", parts=[
             "- `keywords.KeywordTable` exists (v1) – keep two-way lookup.",
             "- NEW: save/load the table as JSON so the explorer (FN-REQ-IVR-008) can read it.",
         ], tests=[
             "- Unit: both directions + `KeyError` on unknown (exists).",
             "- Client-style: want X → say Y; said Y → get X.",
             "- Integration: table persists and reloads for the explorer.",
         ]),
    dict(id="FN-REQ-IVR-005", title="Menu map with position", cap="menu-map",
         priority="v3 (Sat 31 Oct)", modules="map, steps",
         decisions=", D3", parts=[
             "- NEW `map.py`: build states + transitions from step files; state key = normalized prompt text (Assumption A1, OQ-18 open).",
             "- NEW: position marker `*` on the current state; text rendering of the map.",
         ], tests=[
             "- Unit: steps → nodes/edges; `*` sits on the right step.",
             "- Client-style: print the map of a recorded run.",
             "- Integration: steps → map; position follows the practice robot.",
         ]),
    dict(id="FN-REQ-IVR-006", title="Mini robot plays three lines", cap="practice-robot",
         priority="v1 (Thu 29 Oct)", modules="robot, voice, steps",
         decisions=", D6", parts=[
             "- `robot.PracticeRobot` + `mac_say` exist (v1) – keep.",
             "- No changes; this ticket locks the v1 behaviour other tickets build on.",
         ], tests=[
             "- Unit: plays lines through an injected fake speaker (exists).",
             "- Client-style: `run(path)` plays 3 lines, saves 3 steps.",
             "- Integration: robot run → step file with FN-REQ-IVR-003.",
         ]),
    dict(id="FN-REQ-IVR-007", title="Reactive robot", cap="practice-robot",
         priority="v4 (Sun 1 Nov)", modules="robot, line",
         decisions=", D4", parts=[
             "- NEW `line.py`: `speak` / `listen` / `hangup` interface + fake for tests.",
             "- CHANGED `robot`: script tree (prompt → word/key → next), `not-understood` line, exact `ja`/`nej` at confirm.",
         ], tests=[
             "- Unit: known word/key moves on; unknown → not-understood; ja/nej at confirm.",
             "- Client-style: scripted conversation through the `line` interface.",
             "- Integration: explorer → line → robot round-trip.",
         ]),
    dict(id="FN-REQ-IVR-008", title="Pick words from the keyword table", cap="exploration",
         priority="v4 (Sun 1 Nov)", modules="explorer, keywords",
         decisions="", parts=[
             "- NEW `explorer.choose(state, goal)`: reads `keywords`, returns the word for goal X.",
             "- No robot changes; talks through the `line` interface.",
         ], tests=[
             "- Unit: goal X → table word Y; unknown goal → clean miss (no crash).",
             "- Client-style: at a topic step wanting X, Holdmate says Y.",
             "- Integration: explorer + keywords + practice robot reaches the next state.",
         ]),
    dict(id="FN-REQ-IVR-009", title="Try words and fill the map", cap="exploration",
         priority="v4 (Sun 1 Nov)", modules="explorer, map, knowledge",
         decisions=", D3", parts=[
             "- NEW `knowledge.py`: target model – candidate words/states (hypotheses, never facts).",
             "- CHANGED `explorer`: after each reply, append steps and add the observation to `map`.",
         ], tests=[
             "- Unit: one observation grows the map by one edge.",
             "- Client-style: explore run; map file is bigger after every call.",
             "- Integration: line → steps → map chain on the practice robot.",
         ]),
    dict(id="FN-REQ-IVR-010", title="Reach the queue without a loop", cap="exploration",
         priority="v4 (Sun 1 Nov)", modules="explorer",
         decisions="", parts=[
             "- CHANGED `explorer`: visited-set + loop guard (new word when a state repeats); exact `ja`/`nej` at confirm.",
             "- No new modules; this is the v4 end-to-end behaviour.",
         ], tests=[
             "- Unit: repeated state → different next word (loop guard).",
             "- Client-style (= integration): full run reaches the queue; no yes/no loop, no name trap.",
         ]),
    dict(id="FN-REQ-IVR-011", title="Find the queue number", cap="queue-alert",
         priority="v2 (Fri 30 Oct)", modules="queue, ears",
         decisions=", D7", parts=[
             "- NEW `queue.find_number(text)`: pattern table constant with the 3 known phrasings; returns int or None.",
             "- Input text comes from `ears` transcripts.",
         ], tests=[
             "- Unit: each phrasing → 38/12/47; no match → None.",
             "- Client-style: transcript file → queue number.",
             "- Integration: ears transcript → queue number.",
         ]),
    dict(id="FN-REQ-IVR-012", title="Alert on the Mac near the front", cap="queue-alert",
         priority="v2 (Fri 30 Oct)", modules="alert, queue",
         decisions="", parts=[
             "- NEW `alert.notify(n)`: Mac notification via osascript (Assumption A3).",
             "- NEW: `ALERT_AT = 2` threshold constant.",
         ], tests=[
             "- Unit: fires at ≤ 2, silent above (mock the notifier).",
             "- Client-style: queue number 2 → the Mac buzzes.",
             "- Integration: queue → alert chain.",
         ]),
    dict(id="FN-REQ-IVR-013", title="Queue counts down", cap="queue-alert",
         priority="v5 (Mon 2 Nov)", modules="queue, alert",
         decisions="", parts=[
             "- CHANGED `queue`: track the last number across polls; report only on change.",
             "- CHANGED `alert`: expose the current number as display data (for the widget, FN-REQ-IVR-017).",
         ], tests=[
             "- Unit: decreasing polls update; repeats don't re-alert.",
             "- Client-style: simulated countdown 5 → 2 without listening.",
             "- Integration: ears → queue → alert display data.",
         ]),
    dict(id="FN-REQ-IVR-014", title="Intake in own words", cap="assisted-calling",
         priority="post (after hackathon)", modules="intake",
         decisions="", parts=[
             "- NEW `intake.goal_from_text(text)`: chat message → call goal. Talk input later, same return type.",
         ], tests=[
             "- Unit: free-word text → goal object.",
             "- Client-style: chat 'I need to sign up again' → goal taken.",
             "- Integration: intake goal starts an explorer run.",
         ]),
    dict(id="FN-REQ-IVR-015", title="Two ways to start a call", cap="assisted-calling",
         priority="post (after hackathon)", modules="intake",
         decisions="", parts=[
             "- CHANGED `intake`: chat start (014) + menu-tree + Call start (clicked node id → goal). Both yield the same goal type.",
         ], tests=[
             "- Unit: both starts produce equal goals for the same need.",
             "- Client-style ×2: chat start works; tree-click + Call works.",
             "- Integration: either start → explorer steers as far as it can.",
         ]),
    dict(id="FN-REQ-IVR-016", title="Identity-check ping", cap="assisted-calling",
         priority="post (after hackathon)", modules="handover",
         decisions="", parts=[
             "- NEW `handover.ping_identity()`: pings the caller, waits for approval. No code path may approve – assert this.",
         ], tests=[
             "- Unit: ping fires at the identity step; run blocks until approval.",
             "- Client-style: simulated approve → run resumes.",
             "- Safety test: no auto-approve path exists (static check + test).",
         ]),
    dict(id="FN-REQ-IVR-017", title="Handover when a person answers", cap="assisted-calling",
         priority="post (after hackathon)", modules="handover, alert",
         decisions="", parts=[
             "- CHANGED `handover`: buzz text constant ('You are number 3'); handover-or-joint-call flag.",
             "- CHANGED `alert`: queue-number JSON payload for the web widget. iPhone display excluded.",
         ], tests=[
             "- Unit: widget payload shape {line, number, state}.",
             "- Client-style: person answers → buzz + widget data + handover.",
             "- Integration: queue → alert → handover chain.",
         ]),
    dict(id="FN-REQ-IVR-018", title="Handover with a clear question", cap="assisted-calling",
         priority="post (after hackathon)", modules="intake, handover",
         decisions="", parts=[
             "- CHANGED `intake`: `summarise(goal, steps)` → one-line question for the handover. (Calm/no-recall check open – OQ-12.)",
         ], tests=[
             "- Unit: goal + steps → single clear question line.",
             "- Client-style: at handover the question is ready.",
             "- Integration: intake summary reaches the handover.",
         ]),
    dict(id="FN-REQ-IVR-019", title="Any phone line", cap="assisted-calling",
         priority="post (after hackathon)", modules="map, knowledge, explorer",
         decisions="", parts=[
             "- CHANGED: per-line files `data/maps/<line>.json`; `explorer` takes a line parameter. Same train-map-call loop.",
         ], tests=[
             "- Unit: two lines keep separate maps.",
             "- Client-style: newly trained line supports an assisted call.",
             "- Integration: full per-line loop on a second script.",
         ]),
    dict(id="FN-REQ-IVR-020", title="Say it is an AI", cap="safety",
         priority="v5 (Mon 2 Nov)", modules="voice",
         decisions=", D6", parts=[
             "- CHANGED `voice`: `DISCLOSURE_LINE` constant, prepended to every utterance; real-call script uses the same line.",
         ], tests=[
             "- Unit: every `speak()` output contains the disclosure line.",
             "- Client-style: v5 practice run script includes disclosure.",
             "- Integration: voice → line output always discloses.",
         ]),
    dict(id="FN-REQ-IVR-021", title="Real calls with the caller present", cap="real-line-calling",
         priority="future (after hackathon)", modules="line, guard, voice",
         decisions=", D4, D9", parts=[
             "- NEW `line.RealLineAdapter`: phone-service API (46elks is an option, OQ-15) behind the `line` interface.",
             "- CHANGED `guard`: real-line budget check before every call (NF-REQ-IVR-003).",
         ], tests=[
             "- Unit: adapter maps speak/listen (mock service).",
             "- Client-style: scripted call against the mock.",
             "- No CI integration test against the real line – manual checklist: user present + disclosure + user identity check.",
         ]),
    dict(id="FN-REQ-IVR-022", title="Fully on its own", cap="real-line-calling",
         priority="future", modules="handover",
         decisions="", parts=[
             "- BLOCKED on OQ-14 (legal agency). Design only: policy table of which steps need a human; default = human needed.",
         ], tests=[
             "- Deferred until OQ-14 is answered; no code in this ticket.",
         ]),
    dict(id="FN-REQ-IVR-023", title="FK, union, police", cap="more-agencies",
         priority="future", modules="knowledge, explorer, map",
         decisions="", parts=[
             "- NEW: `SEED_WORDS` constants per line from `schemas/IVR-schema.md`; same train-map-call loop as 019. Never 112 (NF-REQ-IVR-005).",
         ], tests=[
             "- Unit per line: seeds load and train a first map.",
             "- Client-style per line: training, mapping, assisted call work.",
             "- Integration per line on that line's script.",
         ]),
    dict(id="FN-REQ-IVR-024", title="Talk through agency MCP", cap="agency-mcp",
         priority="future", modules="mcp, explorer",
         decisions=", D11", parts=[
             "- NEW `mcp.client`: stdio MCP client; `explorer` picks MCP route when a server is offered, else dials.",
         ], tests=[
             "- Unit: client calls against a mock MCP server.",
             "- Client-style: case via MCP; assert no phone call was placed (line untouched).",
             "- Integration: end-to-end case against the mock server.",
         ]),
    dict(id="FN-REQ-IVR-025", title="Cases across agencies", cap="agency-mcp",
         priority="future", modules="mcp, handover",
         decisions=", D11", parts=[
             "- CHANGED `mcp`: multi-server session (case moves a-kassa → Försäkringskassan).",
             "- CHANGED `handover`: loops the caller in at the key steps.",
         ], tests=[
             "- Unit: case state survives a server switch (mock servers).",
             "- Client-style: cross-agency case handled; caller looped in.",
             "- Integration: two-mock-server flow end-to-end.",
         ]),
    dict(id="FN-REQ-IVR-026", title="Wording for your situation", cap="situation-guidance",
         priority="future (v2)", modules="guide, keywords",
         decisions="", parts=[
             "- NEW `guide.wording(situation)`: situation → script, backed by a process-model data file (programme name open – OQ-10).",
         ], tests=[
             "- Unit: sign-up-again situation → the right wording.",
             "- Client-style: situation in → speakable script out.",
             "- Integration: guide → keywords → explorer uses the wording.",
         ]),
    dict(id="FN-REQ-IVR-027", title="Probe recovery behaviour", cap="exploration",
         priority="post (after hackathon)", modules="explorer, map",
         decisions="", parts=[
             "- CHANGED `explorer`: probe plan – no-input vs no-match, correction recovery, loops/dead ends/fallbacks.",
             "- CHANGED `map`: marks fallback paths, loops and dead ends.",
         ], tests=[
             "- Unit: probe matrix recorded per prompt.",
             "- Client-style: scripted probe run on the practice robot.",
             "- Integration: robot → explorer → map fallback paths.",
         ]),
    dict(id="FN-REQ-IVR-028", title="Verify same-state equivalence", cap="exploration",
         priority="post (after hackathon)", modules="map, knowledge",
         decisions="", parts=[
             "- CHANGED `map`: equivalence sets – synonyms, working routes per state, DTMF ≈ speech.",
             "- CHANGED `knowledge`: equivalence hypotheses to confirm or reject.",
         ], tests=[
             "- Unit: equivalent observations merge to one state.",
             "- Client-style: synonym run reaches the same node.",
             "- Integration: map records the equivalence with evidence.",
         ]),
    dict(id="FN-REQ-IVR-029", title="Tag evidence levels in the map", cap="menu-map",
         priority="post (after hackathon)", modules="map",
         decisions=", D3", parts=[
             "- CHANGED `map`: every entry tagged `observed` / `inferred` / `untested` + source step; counter-evidence revises or rejects. (State identity open – OQ-18.)",
         ], tests=[
             "- Unit: tag transitions; counter-evidence revises, never silently overwrites.",
             "- Client-style: map dump shows tags + sources.",
             "- Integration: explorer observations arrive tagged.",
         ]),
    dict(id="FN-REQ-IVR-030", title="Handle silence and timeouts", cap="practice-robot",
         priority="post (after hackathon)", modules="robot, line",
         decisions="", parts=[
             "- CHANGED `robot`: silence → repeated no-input prompts, then timeout or fallback.",
             "- CHANGED `line.listen`: timeout parameter.",
         ], tests=[
             "- Unit: silence → repeated prompt → timeout/fallback.",
             "- Client-style: silent run against the practice robot.",
             "- Integration: explorer silence experiment → map fallback.",
         ]),
    dict(id="NF-REQ-IVR-001", title="Helpful and kind (draft)", cap="assisted-calling",
         priority="v5 (Mon 2 Nov)", modules="voice",
         decisions="", parts=[
             "- CHANGED `voice`: `KIND_LINES` constants – fixed kind phrasings in the v5 run. Draft stays: no kindness metric (OQ-11).",
         ], tests=[
             "- Scripted-test: the fixed kind lines are spoken in the v5 run.",
             "- No behaviour metric until OQ-11 is answered.",
         ]),
    dict(id="NF-REQ-IVR-002", title="No personal data kept", cap="safety",
         priority="always (applies now)", modules="cutter",
         decisions=", D5, D8", parts=[
             "- NEW `cutter.cut(wav, staff_at)`: cuts staff audio before storing.",
             "- NEW: PII pattern list (ID numbers, staff names) for a repo/log/demo scan in CI.",
         ], tests=[
             "- Unit: cut removes everything from the staff timestamp on.",
             "- Client-style: record → cut → store; stored file holds no staff audio.",
             "- Integration: CI scan of logs/demos/repo finds none of the three.",
         ]),
    dict(id="NF-REQ-IVR-003", title="Real-line restraint", cap="safety",
         priority="always", modules="guard",
         decisions=", D4, D9", parts=[
             "- NEW `guard` real-line counter + budget constant (count open – OQ-13).",
             "- CI rule: tests never import the real-line adapter (practice robot only).",
         ], tests=[
             "- Unit: budget exceeded → call refused.",
             "- Repo test: no real-line import anywhere under `tests/`.",
         ]),
    dict(id="NF-REQ-IVR-004", title="Any language (draft)", cap="assisted-calling",
         priority="future", modules="robot, ears, voice",
         decisions="", parts=[
             "- CHANGED `robot`: English branch (press 0). CHANGED `ears` (language param) and `voice` (English lines). Branch content open – OQ-05.",
         ], tests=[
             "- Unit: press 0 → English node.",
             "- Client-style: full run continues in English.",
         ]),
    dict(id="NF-REQ-IVR-005", title="Never test against 112", cap="safety",
         priority="always", modules="guard",
         decisions=", D9", parts=[
             "- NEW `guard.DENYLIST` constant including `112`; checked on every dial.",
         ], tests=[
             "- Unit: 112 refused in every dialling path.",
             "- Repo test: 112 never appears among test targets.",
         ]),
    dict(id="NF-REQ-IVR-006", title="Real-system experiments stay harmless", cap="safety",
         priority="always (when real-line work starts)", modules="guard",
         decisions=", D9", parts=[
             "- CHANGED `guard`: experiment-plan review – a plan that can reach a human agent or disrupt service is rejected; call count within the approved limit.",
         ], tests=[
             "- Unit: agent-reaching plan → rejected; over-limit run → refused.",
             "- Client-style: plan review passes only for harmless plans.",
         ]),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for t in TICKETS:
        body = TEMPLATE.format(
            id=t["id"], title=t["title"], cap=t["cap"], priority=t["priority"],
            modules=t["modules"], decisions=t["decisions"],
            parts="\n".join(t["parts"]), tests="\n".join(t["tests"]),
        )
        (OUT / f"DESIGN-{t['id']}.md").write_text(body, encoding="utf-8")
    print(f"Wrote {len(TICKETS)} tickets to {OUT}")


if __name__ == "__main__":
    main()
