#!/usr/bin/env bash
# Create one GitHub issue per ticket in openspec/tickets.md (30 FN-REQ + 6 NF-REQ).
# Each ticket carries its requirement ID as its name.
# Idempotent: skips any ID already found in an existing issue title.
# Usage: ./sh/make-tickets.sh   (needs: git, gh with repo access)
set -euo pipefail
cd "$(dirname "$0")/.."

URL=$(git remote get-url origin)
REPO=$(echo "$URL" | sed -e 's/.*github.com[:/]//' -e 's/\.git$//')
echo "Repo: $REPO"

HAS_ISSUES=$(gh api "repos/$REPO" --jq .has_issues)
if [ "$HAS_ISSUES" != "true" ]; then echo "Issues are off for $REPO, stop."; exit 1; fi

EXISTING=$(gh api "repos/$REPO/issues?state=all&per_page=100" --paginate --jq '.[] | select(.pull_request|not) | .title')

mk() { # $1 = REQ ID, $2 = short name; body on stdin
  local id="$1" title="$1 $2" tmp number url
  if echo "$EXISTING" | grep -qF "$id"; then echo "SKIP $title (already exists)"; return 0; fi
  tmp=$(mktemp); cat > "$tmp"
  number=$(gh api "repos/$REPO/issues" -f title="$title" -F body=@"$tmp" --jq .number)
  rm -f "$tmp"
  url="https://github.com/$REPO/issues/$number"
  echo "NEW $title -> #$number $url"
  ID="$id" NUM="$number" perl -pi -e 's/^### ($ENV{ID})(?! \xe2\x86\x92)/### $1 \xe2\x86\x92 #$ENV{NUM} /' openspec/tickets.md
}

mk FN-REQ-IVR-001 "Record the robot voice" <<'EOF'
## What
Record the robot side of a call to data/recordings/robot-YYYYMMDD-HHMMSS.wav (mono 16000 Hz) and switch the sound back when done.

## Acceptance
- dated wav is created
- sound switches back via trap on q/Ctrl+C/normal end
- file holds only the other side

## Details
REQ: FN-REQ-IVR-001 · Priority: done (v0) · Depends on: none · Source: openspec/tickets.md (FN-REQ-IVR-001)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-002 "Transcribe the newest recording" <<'EOF'
## What
Turn the newest wav into text with whisper-cli; save the .txt next to it and print it.

## Acceptance
- Swedish by default
- WHISPER_LANG=en gives English
- WHISPER_LANG=auto guesses

## Details
REQ: FN-REQ-IVR-002 · Priority: done (v0) · Depends on: none · Source: openspec/tickets.md (FN-REQ-IVR-002)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-003 "Save each call as steps" <<'EOF'
## What
Define the step-file format and save each call/run as steps.

## Acceptance
- one mini-robot run creates a step file
- a hand-logged call stores as steps the map can use

## Details
REQ: FN-REQ-IVR-003 · Priority: v1 (Thu 29 Oct) · Depends on: none · Source: openspec/tickets.md (FN-REQ-IVR-003)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-004 "Keyword table" <<'EOF'
## What
Table mapping each keyword to what it gets done, and back ("I want X → say Y").

## Acceptance
- keyword → outcome lookup works
- outcome → words lookup works

## Details
REQ: FN-REQ-IVR-004 · Priority: v1 (Thu 29 Oct) · Depends on: none · Source: openspec/tickets.md (FN-REQ-IVR-004)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-005 "Menu map with position" <<'EOF'
## What
Draw the menu map from the steps and mark the current position with *.

## Acceptance
- the * sits on the right step during a call

## Details
REQ: FN-REQ-IVR-005 · Priority: v3 (Sat 31 Oct) · Depends on: FN-REQ-IVR-003 · Source: openspec/tickets.md (FN-REQ-IVR-005)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-006 "Mini robot plays three lines" <<'EOF'
## What
Mini practice robot playing 3 The Doorkeeper lines made with `say`; each line saved as a step.

## Acceptance
- 3 lines play
- each line is saved as a step

## Details
REQ: FN-REQ-IVR-006 · Priority: v1 (Thu 29 Oct) · Depends on: FN-REQ-IVR-003 · Source: openspec/tickets.md (FN-REQ-IVR-006)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-007 "Reactive robot" <<'EOF'
## What
Practice robot reacts to words and key presses, with "not understood" and yes/no handling.

## Acceptance
- known word/key moves on
- unknown input gets the not-understood line
- ja/nej move on at confirm

## Details
REQ: FN-REQ-IVR-007 · Priority: v4 (Sun 1 Nov) · Depends on: FN-REQ-IVR-006 · Source: openspec/tickets.md (FN-REQ-IVR-007)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-008 "Pick words from the keyword table" <<'EOF'
## What
Holdmate picks words from the keyword table when talking to the practice robot.

## Acceptance
- at a topic step wanting X, Holdmate says the table's Y

## Details
REQ: FN-REQ-IVR-008 · Priority: v4 (Sun 1 Nov) · Depends on: FN-REQ-IVR-004, FN-REQ-IVR-007 · Source: openspec/tickets.md (FN-REQ-IVR-008)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-009 "Try words and fill the map" <<'EOF'
## What
Holdmate tries words on the practice robot and adds each observation to the menu map.

## Acceptance
- the map grows with every call

## Details
REQ: FN-REQ-IVR-009 · Priority: v4 (Sun 1 Nov) · Depends on: FN-REQ-IVR-007 · Source: openspec/tickets.md (FN-REQ-IVR-009)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-010 "Reach the queue without a loop" <<'EOF'
## What
Full explore run reaching the right place with no loops.

## Acceptance
- queue reached
- no yes/no loop
- no name trap

## Details
REQ: FN-REQ-IVR-010 · Priority: v4 (Sun 1 Nov) · Depends on: FN-REQ-IVR-008, FN-REQ-IVR-009 · Source: openspec/tickets.md (FN-REQ-IVR-010)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-011 "Find the queue number" <<'EOF'
## What
Text search finding the queue number in three phrasings.

## Acceptance
- "Det är 38 samtal före dig" → 38
- "anropare nummer 12" → 12
- "Din plats är: 47" → 47

## Details
REQ: FN-REQ-IVR-011 · Priority: v2 (Fri 30 Oct) · Depends on: FN-REQ-IVR-002 · Source: openspec/tickets.md (FN-REQ-IVR-011)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-012 "Alert on the Mac near the front" <<'EOF'
## What
Mac alert when the queue is near the front.

## Acceptance
- the Mac alerts at number 2

## Details
REQ: FN-REQ-IVR-012 · Priority: v2 (Fri 30 Oct) · Depends on: FN-REQ-IVR-011 · Source: openspec/tickets.md (FN-REQ-IVR-012)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-013 "Queue counts down" <<'EOF'
## What
Shown queue number updates as the queue moves, without listening.

## Acceptance
- place known without listening to the call

## Details
REQ: FN-REQ-IVR-013 · Priority: v5 (Mon 2 Nov) · Depends on: FN-REQ-IVR-011 · Source: openspec/tickets.md (FN-REQ-IVR-013)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-014 "Intake in own words" <<'EOF'
## What
Holdmate asks "What's your concern?" by chat or talk; free-word answer becomes the call goal.

## Acceptance
- own-words answer in chat or talk is taken as the call goal

## Details
REQ: FN-REQ-IVR-014 · Priority: post (after hackathon) · Depends on: none · Source: openspec/tickets.md (FN-REQ-IVR-014)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-015 "Two ways to start a call" <<'EOF'
## What
Start from chat text or from clicking the menu tree + Call; the app steers as far as it can.

## Acceptance
- chat start works
- menu-tree + Call start works

## Details
REQ: FN-REQ-IVR-015 · Priority: post (after hackathon) · Depends on: FN-REQ-IVR-005 · Source: openspec/tickets.md (FN-REQ-IVR-015)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-016 "Identity-check ping" <<'EOF'
## What
Ping the caller at the identity check; caller approves on their phone (BankID); Holdmate never approves.

## Acceptance
- ping fires at the identity step and Holdmate waits for the approval

## Details
REQ: FN-REQ-IVR-016 · Priority: post (after hackathon) · Depends on: none · Source: openspec/tickets.md (FN-REQ-IVR-016)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-017 "Handover when a person answers" <<'EOF'
## What
Buzz ("You are number 3"), show the queue number in a web widget, hand over or keep both in the call.

## Acceptance
- buzz + widget + handover-or-joint-call all work. (iPhone display excluded – not now.)

## Details
REQ: FN-REQ-IVR-017 · Priority: post (after hackathon) · Depends on: FN-REQ-IVR-012, FN-REQ-IVR-013 · Source: openspec/tickets.md (FN-REQ-IVR-017)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-018 "Handover with a clear question" <<'EOF'
## What
At handover the caller's question is clear and ready.

## Acceptance
- question is clear and ready at handover. (Calm/no-recall verification open – OQ-12.)

## Details
REQ: FN-REQ-IVR-018 · Priority: post (after hackathon) · Depends on: FN-REQ-IVR-014 · Source: openspec/tickets.md (FN-REQ-IVR-018)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-019 "Any phone line" <<'EOF'
## What
Assisted calls work on any trained line, not just The Castle.

## Acceptance
- a newly trained line supports assisted calls

## Details
REQ: FN-REQ-IVR-019 · Priority: post (after hackathon) · Depends on: FN-REQ-IVR-009 · Source: openspec/tickets.md (FN-REQ-IVR-019)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-020 "Say it is an AI" <<'EOF'
## What
Holdmate identifies as AI whenever it talks.

## Acceptance
- disclosure line in the v5 practice run
- same line scripted for real calls

## Details
REQ: FN-REQ-IVR-020 · Priority: v5 (Mon 2 Nov) · Depends on: none · Source: openspec/tickets.md (FN-REQ-IVR-020)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-021 "Real calls with the caller present" <<'EOF'
## What
A few real-line calls: user present, AI disclosure, user does the identity check.

## Acceptance
- user present + disclosure + user-approved identity on each real call

## Details
REQ: FN-REQ-IVR-021 · Priority: future (after hackathon) · Depends on: FN-REQ-IVR-016, FN-REQ-IVR-020, NF-REQ-IVR-003 · Source: openspec/tickets.md (FN-REQ-IVR-021)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-022 "Fully on its own" <<'EOF'
## What
End-to-end case handling; caller steps in only for identity check or to talk to a person.

## Acceptance
- caller needed only where they must. (Blocked on OQ-14 legal input.)

## Details
REQ: FN-REQ-IVR-022 · Priority: future · Depends on: FN-REQ-IVR-021 · Source: openspec/tickets.md (FN-REQ-IVR-022)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-023 "FK, union, police" <<'EOF'
## What
Add Försäkringskassan, the union, and police 114 14 with the same train-map-call approach.

## Acceptance
- training, mapping and assisted calling work per new line. Seeds: schemas/IVR-schema.md.

## Details
REQ: FN-REQ-IVR-023 · Priority: future · Depends on: FN-REQ-IVR-019 · Source: openspec/tickets.md (FN-REQ-IVR-023)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-024 "Talk through agency MCP" <<'EOF'
## What
Use an agency's MCP server directly instead of calling, where offered.

## Acceptance
- with an MCP server available, no phone call is needed

## Details
REQ: FN-REQ-IVR-024 · Priority: future · Depends on: none (agency-side) · Source: openspec/tickets.md (FN-REQ-IVR-024)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-025 "Cases across agencies" <<'EOF'
## What
Handle a case moving between agencies (a-kassa → Försäkringskassan) with the caller in the loop.

## Acceptance
- cross-agency case handled
- caller looped in at the key steps

## Details
REQ: FN-REQ-IVR-025 · Priority: future · Depends on: FN-REQ-IVR-024 · Source: openspec/tickets.md (FN-REQ-IVR-025)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-026 "Wording for your situation" <<'EOF'
## What
v2 – guide what to say from the caller's place in The Castle's process (needs a process model).

## Acceptance
- sign-up-again case gets the right wording. (Programme name open – OQ-10.)

## Details
REQ: FN-REQ-IVR-026 · Priority: future (v2) · Depends on: FN-REQ-IVR-004 · Source: openspec/tickets.md (FN-REQ-IVR-026)

---
_From openspec/tickets.md._
EOF

mk NF-REQ-IVR-001 "Helpful and kind (draft)" <<'EOF'
## What
Holdmate's voice is helpful and kind in the v5 full run.

## Acceptance
- v5 run talks kindly. (How kindness is tested open – OQ-11.)

## Details
REQ: NF-REQ-IVR-001 · Priority: v5 (Mon 2 Nov) · Depends on: none · Source: openspec/tickets.md (NF-REQ-IVR-001)

---
_From openspec/tickets.md._
EOF

mk NF-REQ-IVR-002 "No personal data kept" <<'EOF'
## What
Cut recordings where staff answer; keep no ID numbers, staff names or staff voices in logs, demos or GitHub.

## Acceptance
- staff part cut before storing
- scan of logs/demos/repo finds none of the three

## Details
REQ: NF-REQ-IVR-002 · Priority: always (applies now) · Depends on: none · Source: openspec/tickets.md (NF-REQ-IVR-002)

---
_From openspec/tickets.md._
EOF

mk NF-REQ-IVR-003 "Real-line restraint" <<'EOF'
## What
Real line only a few times with the user present; hackathon testing all on the practice robot.

## Acceptance
- all hackathon tests run against the practice robot. (Count for "a few" open – OQ-13.)

## Details
REQ: NF-REQ-IVR-003 · Priority: always · Depends on: none · Source: openspec/tickets.md (NF-REQ-IVR-003)

---
_From openspec/tickets.md._
EOF

mk NF-REQ-IVR-004 "Any language (draft)" <<'EOF'
## What
Serve callers in any language, starting with the English branch (press 0).

## Acceptance
- pressing 0 continues the call in English. (Branch content open – OQ-05.)

## Details
REQ: NF-REQ-IVR-004 · Priority: future · Depends on: none · Source: openspec/tickets.md (NF-REQ-IVR-004)

---
_From openspec/tickets.md._
EOF

mk NF-REQ-IVR-005 "Never test against 112" <<'EOF'
## What
Keep 112 out of all test targets, always.

## Acceptance
- 112 never appears among test targets

## Details
REQ: NF-REQ-IVR-005 · Priority: always · Depends on: none · Source: openspec/tickets.md (NF-REQ-IVR-005)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-027 "Probe recovery behaviour" <<'EOF'
## What
Probe no-input vs no-match, correction recovery, and loops/dead ends/fallback paths.

## Acceptance
- both no-input and no-match replies recorded and compared
- correction recovery shown
- loops/dead ends/fallbacks identified

## Details
REQ: FN-REQ-IVR-027 · Priority: post (after hackathon) · Depends on: FN-REQ-IVR-007, FN-REQ-IVR-030 · Source: openspec/tickets.md (FN-REQ-IVR-027)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-028 "Verify same-state equivalence" <<'EOF'
## What
Check whether synonyms, different routes, and DTMF vs speech reach the same state.

## Acceptance
- map records synonym equivalence, working routes per state, and DTMF/speech equivalence

## Details
REQ: FN-REQ-IVR-028 · Priority: post (after hackathon) · Depends on: FN-REQ-IVR-009 · Source: openspec/tickets.md (FN-REQ-IVR-028)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-029 "Tag evidence levels in the map" <<'EOF'
## What
Tag map entries as observed/inferred/untested with evidence; revise or reject on counter-evidence.

## Acceptance
- new observations tagged with evidence
- contradicted hypotheses revised or rejected. (State identity open – OQ-18.)

## Details
REQ: FN-REQ-IVR-029 · Priority: post (after hackathon) · Depends on: FN-REQ-IVR-005 · Source: openspec/tickets.md (FN-REQ-IVR-029)

---
_From openspec/tickets.md._
EOF

mk FN-REQ-IVR-030 "Handle silence and timeouts" <<'EOF'
## What
Practice robot answers silence with repeated no-input prompts, then times out or falls back.

## Acceptance
- silence gets a repeated prompt
- repeated silence times out or follows fallback

## Details
REQ: FN-REQ-IVR-030 · Priority: post (after hackathon) · Depends on: FN-REQ-IVR-007 · Source: openspec/tickets.md (FN-REQ-IVR-030)

---
_From openspec/tickets.md._
EOF

mk NF-REQ-IVR-006 "Real-system experiments stay harmless" <<'EOF'
## What
Every real-line experiment plan avoids human agents and service disruption; runs stay within the approved limit.

## Acceptance
- plan review reaches no agent and disrupts nothing
- call count within limit

## Details
REQ: NF-REQ-IVR-006 · Priority: always (applies when real-line work starts) · Depends on: NF-REQ-IVR-003 · Source: openspec/tickets.md (NF-REQ-IVR-006)

---
_From openspec/tickets.md._
EOF

echo "Done."
