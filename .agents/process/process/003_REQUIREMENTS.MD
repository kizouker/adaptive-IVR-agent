
As an agent I now work as a requirement specialist

# Requirements

How we decide *what* to build, before any design or code.
Step 1 of 6 in `docs/process/PROCESS.MD`. No design and no code in this step (see the gate in `docs/process/PROCESS.MD`).

## Roles
See *Roles* in `docs/process/PROCESS.MD`. In short:
- **Claude** (bussines analyst, requirements and test specialist) asks questions and writes the drafts.
- **Rickard (PO)** prioritises and approves. Nothing becomes a ticket without approval.

## Input
1. `VISION_N_GOALS.MD` – the why.
2. Is there any other input? External requirements? 


## Output
1. User stories with Gherkin acceptance criteria, written a file 
   ```$PROJECTDIR/specs/requirements.md```
2. After approval: one GitHub issue per req in the <repository> then the req is removed from this file.
3. After we first created the user stories, me as agent need to "dry test" them and get them approved.

## Format
```gherkin
# User story: As a job seeker, I want …, so that …
Feature: <short name>
  REQ-001

  @REQ-001-S01
  Scenario: <one behaviour>
    Given …
    When …
    Then …
```

## Rules
- Before making code changes, update ```$PROJECTDIR/specs/requirements.md``` with the requested behavior in Gherkin. Give each requirement a unique ID and place it beside the relevant user story.
- Treat each Gherkin `Feature` as one requirement and the unit for a GitHub ticket. Put its unique requirement ID immediately below the `Feature` line.
- Give every Gherkin `Scenario` a unique child ID as a tag (`@REQ-001-S01`), so it can be referenced and tracked as an acceptance case. Scenarios do not get separate GitHub tickets by default.
- When a GitHub issue shows short scenario summaries and expandable full Gherkin, verify that every summary matches the full scenario with the same ID. Treat the full Gherkin as the source of truth and update both together; do not let their wording or acceptance behavior diverge.
- At a later stage import the tickets in REQUIREMENTS.MD into github tickets and when done remove each req from the file (we don't want double book keeping)
- **(proposal)** ID format `REQ-NNN`, scenarios `@REQ-NNN-SNN`.
- **(proposal)** GitHub label `req` on every requirement issue.
- **(proposal)** A req is *ready* when it meets INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable) and every scenario has a clear `Then` that a test can check.

## Sources
- Gherkin reference: https://cucumber.io/docs/gherkin/reference/
- INVEST (Bill Wake, 2003): https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/
- ISTQB Foundation syllabus, ch. 4.5 (acceptance criteria, ATDD): https://www.istqb.org/certifications/certified-tester-foundation-level

## Requirements
Drafts. When approved by Rickard they move to GitHub issues and are removed from here.


