# Holdmate — 3-minute submission video script (draft)

Total: ~3:00. English voiceover. Swedish voices in demo: Agda = Alva, caller = Oskar, officer = Klara.

## 0:00–0:20 Problem (20s)

> "Calling a robot operator like Sweden's Public Employment Service means menus, queues, and waiting on hold. Holdmate is an adaptive IVR agent that learns to make those calls for you — and it practices safely against AF Agda, a scripted copy of the real line built from recorded calls, so the real line is never touched during training."

VISUAL: title card "Holdmate — an adaptive IVR agent"; cut to phone-on-hold stock or waveform.

## 0:20–2:20 Live demo (2min)

Narration under live screen + audio. One command starts everything:

```bash
./start.sh
```

- **Talk (0:20–1:10):** "This is talk mode — I speak, Agda answers as Alva." Show `./sh/talk.sh` call: any key skips ahead, `0` jumps to the English menu, `t` toggles quiet type-and-read mode, faked ID accepts the test number on Enter. Agda greets, caller gives a keyword, Agda routes.
- **Board (1:10–1:40):** "Every turn lands on the live React board." Show `./sh/watch-board.sh` / `watch-calls.sh`: turns, keywords with why, queue place; `watch-map.sh` graphical map with position marker; `./sh/show-map.sh` menu map. Run `./sh/show-call.sh` for the silent printable version.
- **iPhone + Watch (1:40–2:20):** "And it works from the couch: iPhone on speakerphone, Holdmate listens, then responds — queue alert fires on the Mac and mirrors to iPhone and Watch." Show `./sh/alert-demo.sh` firing the queue-place alert; `./sh/holdmate.sh` menu item 1 (board + talk), item 5 sound to speakers/AirPods.

## 2:20–2:50 Tech (30s)

> "Under the hood: a finite-state menu map learned per persona — the explorer tries words, the map grows every call. BFS lessons teach Holdmate to phone Agda by itself, headless. An intent ladder maps what you said to the keyword Agda understands, with teachable aliases for words she mishears."

VISUAL: `./sh/explore-demo.sh` map growing; `./sh/holdmate-call.sh` headless call; `./sh/learn-words.sh` alias teaching; `./sh/route-demo.sh` loop-free route to the queue.

## 2:50–3:10 Next steps (20s)

> "Next: real telephony with 46elks — funded account, live call to AF through ELK to compare against the scripted Agda — and the speakerphone loop: iPhone loudspeaker, Holdmate listens first, then answers, so a real queue works end to end."

VISUAL: 46elks dashboard + iPhone-on-speakerphone sketch.

## Close (one line)

> "Holdmate waits on hold, so you don't have to."
