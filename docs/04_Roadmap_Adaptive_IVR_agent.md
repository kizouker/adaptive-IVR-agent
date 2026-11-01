# Roadmap – Adaptive IVR agent

Oct 28, 2026 · @Rickard Åberg

Where Holdmate is going, step by step – and a new working version every day of the hackathon. The why and the goals are in Doc.

## Roadmap

First this, then this. Each step builds on the one before.

1. **Record and write down** – record calls on the Mac and turn speech into text (Whisper).
2. **Steps and menu map** – save each call as steps, and draw a map from them. *Now: 7 calls written down by hand, first map done.*
3. **Practice robot** – a copy of AF Agda that plays its lines and reacts to words and key presses.
4. **Holdmate explores** – tries words on the practice robot and fills in the map by itself.
5. **Queue alert** – find your place in the queue and alert you, first on the Mac, then in an iPhone app.
6. **The real phone line, with me** – a few calls where Holdmate talks, says it is an AI, and I do the identity check.
7. **More agencies** – the Swedish Social Insurance Agency (Försäkringskassan), the union (facket), the police (polisen).
8. **Agencies offer MCP** – each public agency (myndighet) offers an MCP server, some built on REST APIs they already have. Holdmate talks to the agencies directly instead of the phone robots, and handles cases that span several agencies, with you in the loop.

**Hard part:** for Holdmate to make real calls, we need a phone service (like 46elks) that costs money per minute. That is why the practice robot comes first.

## Hackathon plan: a new version every day

Each day ends with a version that works from start to end – a little more than the day before. All testing is against the practice robot.

| Day | Version | What it adds | Done when (draft) |
| --- | --- | --- | --- |
| Mon 26 – Wed 28 Oct | v0 (done) | Recording set up, 7 test calls logged, the vision | – |
| Thu 29 Oct | v1 | Keyword table, plus a mini practice robot that plays 3 AF Agda lines (made with `say`). Each line is saved as a step | One run creates a step file |
| Fri 30 Oct | v2 | Whisper turns the sound into text. A text search finds the queue number ("Det är N samtal före dig", "anropare nummer N"). Mac alert | The Mac alerts at number 2 |
| Sat 31 Oct | v3 | Menu map drawn from the steps, with a \* where you are | The \* sits on the right step |
| Sun 1 Nov | v4 | The practice robot reacts to words and keys, including "not understood" and yes/no. Holdmate picks words from the keyword table | Holdmate reaches the queue without a loop |
| Mon 2 Nov | v5 | Holdmate says it is an AI and talks kindly. The queue counts down | A full run from welcome to alert |
| Tue 3 Nov | v6 | Demo: short video, README, pitch | Ready to hand in |

## After the hackathon

- More test calls: dialects and accents, busy hours, and the queue number at The Castle.
- Then the real line, a few calls, with me there.
- Version 2: Holdmate tells you what to say based on where *you* are in The Castle's process.

**Separate idea:** checklists – one for the caller, so you don't say the wrong thing, and one for the The Castle staff.

**Not now, on purpose:** the iPhone app (a Mac message is enough for now), Holdmate talking in real calls, our own sound model, more agencies, moving the code to Java/Kotlin.
