# Tickets – Holdmate

One ticket per requirement. Each ticket carries its requirement ID as its name. Priority = hackathon day (v0 done … v5), post (after hackathon), future, always. Small enough for one work session. No GitHub issues created – only on request.

### FN-REQ-IVR-001 Record the robot voice

- REQ IDs: FN-REQ-IVR-001
- Description: Record the robot side of a call to data/recordings/robot-YYYYMMDD-HHMMSS.wav (mono 16000 Hz) and switch the sound back when done.
- Acceptance: dated wav is created; sound switches back via trap on q/Ctrl+C/normal end; file holds only the other side.
- Priority: done (v0)
- Depends on: –

### FN-REQ-IVR-002 Transcribe the newest recording

- REQ IDs: FN-REQ-IVR-002
- Description: Turn the newest wav into text with whisper-cli; save the .txt next to it and print it.
- Acceptance: Swedish by default; WHISPER_LANG=en gives English; WHISPER_LANG=auto guesses.
- Priority: done (v0)
- Depends on: –

### FN-REQ-IVR-003 Save each call as steps

- REQ IDs: FN-REQ-IVR-003
- Description: Define the step-file format and save each call/run as steps.
- Acceptance: one mini-robot run creates a step file; a hand-logged call stores as steps the map can use.
- Priority: v1 (Thu 29 Oct)
- Depends on: –

### FN-REQ-IVR-004 Keyword table

- REQ IDs: FN-REQ-IVR-004
- Description: Table mapping each keyword to what it gets done, and back ("I want X → say Y").
- Acceptance: keyword → outcome lookup works; outcome → words lookup works.
- Priority: v1 (Thu 29 Oct)
- Depends on: –

### FN-REQ-IVR-005 Menu map with position

- REQ IDs: FN-REQ-IVR-005
- Description: Draw the menu map from the steps and mark the current position with *.
- Acceptance: the * sits on the right step during a call.
- Priority: v3 (Sat 31 Oct)
- Depends on: FN-REQ-IVR-003

### FN-REQ-IVR-006 Mini robot plays three lines

- REQ IDs: FN-REQ-IVR-006
- Description: Mini practice robot playing 3 AF Agda lines made with `say`; each line saved as a step.
- Acceptance: 3 lines play; each line is saved as a step.
- Priority: v1 (Thu 29 Oct)
- Depends on: FN-REQ-IVR-003

### FN-REQ-IVR-007 Reactive robot

- REQ IDs: FN-REQ-IVR-007
- Description: Practice robot reacts to words and key presses, with "not understood" and yes/no handling.
- Acceptance: known word/key moves on; unknown input gets the not-understood line; ja/nej move on at confirm.
- Priority: v4 (Sun 1 Nov)
- Depends on: FN-REQ-IVR-006

### FN-REQ-IVR-008 Pick words from the keyword table

- REQ IDs: FN-REQ-IVR-008
- Description: Holdmate picks words from the keyword table when talking to the practice robot.
- Acceptance: at a topic step wanting X, Holdmate says the table's Y.
- Priority: v4 (Sun 1 Nov)
- Depends on: FN-REQ-IVR-004, FN-REQ-IVR-007

### FN-REQ-IVR-009 Try words and fill the map

- REQ IDs: FN-REQ-IVR-009
- Description: Holdmate tries words on the practice robot and adds each observation to the menu map.
- Acceptance: the map grows with every call.
- Priority: v4 (Sun 1 Nov)
- Depends on: FN-REQ-IVR-007

### FN-REQ-IVR-010 Reach the queue without a loop

- REQ IDs: FN-REQ-IVR-010
- Description: Full explore run reaching the right place with no loops.
- Acceptance: queue reached; no yes/no loop; no name trap.
- Priority: v4 (Sun 1 Nov)
- Depends on: FN-REQ-IVR-008, FN-REQ-IVR-009

### FN-REQ-IVR-011 Find the queue number

- REQ IDs: FN-REQ-IVR-011
- Description: Text search finding the queue number in three phrasings.
- Acceptance: "Det är 38 samtal före dig" → 38; "anropare nummer 12" → 12; "Din plats är: 47" → 47.
- Priority: v2 (Fri 30 Oct)
- Depends on: FN-REQ-IVR-002

### FN-REQ-IVR-012 Alert on the Mac near the front

- REQ IDs: FN-REQ-IVR-012
- Description: Mac alert when the queue is near the front.
- Acceptance: the Mac alerts at number 2.
- Priority: v2 (Fri 30 Oct)
- Depends on: FN-REQ-IVR-011

### FN-REQ-IVR-013 Queue counts down

- REQ IDs: FN-REQ-IVR-013
- Description: Shown queue number updates as the queue moves, without listening.
- Acceptance: place known without listening to the call.
- Priority: v5 (Mon 2 Nov)
- Depends on: FN-REQ-IVR-011

### FN-REQ-IVR-014 Intake in own words

- REQ IDs: FN-REQ-IVR-014
- Description: Holdmate asks "What's your concern?" by chat or talk; free-word answer becomes the call goal.
- Acceptance: own-words answer in chat or talk is taken as the call goal.
- Priority: post (after hackathon)
- Depends on: –

### FN-REQ-IVR-015 Two ways to start a call

- REQ IDs: FN-REQ-IVR-015
- Description: Start from chat text or from clicking the menu tree + Call; the app steers as far as it can.
- Acceptance: chat start works; menu-tree + Call start works.
- Priority: post (after hackathon)
- Depends on: FN-REQ-IVR-005

### FN-REQ-IVR-016 Identity-check ping

- REQ IDs: FN-REQ-IVR-016
- Description: Ping the caller at the identity check; caller approves on their phone (BankID); Holdmate never approves.
- Acceptance: ping fires at the identity step and Holdmate waits for the approval.
- Priority: post (after hackathon)
- Depends on: –

### FN-REQ-IVR-017 Handover when a person answers

- REQ IDs: FN-REQ-IVR-017
- Description: Buzz ("You are number 3"), show the queue number in a web widget, hand over or keep both in the call.
- Acceptance: buzz + widget + handover-or-joint-call all work. (iPhone display excluded – not now.)
- Priority: post (after hackathon)
- Depends on: FN-REQ-IVR-012, FN-REQ-IVR-013

### FN-REQ-IVR-018 Handover with a clear question

- REQ IDs: FN-REQ-IVR-018
- Description: At handover the caller's question is clear and ready.
- Acceptance: question is clear and ready at handover. (Calm/no-recall verification open – OQ-12.)
- Priority: post (after hackathon)
- Depends on: FN-REQ-IVR-014

### FN-REQ-IVR-019 Any phone line

- REQ IDs: FN-REQ-IVR-019
- Description: Assisted calls work on any trained line, not just The Castle.
- Acceptance: a newly trained line supports assisted calls.
- Priority: post (after hackathon)
- Depends on: FN-REQ-IVR-009

### FN-REQ-IVR-020 Say it is an AI

- REQ IDs: FN-REQ-IVR-020
- Description: Holdmate identifies as AI whenever it talks.
- Acceptance: disclosure line in the v5 practice run; same line scripted for real calls.
- Priority: v5 (Mon 2 Nov)
- Depends on: –

### FN-REQ-IVR-021 Real calls with the caller present

- REQ IDs: FN-REQ-IVR-021
- Description: A few real-line calls: user present, AI disclosure, user does the identity check.
- Acceptance: user present + disclosure + user-approved identity on each real call.
- Priority: future (after hackathon)
- Depends on: FN-REQ-IVR-016, FN-REQ-IVR-020, NF-REQ-IVR-003

### FN-REQ-IVR-022 Fully on its own

- REQ IDs: FN-REQ-IVR-022
- Description: End-to-end case handling; caller steps in only for identity check or to talk to a person.
- Acceptance: caller needed only where they must. (Blocked on OQ-14 legal input.)
- Priority: future
- Depends on: FN-REQ-IVR-021

### FN-REQ-IVR-023 FK, union, police

- REQ IDs: FN-REQ-IVR-023
- Description: Add Försäkringskassan, the union, and police 114 14 with the same train-map-call approach.
- Acceptance: training, mapping and assisted calling work per new line. Seeds: schemas/IVR-schema.md.
- Priority: future
- Depends on: FN-REQ-IVR-019

### FN-REQ-IVR-024 Talk through agency MCP

- REQ IDs: FN-REQ-IVR-024
- Description: Use an agency's MCP server directly instead of calling, where offered.
- Acceptance: with an MCP server available, no phone call is needed.
- Priority: future
- Depends on: – (agency-side)

### FN-REQ-IVR-025 Cases across agencies

- REQ IDs: FN-REQ-IVR-025
- Description: Handle a case moving between agencies (a-kassa → Försäkringskassan) with the caller in the loop.
- Acceptance: cross-agency case handled; caller looped in at the key steps.
- Priority: future
- Depends on: FN-REQ-IVR-024

### FN-REQ-IVR-026 Wording for your situation

- REQ IDs: FN-REQ-IVR-026
- Description: v2 – guide what to say from the caller's place in The Castle's process (needs a process model).
- Acceptance: sign-up-again case gets the right wording. (Programme name open – OQ-10.)
- Priority: future (v2)
- Depends on: FN-REQ-IVR-004

### NF-REQ-IVR-001 Helpful and kind (draft)

- REQ IDs: NF-REQ-IVR-001
- Description: Holdmate's voice is helpful and kind in the v5 full run.
- Acceptance: v5 run talks kindly. (How kindness is tested open – OQ-11.)
- Priority: v5 (Mon 2 Nov)
- Depends on: –

### NF-REQ-IVR-002 No personal data kept

- REQ IDs: NF-REQ-IVR-002
- Description: Cut recordings where staff answer; keep no ID numbers, staff names or staff voices in logs, demos or GitHub.
- Acceptance: staff part cut before storing; scan of logs/demos/repo finds none of the three.
- Priority: always (applies now)
- Depends on: –

### NF-REQ-IVR-003 Real-line restraint

- REQ IDs: NF-REQ-IVR-003
- Description: Real line only a few times with the user present; hackathon testing all on the practice robot.
- Acceptance: all hackathon tests run against the practice robot. (Count for "a few" open – OQ-13.)
- Priority: always
- Depends on: –

### NF-REQ-IVR-004 Any language (draft)

- REQ IDs: NF-REQ-IVR-004
- Description: Serve callers in any language, starting with the English branch (press 0).
- Acceptance: pressing 0 continues the call in English. (Branch content open – OQ-05.)
- Priority: future
- Depends on: –

### NF-REQ-IVR-005 Never test against 112

- REQ IDs: NF-REQ-IVR-005
- Description: Keep 112 out of all test targets, always.
- Acceptance: 112 never appears among test targets.
- Priority: always
- Depends on: –

### FN-REQ-IVR-027 Probe recovery behaviour

- REQ IDs: FN-REQ-IVR-027
- Description: Probe no-input vs no-match, correction recovery, and loops/dead ends/fallback paths.
- Acceptance: both no-input and no-match replies recorded and compared; correction recovery shown; loops/dead ends/fallbacks identified.
- Priority: post (after hackathon)
- Depends on: FN-REQ-IVR-007, FN-REQ-IVR-030

### FN-REQ-IVR-028 Verify same-state equivalence

- REQ IDs: FN-REQ-IVR-028
- Description: Check whether synonyms, different routes, and DTMF vs speech reach the same state.
- Acceptance: map records synonym equivalence, working routes per state, and DTMF/speech equivalence.
- Priority: post (after hackathon)
- Depends on: FN-REQ-IVR-009

### FN-REQ-IVR-029 Tag evidence levels in the map

- REQ IDs: FN-REQ-IVR-029
- Description: Tag map entries as observed/inferred/untested with evidence; revise or reject on counter-evidence.
- Acceptance: new observations tagged with evidence; contradicted hypotheses revised or rejected. (State identity open – OQ-18.)
- Priority: post (after hackathon)
- Depends on: FN-REQ-IVR-005

### FN-REQ-IVR-030 Handle silence and timeouts

- REQ IDs: FN-REQ-IVR-030
- Description: Practice robot answers silence with repeated no-input prompts, then times out or falls back.
- Acceptance: silence gets a repeated prompt; repeated silence times out or follows fallback.
- Priority: post (after hackathon)
- Depends on: FN-REQ-IVR-007

### NF-REQ-IVR-006 Real-system experiments stay harmless

- REQ IDs: NF-REQ-IVR-006
- Description: Every real-line experiment plan avoids human agents and service disruption; runs stay within the approved limit.
- Acceptance: plan review reaches no agent and disrupts nothing; call count within limit.
- Priority: always (applies when real-line work starts)
- Depends on: NF-REQ-IVR-003
