# Holdmate – Functional Requirements (OpenSpec)

Holdmate is a voice agent that calls phone robots (speech IVRs) at Swedish public agencies for job seekers: it learns the menu, uses the right words, waits in the queue, and hands over when a person answers – with the caller in the loop for the identity check. Demo focus: anyone who is a job seeker. (Sources: docs/01–05, README.md, docs/recording-setup.md, schemas/IVR-schema.md; docs/templates/ skipped as copies.)

## Core model

- **Holdmate** – our AI voice agent; calls, picks words, waits in the queue for you.
- **Caller (you)** – the job seeker; describes the concern, approves the identity check, takes over at handover.
- **Phone robot** – the agency's speech IVR (AF Agda = the real one; the practice robot = our simulator copy).
- **Step** – one saved exchange of a call; calls are stored as steps.
- **Menu map** – map of every choice and where it leads, drawn from steps; the keyword table (keyword ↔ what it gets done) belongs to it.
- **Queue place** – the caller's number N in the queue ("Det är N samtal före dig").

Same word for the same thing everywhere; full glossary in 01.

## Capabilities

1. [Recording](recording/spec.md) – record the robot voice (v0, done).
2. [Transcription](transcription/spec.md) – Whisper speech-to-text (v0 done, used in v2).
3. [Menu map](menu-map/spec.md) – steps, keyword table, map with * (v1, v3).
4. [Practice robot](practice-robot/spec.md) – simulator of AF Agda (v1, v4).
5. [Exploration](exploration/spec.md) – Holdmate tries words, fills the map (v4).
6. [Queue alert](queue-alert/spec.md) – find queue number, alert, countdown (v2, v5).
7. [Assisted calling](assisted-calling/spec.md) – intake, identity ping, handover (after hackathon).
8. [Safety](safety/spec.md) – AI disclosure, privacy, real-line restraint (always).
9. [Real-line calling](real-line-calling/spec.md) (future) – real calls, then fully on its own.
10. [More agencies](more-agencies/spec.md) (future) – FK, union, police.
11. [Agency MCP](agency-mcp/spec.md) (future) – agencies talk to agents directly.
12. [Situation guidance](situation-guidance/spec.md) (future) – v2 wording for your situation.

## Walking skeleton slice

v1 (Thu 29 Oct): keyword table plus a mini practice robot – "One run creates a step file". Needs FN-REQ-IVR-003, FN-REQ-IVR-004, FN-REQ-IVR-006. (The source names this first slice: 04 Hackathon plan.)

## Out of scope

- iPhone app – "a Mac message is enough for now" (04, Not now).
- Holdmate talking in real calls during the hackathon – "All testing is against the practice robot" (04).
- Own sound model – listed under "Not now, on purpose" (04), no reason given.
- Moving the code to Java/Kotlin – Not now; the language choice itself is still open (04, 05).
- Checklists (caller + staff) – "Separate idea" (04).
- Email/chat instead of calling – context only; The Castle has no working chat (01).

## Open questions

About AF Agda (05, "to test in the next calls"):

- OQ-01 "Does AF Agda understand dialects and accents? Not tested yet – all calls so far used one voice."
- OQ-02 "Does saying one of its own words straight away (e.g. "ersättning") skip the yes/no step?"
- OQ-03 "Where does "jag vill prata med en handläggare" lead?"
- OQ-04 "What happens if you answer "ja" at "Stämmer det?""
- OQ-05 "What does the English branch (press 0) offer?"
- OQ-06 "What does AF Agda say about your place in the queue? We have only heard ... "Det är N samtal före dig". Try a busy time of day."
- OQ-07 "Are the example words picked at random, or do they change with the time or the caller?"

Decisions (05):

- OQ-08 "Which language for the first versions: Java/Kotlin (my long-term choice) or Python (faster this week)?"
- OQ-09 "Time estimates for each goal – the "Time to deliver" column in the Goals table is still "?"."
- OQ-10 "Is the programme I should have asked for really the Job and Development Programme – Jobb- och utvecklingsgarantin?"

Vague lines (no way to test as written):

- OQ-11 Goal 4: "Holdmate is helpful and kind, and knows the caller may be having a hard time." – how do we test kind? (NF-REQ-IVR-001 stays draft until answered.)
- OQ-12 Goal 6: "You reach a person ready and calm ... and don't have to call again" – how do we verify calm, and over how many calls?
- OQ-13 Rules: "The real phone line only a few times" – how many is "a few", and who approves each call?
- OQ-14 Legal: "who may legally act in your name ... power of attorney (fullmakt), limited delegated rights, AI disclosure and digital ID wallets" – needs input from customer/PM; blocks FN-REQ-IVR-022.
- OQ-15 Cost: "we need a phone service (like 46elks) that costs money per minute" – what budget, whose approval?
- OQ-16 Access: target group "People whose first language is not Swedish, or who have a disability ... Later" – what exactly must work for them first?

From the design research (openspec/design/IVR-domain-research-solution-concepts.md):

- OQ-17 "We have not established which IVR platform the Swedish Public Employment Service (Arbetsförmedlingen) currently uses, nor how its internal dialog logic is implemented." – research ongoing; no vendor assumptions meanwhile.
- OQ-18 "How should the agent determine whether two observations correspond to the same dialog state?" – affects the step format (FN-REQ-IVR-003) and evidence tagging (FN-REQ-IVR-029); the rest of §4 stays in the design doc for the design phase.

## Notes

- Build order = hackathon days: v1 steps/table/mini-robot → v2 Whisper + queue find + Mac alert → v3 map with * → v4 reactive robot + explore → v5 disclosure + countdown + full run → v6 demo video/README/pitch.
- The source gives no priorities (goals have no Must/Should/Could); ticket priority comes from the hackathon day order.
- Risks: paid phone minutes (46elks); the staff part of a call must be cut before storing; legal agency unclear (OQ-14).
- Tools in play: whisper.cpp (ggml-small), Mac `say`, BlackHole + ffmpeg + SwitchAudioSource, FaceTime, BankID, web widget for display (iPhone not now).
- ID note: per user request the scheme is FN-REQ-IVR-* (functional), NF-REQ-IVR-* (non-functional), US-IVR-* (stories). Non-functional requirements are captured as NF-REQ instead of open questions only.

## Traceability table

| REQ ID | Story | Source |
| --- | --- | --- |
| FN-REQ-IVR-001 | – | recording-setup.md §The idea, §5–6; 04 step 1 "Record ... on the Mac" |
| FN-REQ-IVR-002 | – | recording-setup.md §7; 04 step 1 "(Whisper)"; v2 "Whisper turns the sound into text" |
| FN-REQ-IVR-003 | US-IVR-002 | 04 step 2 "save each call as steps"; v1 "Each line is saved as a step" + "One run creates a step file" |
| FN-REQ-IVR-004 | US-IVR-001 | 01 Goal 1 done "A table maps each keyword ..."; v1 "Keyword table" |
| FN-REQ-IVR-005 | US-IVR-002 | 01 Goal 2 done "marks where you are now with a *"; v3 |
| FN-REQ-IVR-006 | – | v1 "mini practice robot that plays 3 AF Agda lines (made with say)" |
| FN-REQ-IVR-007 | – | 04 step 3 "reacts to words and key presses"; v4 'including "not understood" and yes/no' |
| FN-REQ-IVR-008 | US-IVR-003 | v4 "Holdmate picks words from the keyword table" |
| FN-REQ-IVR-009 | US-IVR-003 | 04 step 4 "tries words ... and fills in the map by itself"; 01 "a menu map that grows with every call" |
| FN-REQ-IVR-010 | US-IVR-003 | 01 Goal 3 done "reaches the right place without getting stuck in a loop"; v4 done "reaches the queue without a loop" |
| FN-REQ-IVR-011 | US-IVR-005 | v2 '"Det är N samtal före dig", "anropare nummer N"'; README.md:5 '"Din plats är : <number>"'; 02 FK evidence |
| FN-REQ-IVR-012 | US-IVR-005 | v2 "Mac alert" + "The Mac alerts at number 2"; 01 Goal 5 "get an alert near the front" |
| FN-REQ-IVR-013 | US-IVR-005 | v5 "The queue counts down"; 01 Goal 5 "know your place in the queue without listening" |
| FN-REQ-IVR-014 | US-IVR-007 | 01 "A good day": "It asks: "What's your concern?" ... chat with it or just talk to it ... in your own words" |
| FN-REQ-IVR-015 | US-IVR-007 | 01 Goal 7 done "Two ways in: write in a chat ... or click it in the menu tree and press Call. The app does the rest as far as it can." |
| FN-REQ-IVR-016 | US-IVR-007 | 01 Goal 7 "It pings you for the identity check"; "A good day" BankID approve on phone; "always done by you, never by Holdmate" |
| FN-REQ-IVR-017 | US-IVR-007 | 01 Goal 7 "pings you ... when a person answers, shows your queue number in a web widget or on your iPhone, then hands the call over to you or keeps both of you ... in the call" |
| FN-REQ-IVR-018 | US-IVR-006 | 01 Goal 6 done "with your question clear" (+ OQ-12 for the rest) |
| FN-REQ-IVR-019 | US-IVR-007 | 01 Goal 7 "The Castle is just one case – it should work for any phone line." |
| FN-REQ-IVR-020 | – | 01 Rules "Holdmate always says it is an AI (AI disclosure)"; v5 "says it is an AI"; 04 step 6 "says it is an AI" |
| FN-REQ-IVR-021 | – | 04 step 6 "The real phone line, with me – ... Holdmate talks, says it is an AI, and I do the identity check" |
| FN-REQ-IVR-022 | – | 01 "Later – fully on its own" (+ OQ-14) |
| FN-REQ-IVR-023 | – | 04 step 7; 01 Later "Försäkringskassan ... the union (facket), and the police non-emergency line (polisen, 114 14)" |
| FN-REQ-IVR-024 | – | 04 step 8 "each public agency offers an MCP server ... Holdmate talks to the agencies directly instead of the phone robots" |
| FN-REQ-IVR-025 | – | 04 step 8 "handles cases that span several agencies"; 01 "like a case moving between the unemployment fund (a-kassa) and ... (Försäkringskassan) – with you in the loop" |
| FN-REQ-IVR-026 | – | 01 "Version 2 – say the right thing for your situation" + sign-up-again example (+ OQ-10) |
| NF-REQ-IVR-001 | US-IVR-004 | 01 Goal 4 done "helpful and kind ... hard time"; v5 "talks kindly" (+ OQ-11) |
| NF-REQ-IVR-002 | – | 01 Rules "No ID numbers, staff names or staff voices in logs, demos or GitHub"; recording-setup "Cut the file where the staff member answers. No staff voices, names or personnummer in the repo, demo or logs." |
| NF-REQ-IVR-003 | – | 01 Rules "The real phone line only a few times, and only when I am there. Most testing happens against the practice robot." (+ OQ-13) |
| NF-REQ-IVR-004 | – | 01 Vision "in any language, whatever their situation"; 02 "It is even harder if Swedish is not your first language"; 05 OQ-05 |
| NF-REQ-IVR-005 | – | schemas/IVR-schema.md "112 är endast akutnummer och ska inte användas som testmål" |
| FN-REQ-IVR-027 | US-IVR-003 | design §3 knowledge-guided exploration: no-input/no-match, correction, loops/dead ends/fallbacks |
| FN-REQ-IVR-028 | US-IVR-002 | design §3: synonyms, different routes, DTMF vs speech equivalence |
| FN-REQ-IVR-029 | US-IVR-002 | design §3: observed facts / inferred hypotheses / untested possibilities; revise or reject |
| FN-REQ-IVR-030 | – | design §2 no-input, timeouts, repeated prompts; extends FN-REQ-IVR-007 |
| NF-REQ-IVR-006 | – | design §5 "limited, controlled ... avoid disrupting services or occupying human agents unnecessarily" |

## Earlier work

- The idea-check skill is not installed (load failed); a manual search found no earlier REQ IDs and no openspec/ dir – numbering starts at 001.
- docs/templates/01–05 skipped – copies of the same five docs.
- Call evidence behind the map: data/call-transcripts-by-claude, data/recordings; per-line logs named in 02 (ivr-calls-*.md).
- Seed words for new lines: schemas/IVR-schema.md, schemas/public-authority-ivr-target-seeds.json.
- Domain research + solution concept (Codex, 29 Oct): openspec/design/IVR-domain-research-solution-concepts.md – input to reqs and architecture; Target/Observed Model are hypotheses, not decisions. AF platform still unknown – no vendor assumptions.
