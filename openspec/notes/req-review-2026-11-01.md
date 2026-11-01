# Requirements completion review – 2026-11-01

Role: Requirements analyst (process steps 1–2). Read-only review; no code, ticket, or process edits made.

Sources read: `.agents/process/PROCESS.MD`, `.agents/process/003_REQUIREMENTS.MD`,
`.agents/process/007_TEST.MD`, all 12 `openspec/specs/*/spec.md` files, all 12
`features/*.feature` files, `openspec/tickets.md`, `sh/make-tickets.sh`,
`sh/check-reqs.sh`, GitHub issues #3–#48 (read-only `gh issue view`), `src/`,
`tests/`, `sh/`, `data/` listings plus header greps.

## Gate verdict (PROCESS.MD: no design/code before all three exist)

1. Vision – exists (`docs/01_Vision _Adaptive_IVR_agent.md`, not re-reviewed here).
2. Requirement = GitHub issue with Gherkin and IDs, approved by Rickard – **FAILS**.
   All 36 requirements have an issue, but 0 of 36 issues contain Gherkin and 0 carry
   scenario IDs. No `req` label on any issue (proposal in 003).
3. Test cases in 007_TEST.MD, dry-tested – **FAILS**. `007_TEST.MD` holds no test
   cases and no scenario-to-test mapping exists anywhere. Only 5 of 36 requirements
   have pytest coverage, written test-first alongside code (step 4 style), not as a
   step-2 dry test.

Per the gate rule, the missing items are: Gherkin + scenario IDs in the GitHub
issues, and dry-test cases per scenario.

## Counts

- Total requirements: **36** (FN-REQ-IVR-001..030, NF-REQ-IVR-001..006), **57** scenarios.
- (a) Spec + Gherkin exist: **36/36** (spec.md section + `@ID`-tagged feature scenarios;
  `sh/check-reqs.sh` enforces this pairing).
- (b) GitHub ticket exists: **36/36** (issues #3–#38, titled T-001..T-036). With Gherkin: **0/36**.
- (c) Dry-test mapping per 007_TEST.MD (one pytest test per scenario + falsifiability
  check): **0/36 fully**; pytest files exist for **5/36** (FN-003, 004, 005, 006, 007),
  none mapped per scenario.
- (d) Implemented: **7/36** – FN-001 (`sh/record-call.sh`), FN-002
  (`sh/transcribe-latest.sh`), FN-003 (`src/adaptive_ivr_agent/steps.py`), FN-004
  (`keywords.py`), FN-005 (`menu_map.py`), FN-006 (`robot.py`), FN-007 (`reactive.py`).
- Extra work tickets without a parent REQ: T-037..T-046 (issues #39–#48).

## Per-requirement table

Columns: S = # scenarios in spec+feature (match checked by reading both) · G = Gherkin
in spec+feature · T = GitHub ticket (# + T-tag) · D = dry-test mapping (scenario→test,
falsifiable) · I = implemented (trace) · INVEST/testability note.

| REQ | S | G | T | D | I | INVEST / testability |
|---|---|---|---|---|---|---|
| FN-REQ-IVR-001 Record the robot voice | 3 | yes | #3 T-001 | NO – no tests at all | YES `sh/record-call.sh` (+`check-recording.sh`,`switchaudio.sh`) | Testable in principle (file exists, trap, mic exclusion); "only the other side" needs a defined check. Marked done (v0) with zero tests. |
| FN-REQ-IVR-002 Transcribe the newest recording | 3 | yes | #4 T-002 | NO – no tests | YES `sh/transcribe-latest.sh` | Testable (file + lang flag); "prints it, in Swedish" is checkable. Done (v0), zero tests. |
| FN-REQ-IVR-003 Save each call as steps | 2 | yes | #5 T-003 | PARTIAL – `tests/test_steps.py` + `test_v1_flow.py`, no per-scenario map | YES `src/adaptive_ivr_agent/steps.py` | Small, testable. "Hand-logged call" scenario depends on manual input format – negotiable. |
| FN-REQ-IVR-004 Keyword table | 2 | yes | #6 T-004 | PARTIAL – `tests/test_keywords.py`, no per-scenario map | YES `keywords.py` | Independent, testable both directions. |
| FN-REQ-IVR-005 Menu map with position | 1 | yes | #7 T-005 | PARTIAL – `tests/test_menu_map.py` | YES `menu_map.py` (+`sh/show-map.sh`,`watch-map.sh`) | Testable ("*" position). Depends on 003 – fine. |
| FN-REQ-IVR-006 Mini robot plays three lines | 2 | yes | #8 T-006 | PARTIAL – `tests/test_practice_robot.py` (+`test_v1_flow.py`) | YES `robot.py` (+`sh/demo-robot.sh`) | Small, testable. `say` dependency is Mac-only – estimable risk, handled via injected sound in tests. |
| FN-REQ-IVR-007 Reactive robot | 3 | yes | #9 T-007 | PARTIAL – `tests/test_reactive.py` | YES `reactive.py` (extended under T-044 personas) | Testable; "known word" set is open-ended (grows via T-038/T-044) – boundary needs pinning. |
| FN-REQ-IVR-008 Pick words from the keyword table | 1 | yes | #10 T-008 | NO | NO (no explorer code in `src/`) | Testable (X→Y lookup at runtime) but needs 004+007 – dependent, ok. |
| FN-REQ-IVR-009 Try words and fill the map | 1 | yes | #11 T-009 | NO | NO | "Map grows" is testable; needs a falsifiable growth assertion (which entry, after which turn). |
| FN-REQ-IVR-010 Reach the queue without a loop | 1 | yes | #12 T-010 | NO | NO | WEAK: "the right place" undefined; "no name trap" undefined; loop bound (max turns?) missing. Not falsifiable as written. |
| FN-REQ-IVR-011 Find the queue number | 3 | yes | #13 T-011 | NO | NO (no queue-parsing code found) | Strong: three concrete input→output pairs. Independent, small, testable. |
| FN-REQ-IVR-012 Alert on the Mac near the front | 1 | yes | #14 T-012 | NO | NO | Testable if "alerts" is pinned (notification? sound?). "Near the front" vs fixed 2 – pick one. |
| FN-REQ-IVR-013 Queue counts down | 1 | yes | #15 T-013 | NO | NO (`live_view.py` shows turns/map under T-045, not queue countdown) | WEAK: "shown number updates without listening" – shown where? Needs an observable. |
| FN-REQ-IVR-014 Intake in own words | 1 | yes | #16 T-014 | NO | NO (post-hackathon) | "Takes it as the call goal" needs an observable (stored where? echoed?). |
| FN-REQ-IVR-015 Two ways to start a call | 2 | yes | #17 T-015 | NO | NO (post-hackathon) | "Steers as far as it can" is vague – needs a boundary (handover point). Two scenarios ok, one req still small. |
| FN-REQ-IVR-016 Identity-check ping | 1 | yes | #18 T-016 | NO | NO (post-hackathon) | Testable (ping fires, waits). "Never approves" is a negative – needs a positive check (no approval API path). |
| FN-REQ-IVR-017 Handover when a person answers | 1 | yes | #19 T-017 | NO | NO (post-hackathon) | NOT SMALL: buzz + widget + handover-or-joint in one scenario; "or" makes it untestable as one case – split into 2–3 scenarios. |
| FN-REQ-IVR-018 Handover with a clear question | 1 | yes | #20 T-018 | NO | NO (post-hackathon) | WEAK: "clear and ready" not operationalised (OQ-12 open). Not testable yet. |
| FN-REQ-IVR-019 Any phone line | 1 | yes | #21 T-019 | NO | NO (post-hackathon) | Testable once "trained" is defined (which artefacts = trained?). Depends on 009. |
| FN-REQ-IVR-020 Say it is an AI | 2 | yes | #22 T-020 | NO | NO (no disclosure string in `src/`) | Testable (exact line present in output). Line wording not yet fixed – fix it. |
| FN-REQ-IVR-021 Real calls with the caller present | 1 | yes | #23 T-021 | NO | NO (future; T-040 46elks is BACKLOG/paused) | Testable per call (present + disclosure + user identity). "Few" inherits OQ-13. |
| FN-REQ-IVR-022 Fully on its own | 1 | yes | #24 T-022 | NO | NO (future, blocked OQ-14 legal) | Not estimable/negotiable until OQ-14 closes – correctly parked. |
| FN-REQ-IVR-023 FK, union, police | 1 | yes | #25 T-023 | NO | NO (future) | Bundles 3 lines in one req – NOT SMALL; split per line when scheduled. |
| FN-REQ-IVR-024 Talk through agency MCP | 1 | yes | #26 T-024 | NO | NO (future, agency-side dep) | Testable (no call placed when MCP used). External dependency – not independent, correctly parked. |
| FN-REQ-IVR-025 Cases across agencies | 1 | yes | #27 T-025 | NO | NO (future) | "Caller in the loop" needs loop-in points defined. Depends on 024. |
| FN-REQ-IVR-026 Wording for your situation | 1 | yes | #28 T-026 | NO | NO (future v2, OQ-10 open) | Testable once the process model + keyword exist; currently blocked on OQ-10. |
| FN-REQ-IVR-027 Probe recovery behaviour | 3 | yes | #34 T-032 | NO | NO (post-hackathon) | Strong Given/When/Then; testable against the practice robot. Depends on 007+030 – 030 unbuilt. |
| FN-REQ-IVR-028 Verify same-state equivalence | 3 | yes | #35 T-033 | NO | NO (post-hackathon) | Testable but needs a state-identity rule (see OQ-18 on 029) or "same state" is uncheckable. |
| FN-REQ-IVR-029 Tag evidence levels in the map | 2 | yes | #36 T-034 | NO | NO (post-hackathon) | Testable (tag values enumerated). State identity open (OQ-18). |
| FN-REQ-IVR-030 Handle silence and timeouts | 2 | yes | #37 T-035 | NO | NO (post-hackathon; practice-robot change) | Testable (prompt repeats N times, then timeout/fallback). Counts/thresholds need pinning. |
| NF-REQ-IVR-001 Helpful and kind (draft) | 1 | yes | #29 T-027 | NO | NO | NOT TESTABLE as written (OQ-11 open: how is kindness tested?). Draft status correct – do not build. |
| NF-REQ-IVR-002 No personal data kept | 2 | yes | #30 T-028 | NO | NO ("always" rule; no cut script or scan found) | Testable: cut-point rule + a repo-scan check could be automated. "Cut there" needs a precise cut point. |
| NF-REQ-IVR-003 Real-line restraint | 1 | yes | #31 T-029 | NO | process rule, not code | "A few" undefined (OQ-13) – needs a number before it can be verified. |
| NF-REQ-IVR-004 Any language (draft) | 1 | yes | #32 T-030 | NO | NO (future, OQ-05 open) | Draft correct; "any language" untestable, English-branch slice testable once OQ-05 closes. |
| NF-REQ-IVR-005 Never test against 112 | 1 | yes | #33 T-031 | NO | process rule; repo grep finds 112 only in `make-tickets.sh` text + this review's scope | Testable (grep test targets). Could be a CI check. |
| NF-REQ-IVR-006 Real-system experiments stay harmless | 2 | yes | #38 T-036 | NO | process rule (applies when real-line work starts) | Review-based; testable as a plan checklist + call-count limit. Limit number missing (inherits OQ-13). |

Ticket-number note: T-027..T-031 sit on issues #29–#33 and T-032..T-036 on issues
#34–#38 (T-tag ≠ issue number from T-027 on; T-030 is issue #32).

## Flag 1 – implemented-without-ticket (traceability gaps)

Strictly, every shipped file traces to a ticket. Two boundary cases need a PO call:

1. `sh/record-call.sh --call` **places a real call** (`open "tel:$CALL_NUMBER"`).
   FN-REQ-IVR-001 covers *recording*, not placing calls; placing real calls belongs to
   FN-REQ-IVR-021 (future) / NF-REQ-IVR-003 restraint. Either scope `--call` into a
   ticket or remove it. (Default `.env.example` ships `CALL_NUMBER=""`, and no 112/real
   number is hardcoded – good.)
2. Helper scripts with no ticket trace: `sh/show-map.sh`, `sh/watch-map.sh`,
   `sh/watch-calls.sh`, `sh/watch-board.sh`, `sh/play-latest.sh`, `sh/apply-names.sh`,
   `sh/pre-push.sh`, `sh/check-recording.sh`, `sh/switchaudio.sh`. Most read as
   file-system/chore maintenance (ticket-exempt per PROCESS.MD), but `show-map.sh` /
   `watch-map.sh` render FN-REQ-IVR-005 output and should reference T-005.

## Flag 2 – ticketed-but-unspecified

- Among T-001..T-036: none – every ticket has a spec section, feature scenarios, and a
  `tickets.md` entry.
- T-037..T-046 (issues #39–#48) are tickets **without parent requirements**: research
  (T-037, T-043), data seeds (T-038, T-039), backlog (T-040), voice/demo/UI work
  (T-041, T-042, T-044, T-045, T-046). Only T-040 names a REQ dependency (FN-REQ-IVR-021);
  T-044/T-045 point at T-tickets, not REQs. Upward traceability REQ→work is broken for
  this whole batch: e.g. T-045's live board overlaps FN-REQ-IVR-013's display need, and
  T-044 extends FN-REQ-IVR-007's keyword set, but neither link is recorded. Proposal:
  add "Parent REQ:" to each T-037..T-046 (or mint REQs where genuinely new behaviour
  exists – T-045's bilingual web UI looks like new behaviour, not a task).

## Flag 3 – dry-test gaps (007_TEST.MD)

- `007_TEST.MD` contains zero test cases; the step-2 dry test has not happened.
- One-pytest-per-scenario mapping: 0 of 57 scenarios mapped. The 6 pytest files cover
  5 requirements at file level only (`test_steps.py`, `test_keywords.py`,
  `test_menu_map.py`, `test_practice_robot.py`, `test_reactive.py`, `test_v1_flow.py`).
- FN-REQ-IVR-001/002 are marked **done (v0)** and implemented, with **no tests at all**
  – highest dry-test debt.
- FN-REQ-IVR-010, 013, 018, NF-REQ-IVR-001 cannot be dry-tested yet – their `Then`s are
  not falsifiable (see table). These four need rewording before step 2 can pass.
- `tests/test_doorkeeper_data.py` (T-039) and `tests/test_live_view.py` (T-045) test
  work that has no parent REQ – tests without requirements, mirroring Flag 2.

## Flag 4 – format deviations from 003_REQUIREMENTS.MD

1. Requirement IDs: 003 mandates `NFR-REQ-NNN`; the repo uses `NF-REQ-IVR-NNN`
   everywhere (specs, features, tickets, issues). Consistent internally, but 003 says
   "Existing IDs are not renamed automatically. Record any approved migration" – no
   migration record exists. Either amend 003 or record the migration.
2. Scenario IDs: 003 mandates one `@FN-REQ-001-S01`-style tag per scenario; features/
   repeat the bare `@FN-REQ-IVR-NNN` tag on every scenario and no `-SNN` IDs exist
   anywhere. Scenario-level tracking (gate item 2, "IDs") is therefore impossible.
3. GitHub issues carry What/Acceptance/Details but **no Gherkin** (`sh/make-tickets.sh`
   generates them without it), and titles use `T-NNN` while 003/`tickets.md` name the
   REQ ID. Gate item 2 explicitly requires "a GitHub issue with Gherkin and IDs".
4. Double bookkeeping: `openspec/tickets.md` still holds all 36 tickets AND all 36
   exist as GitHub issues, against both PROCESS.MD ("Never keep tickets in local
   files") and 003 ("when done remove each req from the file"). `tickets.md` also
   still claims "No GitHub issues created – only on request", which is stale.

## Top 5 gaps (ordered by gate impact)

1. **No Gherkin in any GitHub ticket (36/36)** – gate item 2 fails; add the full
   Gherkin + `-SNN` scenario IDs to issues #3–#38 (or record a PO decision that
   features/ is the single source of truth and amend the gate).
2. **Step-2 dry test missing entirely** – `007_TEST.MD` has no test cases and no
   scenario→test map; 003/007 require one test per scenario before design/code, yet
   7 requirements are already implemented.
3. **FN-001/FN-002 done-but-untested** – v0 "done" with zero tests; write the dry tests
   (file created, trap restores audio, mic excluded, lang flags) first.
4. **Four unfalsifiable requirements** – FN-010 ("right place", "name trap"), FN-013
   ("shown" where?), FN-018 ("clear and ready", OQ-12), NF-001 ("kindly", OQ-11);
   reword or keep as drafts until the open questions close.
5. **T-037..T-046 have no parent REQ** – a growing body of specified, ticketed, tested
   and demoed work (personas, voices, live board) outside the REQ tree; add parent
   links or mint REQs (T-045 especially).

## Smallest next steps for the PO

- Decide the single source of truth for Gherkin (GitHub issue body vs `features/`),
  then close gap 1 mechanically.
- Pin the four open testability questions (gaps 3–4) or formally park the reqs as drafts.
- Record the `NFR`→`NF` migration (or fix 003) and adopt `-SNN` scenario tags.
- Link T-037..T-046 to parent REQs before the batch grows further.
