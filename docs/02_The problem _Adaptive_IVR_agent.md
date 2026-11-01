# The problem – Adaptive IVR agent

Oct 28, 2026 · @Rickard Åberg

The full picture of what goes wrong when you call a public agency today, from 7 real calls. The short version is in Doc.

## The problem today

- You don't know what to say to AF Agda, so it is hard to get through.
- You don't know what choices there are. Banks read their menu out loud ("press 1 for…"), so you know where to go.
- You wait in the queue and hear your place in the queue again and again.
- It is even harder if Swedish is not your first language.
- The robot is old, but has been used for years. The same system is used at least at the Swedish Social Insurance Agency (Försäkringskassan), and perhaps at other public services too. The Police robot even uses the same words ("Vad gäller ditt ärende?", "Förlåt, jag uppfattade inte").

**The solution:** Holdmate knows what to say to AF Agda and waits in the queue for you – or handles the whole call for you, with you in the loop (human-in-the-loop).

## Who has the problem (target group)

| Who | Why | When |
| --- | --- | --- |
| **Me (first user)** | I look for work and call The Castle often | Now |
| **Other job seekers** | They get stuck on exact words and long queues | When it works for me |
| **People whose first language is not Swedish, or who have a disability** | AF Agda wants exact Swedish words | Later |
| **Hackathon judges and employers** | A real problem, a working demo, built safely | Hackathon week, my portfolio |

**Demo focus:** anyone who is a job seeker.

## A call today

&#91;embedded content: a call today · 6 steps, 3 places to get stuck\]

Steps 1–4 and 6 come from two real calls on 27 October 2026. The queue step comes from an earlier call.

## Plain words, random answers

&#91;embedded content: plain Swedish in · five different replies out\]

You say a normal sentence, and you can't tell where you will end up. Only one of these replies takes you where you wanted to go.

## All calls so far

The two press-a-number menus never got stuck. The speech robots had their trouble at "say your topic" and the yes/no step.

| Date | Phone line | Menu kind | How it ended | Log (project file) |
| --- | --- | --- | --- | --- |
| 28 Oct | Swedbank | press a number | Self-service menu | not logged |
| 28 Oct | Unemployment fund AEA (a-kassa) | press a number | Reached a person fast | ivr-calls-aea-2026-10-28.md |
| 28 Oct | Social Insurance Agency (Försäkringskassan) | speech | Queue: "Det är 38 samtal före dig" | ivr-calls-fk-2026-10-28.md |
| 28 Oct | Police 114 14 | speech | Stuck in a yes/no loop | ivr-calls-police-2026-10-28.md |
| 28 Oct | AF Agda, call 3 | speech | Reached the queue | ivr-calls-2026-10-28.md |
| 27 Oct | AF Agda, call 2 | speech | Reached a person | ivr-calls-2026-10-27.md |
| 27 Oct | AF Agda, call 1 | speech | Stuck in the name trap | ivr-calls-2026-10-27.md |
