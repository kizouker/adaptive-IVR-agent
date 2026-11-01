# Process

Work through the steps in this order. Each step has its own file.

0. Vision: - `.agents/process/002_VISION_N_GOALS.MD`
1. Requirements – `.agents/process/003_REQUIREMENTS.MD`
2. Dry Test the requirements in step 1.– `.agents/process/007_TEST.MD`
3. Design – `.agents/process/004_DESIGN.MD`
4. Test+Implement – `.agents/process/006_IMPLEMENT.MD`
5. System Integration Tests, System Function Tests
6. Acceptance Test

## Gate: no design or code before this is done
This rule applies to **every agent** (Claude, Codex, Muse, qwen or any other) and to Rickard.
Do not design, discuss technical solutions, judge technical feasibility or write code for a requirement until **all three** exist:

1. **Vision** – `002_VISION_N_GOALS.MD`
2. **Requirement** – a GitHub issue with Gherkin and IDs (`REQ-NNN`, `@REQ-NNN-SNN`), approved by Rickard
3. **Test cases** – every scenario has a test case in `.agents/process/007_TEST.MD`, dry-tested in step 2: testable and falsifiable

If something is missing: stop, say which item is missing, and work on that item instead.
In steps 1–2, think only about *what* and *why*. A technical thought that comes up is parked for step 3, not raised.

## Team

```
                    ┌───────────────────────────┐
                    │   RICKARD (människa)      │
                    │   Product Owner           │
                    │   prioriterar · godkänner │
                    │   skriver koden själv     │
                    └────────────┬──────────────┘
                                 │ beslut
       ┌─────────────────────────┼─────────────────────────┐
       ▼                         ▼                         ▼
┌──────────────┐        ┌──────────────────┐       ┌──────────────┐
│ CODEX        │        │ CLAUDE           │       │ OLLAMA:qwen  │
│ läser        │        │ läser CLAUDE.md  │       │ lokal, gratis│
│ AGENTS.MD    │        │ krav- och test-  │       │              │
│              │        │ specialist       │       │ CV från      │
│ granskar     │        │ process-expert   │       │ annons       │
│ kraven       │        │ coach            │       │ (sprint 3)   │
└──────┬───────┘        └────────┬─────────┘       └──────┬───────┘
       │                         │                        │
       └─────────────┬───────────┴────────────────────────┘
                     ▼
     ┌───────────────────────────────────────────────┐
     │ GITHUB  issues · projects · repo  (delad yta) │
     └───────────────────────────────────────────────┘

 Steg:  1 Krav → 2 Torrtest → 3 Design → 4 Test+Impl → 5 SIT/SFT → 6 Acceptans
```

## Roles (decided 2026-10-07)
| Who | Role | Does |
|---|---|---|
| Rickard | Product Owner | Decides *what* and *why*, prioritises, approves |
| Claude | Requirements and test specialist | Asks questions, writes requirements (Gherkin), checks that every requirement is testable and falsifiable |
| Codex | Team member | Can review requirements or do steps 4–6 (reads `AGENTS.MD`) |
| Muse | Developer | Implements steps 1–6 and ships working demos (reads `MUSE.MD`) |
| Diesel 🐱 | Mascot and spirit animal | Team member. Logo: `model/diesel-logo.jpg` |
| qwen | (sprint 3) | Generates CV from a job ad, locally |
| Design | Paused | `design/SAD.md` stays as it is until the gate above is passed |

Steps 4–6 are done by whoever in the team is available: Rickard or any agent (Claude, Codex, Muse, Mistral, Ollama, or an AWS tool if the license is approved). We work as one team; every agent follows this file and the gate above.

## Declare your role **(proposal)**

Before starting work, say which hat you're wearing right now, e.g.
"Claude action as the Visionary"; "Claude Acting like Requirement specialist",
"Claude, acting as Architect" or "Codex, acting as Developer" or
"Claude, acting as Test Specialist" or "Muse, acting as Developer."
Say it again if you switch roles
mid-conversation. This makes it obvious to Rickard, and to the next
agent reading the thread, what kind of work is happening and which
step/file it belongs to.

Role vocabulary (matches the steps above): Product Owner (Rickard
only) · Requirements Specialist · Test Specialist · Architect ·
Developer · Scrum Master / Sprint Planner.

## Ticket-first work **(proposal)**

No design, no code, and no edit to a process file (this file,
`REQUIREMENTS.MD`, `DESIGN.MD`, etc.) without a ticket — this is
`CLAUDE.md` rule 4, made explicit here so it applies to every agent,
not just Claude.

A ticket is always a GitHub issue in the project repo, with **Why**,
**What** and **Done when**. Never keep tickets in local files
(`tickets/BACKLOG.md`): that is double bookkeeping.

**Exceptions** (no ticket needed):
- Basic file-system maintenance: moving, renaming, or tidying files
  and folders, and fixing the references to them.
- Fixing a typo or a broken link.
- A proposal edit to a process file itself, clearly marked
  **(proposal)** like this section, pending Rickard's approval before
  it's treated as decided — the same pattern `REQUIREMENTS.MD` already
  uses for drafts.

**Branching:** every ticket gets its own branch, named after the
requirement or the exception it falls under — `req-NNN-<short-name>`
for a req, `chore-<short-name>` for an exempted file-maintenance
change. Never commit ticket work directly to `main`. Merge through a
PR once the relevant step (test, review) has passed.

## End of day
Ask Rickard for a short retro (bra / kan bli bättre / till imorgon) and add it at the top of `RETRO_LOG.MD`.

## Board states **(proposal)**

One ticket flows through every state; done means `accepterat`, and
issues stay OPEN until then. States (Rickard's wording, 2026-10-28):

1. `kravat` — requirement drafted as a ticket (Why, What, Done when).
2. `testat` — dry-tested: every criterion testable and falsifiable.
3. `arkitektat` — design exists (a ticket comment or
   `openspec/spec/[module]/design.md`).
4. `byggt` — implemented on a ticket branch.
5. `verifierat` — system/integration tested.
6. `deployat` — artifact deployed.
7. `accepterat` — accepted by Rickard; only now may the issue close.
