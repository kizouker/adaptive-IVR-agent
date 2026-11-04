# Holdmate — purpose (draft)

## One line

Holdmate tar dig förbi telefonroboten och står i kön åt dig.

## Two names, two roles (never mix the words)

- **Holdmate** = din *agent*. Står på din sida.
- **Roksolana** = en *övningskopia* av Arbetsförmedlingens telefonrobot, byggd från riktiga inspelade samtal.

Aldrig "robot" om Holdmate. Aldrig "agent" om Roksolana.

Roksolana är en **IVR-simulator** (talsvarssimulator) — inte en flygsimulator.

## The story, in order

1. Arbetsförmedlingens telefonrobot förstår bara exakta ord.
2. Holdmate är en agent som lär sig de orden och tar dig igenom.
3. Holdmate kan inte öva genom att ringa riktiga linjen hundra gånger — så jag byggde Roksolana, en kopia gjord från riktiga samtal.
4. Holdmate övar på Roksolana (IVR-simulatorn), och ringer sedan på riktigt åt dig.

## Talk (Toastmasters)

### 1. Opening (hook) — Rickard's real call

> I called the Swedish unemployment office to sign up for their program.
> A robot asked what my errand was. I told it — in my own words.
> It didn't understand, and tried to send me to parental leave.
>
> That's when I decided to build an agent that learns these phone menus —
> the same old IVR system almost every Swedish government agency uses.
>
> I've had this idea for several years, but only now, with large language
> models, could I make it come true.

### 2. Core point 1 — the problem (Russell & Norvig environment)

The IVR only understands exact words. As an agent environment
(Russell & Norvig, *AI: A Modern Approach*) it is:

- **Partially observable** — you never see the menu tree, only the next prompt.
- **Non-deterministic** — it hears my Skåne dialect differently each time.
- **Has traps** — some branches loop with no way out (a point of no return).

Plain version for non-technical listeners:
> You can't see the menu, it doesn't hear you the same way twice,
> and one wrong word can trap you in a loop.

**Who it hurts:** hard for me — and close to impossible for the many
immigrants in Sweden who don't speak the exact Swedish the robot expects.

### 3. Core point 2 — what Holdmate does (two goals)

1. **Map the menu** — document the IVR's menu system, so you know which
   keywords actually work.
2. **Do the call for you** — the agent navigates and waits on your behalf,
   with you as the human in the loop (you identify yourself, you take over
   when a person answers).

### 4. Core point 3 — what this project shows (and where it stands)

Built from first principles: a **rational agent** (Russell & Norvig, ch. 2).
The project demonstrates that Holdmate can:

- **Explore** the menu system,
- **Document** it as a state-machine graph,
- **Learn** the keywords that work,
- **Practice** on its own,
- and **get further in line**.

**Status, honestly:** the plan was to connect to a real phone operator
(46elks); no answer from them yet. So today it is a **simulator of the IVR**
(Roksolana) plus **an agent learning from it** (Holdmate).

We have used, actually, … *(to be continued)*

**Tools, honestly:** the first real calls were transcribed with Claude
dictation (Whisper did no better, dictation was quicker). The Meta part
today is **Muse Spark** in the intent stage; next step is to swap
transcription over to Meta's models too.

> Coach note: this is a Meta hackathon — lead with what Meta does in the
> project (Muse Spark intent stage), mention the transcription tool only
> as history, in one line.

### Holdmate's third job — the queue

Holdmate **keeps track of your place in the queue** and counts it down.
The real goal: call, get through the menu, and get to the front of the line.
Mute the call — Holdmate shows your place on iPhone / Apple Watch and
**notifies you when it's your turn** to be connected.

### The menu is a state machine

Every call follows the same states:

1. **Open question** — "What is your errand?"
2. **Options** — "You can say for example …"
3. **Yes/no question** — where you can end up in a *no-operation loop*: no way back.
4. **Transfer**
5. **Identification** (BankID / Freja)
6. **Queue** — Holdmate counts down your place.
