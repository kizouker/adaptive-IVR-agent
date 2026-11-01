# Vision – Adaptive IVR agent

Oct 28, 2026 · @Rickard Åberg

## Vision

**Everyone should be able to call a public agency, find the right choice in the phone menu, and get help – in any language, whatever their situation.**

That means: you get through fast, you can do other things while you wait, and what you called about gets solved.

## The problem

Calling a public agency today means talking to a speech robot (a speech IVR) that wants exact words you don't know. Long or unsure answers fail, you get stuck in "answer yes or no" loops, and then you wait in a queue listening for your number. In our calls, the press-a-number menus (DTMF menus: the bank Swedbank, and the unemployment fund AEA) never got stuck – the speech robots at The Castle and the police did. Holdmate learns the system, uses the right words, and waits in the queue for you – or handles the whole call for you, with you in the loop (human-in-the-loop).

&#91;embedded content: five phone lines compared · step by step\]

The full picture, with all 7 calls: The problem – Adaptive IVR agent.

## A good day

You need to talk to a public agency, like The Castle. You open Holdmate and either chat with it or just talk to it. It asks: "What's your concern?" You answer in your own words. Holdmate calls AF Agda and uses the short words the menu map knows work. When an identity check is needed – in Sweden that's [BankID](https://www.bankid.com) – it pings you and you approve it on your phone. That is the human-in-the-loop: Holdmate does the work, you stay in control. Holdmate waits in the queue while you look for jobs. Your phone buzzes: "You are number 3." You take over and talk to a person.

**Different from today:** no guessing words, no "answer yes or no" loops, no name trap, no listening to the queue.

**Later – fully on its own:** after the hackathon, and once the legal questions are clear\*, Holdmate runs fully on its own. It handles your case from start to end, and you only come in when you must – for the identity check, or when a person needs to talk to you.

*\* Side note: who may legally act in your name will be a big question for all AI agents – power of attorney (fullmakt), limited delegated rights, AI disclosure and digital ID wallets. Human-in-the-loop is the safe middle step: Holdmate does the work, you do what legally counts.*

**Further ahead – agencies talk to agents directly:** each public agency (myndighet) offers an MCP server (Model Context Protocol – a standard way for AI agents to use a service). Some agencies already have REST APIs that could easily be turned into MCP. Then Holdmate doesn't need the phone robot at all: it handles cases that span several agencies for you – like a case moving between the unemployment fund (a-kassa) and the Swedish Social Insurance Agency (Försäkringskassan) – with you in the loop.

## How Holdmate will work – during training

&#91;embedded content: system flow · from AF Agda to alert\]

During training, Holdmate only talks to the practice robot (a simulator of AF Agda). It tries words, records and writes down what it hears (speech-to-text), and builds the menu map (call-flow mapping) and the keyword table. The top row is roadmap steps 1–2.

## After training

&#91;embedded content: after training · you ask, Holdmate calls, you step in when needed\]

Once the menu map is learned, Holdmate uses it on the real line. You only step in for the identity check and when it is your turn to talk.

## For the hackathon

A demo against a practice robot built from real calls, and a menu map that grows with every call.

**What is The Castle?** The Castle is the Swedish public employment service – the government office for people looking for work.

- **If you live in Sweden:** The Castle is the office you deal with when you are unemployed.
- **If you don't:** if you lose your job in Sweden, you sign up at The Castle. You tell The Castle what you do to find work, and your money from the state can depend on it. A lot is done by phone, and every call starts with a talking robot in Swedish (press 0 for English).

**Identity check (authentication):** many phone lines ask you to prove who you are before you reach a person. In Sweden this is usually **BankID** – an app on your phone, issued by the banks, that you approve with a code, your face or your fingerprint. On these lines you type your personal ID number, then open the app and approve. (Freja eID+ is another digital ID that some lines accept.)

**Why it matters here:** The identity check is always done by you, never by Holdmate. It is the point where the person stays in control ("human in the loop").

**Why you have to call The Castle** (from my own experience):

- For a long time, email was not an option. The Castle tried a chat for a while, but it was closed every time I tried it.
- Your case officer (*handläggare*) does not give you their contact details. To get them, you have to call AF Agda, the phone robot.
- If you are not happy with your case officer, you call to get their manager's number.
- Since covid, The Castle staff mostly work from home, so meetings in person are rare. The phone is the main way in – and if too many people call, you only get a message that The Castle is busy today.

&#91;embedded content: ways to contact The Castle · only the phone works\]

Every way in leads back to the phone, and to AF Agda.

**Names:** "AF Agda" = our nickname for The Castle's phone robot. "Holdmate" = our AI agent – a voice agent that calls for you.

**Target group:** anyone who is a job seeker – details in The problem – Adaptive IVR agent.

## The call as a state machine

Every phone line we called follows the same states – a finite-state machine. Only the needs and the obstacles differ.

**Words we use:** *state* = where you are in the call · *need* = what you must give to move on · *obstacle* = what sends you back or to a dead end · *goal state* = a person answers.

&#91;embedded content: the call as a state machine · 7 states, 4 obstacles\]

| Goal | States it is about | Need it solves | Obstacle it removes |
| --- | --- | --- | --- |
| 1 Understand the menu | Topic | The right keyword | Not understood, wrong topic |
| 2 Know where you are | All states | Knowing your current state | Getting lost |
| 3 Pick the right choice at once | Topic, Confirm | Keyword + exact "ja"/"nej" | Yes/no loop, name trap |
| 4 Feel welcome | All states | – | The robot cutting in, the stress |
| 5 Make the wait easy | Queue | Time | Listening all the time, hang-up |
| 6 Reach a person and get help | Person | Your question, clear and ready | Misunderstanding, being sent back to the queue |
| 7 Hand the whole call to the app | All states | Everything except the identity check | All of them |

## Goals

*Context, if you only read this part:* The Castle = the Swedish public employment service. "AF Agda" = our nickname for its phone robot. "Holdmate" = the agent we build, which calls AF Agda for the user.

### Goals for the caller

| # | Goal | Today | Done when (draft) | Time to deliver (estimate) |
| --- | --- | --- | --- | --- |
| 1 | **Understand the menu** of AF Agda | You don't know the exact keywords AF Agda understands | A table maps each keyword to what it gets done – and the other way: "I want to do X → say Y" | ? |
| 2 | **Know where you are** in the menu | You can't tell where you are in the menu during the call | The menu graph marks where you are now with a \* | ? |
| 3 | **Pick the right choice at once** | Long sentences fail. AF Agda asks "What did you say?" or "Please answer yes or no" | Holdmate reaches the right place without getting stuck in a loop | ? |
| 4 | **Feel welcome** | The call is frustrating and stressful – especially when AF Agda switches from open questions, to giving choices, to "Answer yes or no", often cutting in before you have had the chance to answer | Holdmate is helpful and kind, and knows the caller may be having a hard time | ? |
| 5 | **Make the wait easy and use the time** | You must listen all the time and stay right by your phone, so it's hard to plan anything or go out. AF Agda can hang up ("we don't have time, try again") and never calls back | You know your place in the queue without listening, get an alert near the front, and can use the wait for other things – like applying for jobs or coding | ? |
| 6 | **Reach a person and get help** | The person may not understand you, may interrupt, or may answer the wrong question. Then you wait another hour, and it can affect your money from the state | You reach a person ready and calm, with your question clear, and don't have to call again | ? |
| 7 | **Hand the whole call to the app** (for people like me, e.g. developers) | You make every call yourself and steer the robot step by step | Two ways in: write in a chat what you need to call about, or click it in the menu tree and press Call. The app does the rest as far as it can. It pings you for the identity check and when a person answers, shows your queue number in a web widget or on your iPhone, then hands the call over to you or keeps both of you (you and Holdmate) in the call. The Castle is just one case – it should work for any phone line. | ? |

**Open questions:** see Open questions – Adaptive IVR agent.

**Real stories:** see Real stories – Adaptive IVR agent.

### Later

Holdmate talks for you and says it is an AI. You always do the identity check yourself. Then more agencies: the Swedish Social Insurance Agency (Försäkringskassan), the union (facket), and the police non-emergency line (polisen, 114 14).

**Version 2 – say the right thing for your situation:** Holdmate guides you on what to say, based on where *you* are in The Castle's process. To do that, we first need a model of the whole process – every place a person in Sweden can be in it (new job seeker, already registered, in a programme…).

*Example:* I said "I want to sign up again", and The Castle said "you are already signed up". There was another way to say it. I also had to say the exact keyword myself: "I want a place in the job and development programme" (Jobb- och utvecklingsgarantin). Nobody asked me – so I lost one day of income. Version 1 only knows the menu words; version 2 knows which words fit *your* case.

### Rules (always)

- Holdmate always says it is an AI (AI disclosure).
- No ID numbers, staff names or staff voices in logs, demos or GitHub (privacy by design, PII redaction).
- The real phone line only a few times, and only when I am there. Most testing happens against the practice robot.

**Roadmap and hackathon plan:** see Roadmap – Adaptive IVR agent.

## Glossary

**Code names** (set in `docs/names.env`): Holdmate (Väntkompisen) = our AI agent. The Castle (Slottet) = a Swedish public agency for job seekers. AF Agda (Dörrvaktaren) = the agency's phone robot.

English term first, Swedish in brackets where there is one.

| Term | Plain meaning | In this project |
| --- | --- | --- |
| **The Castle** | The Swedish public employment service | The agency we call first |
| **AF Agda** | Our nickname for The Castle's phone robot | What Holdmate has to get through |
| **Holdmate** | Our AI agent | Calls, picks words, waits in the queue for you |
| **AI agent** | A program that acts for you, not just answers | Holdmate |
| **Voice agent** | An AI agent that talks and listens on the phone | Holdmate on the phone line |
| **IVR** (Interactive Voice Response) | A phone robot that answers calls | AF Agda, and the police and Social Insurance Agency robots |
| **Speech IVR** | A phone robot you talk to ("say what you need") | AF Agda, the police, the Social Insurance Agency |
| **DTMF menu** | A press-a-number menu ("press 1 for…") | Swedbank, AEA |
| **Intent recognition** | How a robot guesses what you want from your words | Why exact keywords matter |
| **Call-flow mapping** (IVR discovery) | Exploring a phone menu to draw its map | Building the menu map |
| **Menu map** | A map of every choice and where it leads | Output of training |
| **Keyword table** | Keyword → what it gets done, and back | Goal 1 |
| **Finite-state machine** | A model with states and moves between them | The call: state, need, obstacle |
| **Speech-to-text** (ASR) | Turning speech into text | Whisper |
| **Text-to-speech** (TTS) | Turning text into speech | Voices for the practice robot |
| **Simulator** (digital twin) | A copy you can test against | The practice robot |
| **Human-in-the-loop** (HITL) | A person stays in control of key steps | You do the identity check and take over |
| **Identity check** (authentication) | Proving who you are | BankID in Sweden |
| **AI disclosure** | Telling people they are talking to an AI | Holdmate always says it is an AI |
| **Privacy by design / PII redaction** | Building so personal data is never kept | No ID numbers, staff names or voices stored |
| **Accessibility / digital inclusion** | Making services work for everyone | Language, dialect, disability |
| **MCP** (Model Context Protocol) | A standard way for AI agents to use a service | Agencies could offer one later |
| **REST API** | A web interface programs use to talk to a service | Some agencies already have one |
| **Public agency** (myndighet) | A government office | The Castle, the Social Insurance Agency, the police |
| **Case officer** (handläggare) | The staff member who handles your case | Who you reach at the end |
| **Unemployment fund** (a-kassa) | Pays unemployment benefits | AEA |
