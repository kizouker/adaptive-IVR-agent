# Holdmate in agent-theory terms (AIMA ch. 2 + ch. 18)

Source: Russell & Norvig, *Artificial Intelligence: A Modern Approach*
(4th ed., 2020). Ch. 2 "Intelligent Agents", ch. 18 "Learning from Examples".
Ticket: T-037 (#39). Status: research note, not a design decision.

## 1. Ch. 2 extract: the rational agent

An **agent** is anything that perceives its environment through **sensors**
and acts on it through **actuators**. A **rational agent** acts to achieve
the best expected outcome given its percept history and built-in knowledge
(§2.1–2.2). Rationality is about the *decision procedure*, not perfection:
an agent can be rational and still fail when the environment hides
information (§2.2: "rationality vs. omniscience").

**PEAS** (§2.3): every agent design starts by naming its Task environment:
**P**erformance measure, **E**nvironment, **A**ctuators, **S**ensors.

**Environment taxonomy** (§2.3.2) — seven axes:

| Axis | Question it asks |
|---|---|
| Fully vs partially observable | Do sensors reveal the full state? |
| Single-agent vs multi-agent | Are there other agents to cooperate/compete with? |
| Deterministic vs stochastic | Is the next state fixed by current state + action? |
| Episodic vs sequential | Does each action stand alone, or do earlier acts shape later ones? |
| Static vs dynamic vs semidynamic | Does the world change while the agent thinks? (Semidynamic: it does not, but waiting costs score — e.g. chess with a clock.) |
| Discrete vs continuous | Finite states/percepts/actions, or not? |
| Known vs unknown | Is the transition model (the "rules") given, or must it be learned? |

**Agent types** (§2.4), simplest first: simple reflex (condition–action
rules) → model-based reflex (keeps an internal **state**: "how the world
evolves", "what my actions do") → goal-based ("what do I want?") →
utility-based ("how much do I want it?") → **learning agent** (§2.4.6):
a *performance element* (acts), a *critic* (feedback on how it went), a
*learning element* (improves the performance element), and a *problem
generator* (suggests informative new experiments).

**Explore vs exploit.** Ch. 2 names the learning agent; the trade-off itself
is treated under *online search in unknown environments* (ch. 4) and
reinforcement learning (ch. 21/22): **exploration** (try something new to
learn) vs **exploitation** (use what works to score now). An agent that only
exploits never learns; one that only explores never finishes.

## 2. Holdmate as a rational agent (PEAS)

| PEAS | Holdmate |
|---|---|
| Performance | Reach the right queue with no loops, no name trap (FN-REQ-IVR-010); correct queue number found (011); queue place known without listening (013); caller steps in only at identity check/handover (016/017) |
| Environment | AF Agda: a speech-driven phone dialog (practice robot in v1–v5, real line later) |
| Actuators | Speech (TTS/`say`), DTMF key presses, deliberate silence |
| Sensors | Call audio recordings (FN-REQ-IVR-001), transcripts via local STT (002) |

Holdmate's *percepts* are transcripts + derived facts (queue numbers);
its *actions* are utterances, key presses, and silence. Its rationality is
bounded by STT noise and by never seeing the robot's internal dialog state.

## 3. AF Agda environment on the seven axes

| Axis | Verdict | Evidence (our calls) |
|---|---|---|
| Partially observable | yes | We hear prompts, never the internal dialog state; STT adds noise; whole branches stay unvisited |
| Single-agent | training: yes | Practice robot is a fixed environment, not an opponent. (Real line: humans enter at handover — multi-agent then.) |
| Stochastic | yes | Same input can yield a no-match reprompt, a yes/no fallback, or progress; timeouts and queue lengths vary |
| Sequential | yes | Open question → topic → yes/no confirm → queue: every utterance constrains what comes next; a wrong word can reroute the whole call |
| Semidynamic | yes | The robot waits for input, but silence triggers no-input reprompts and timeouts — deliberating costs score |
| Discrete | effectively | Finite prompts, finite candidate utterances, finite keys; continuous audio is discretised by STT into text percepts |
| Unknown | yes | No published dialog tree or vocabulary; Holdmate must learn the transition model call by call |

Hardest combination (per §2.3.2): partially observable + stochastic +
sequential + unknown. That is exactly why the SAD (§4) prescribes a
simulator-first, evidence-tagged approach: learn the model where mistakes
are free.

## 4. Holdmate's agent architecture (ch. 2 terms)

| Learning-agent part (§2.4.6) | Holdmate part (SAD §5) |
|---|---|
| Performance element | caller: speaks/keypresses from keyword table + map position |
| Critic | step files (FN-REQ-IVR-003): each run scored (loop? queue reached?) |
| Learning element | map builder: steps → menu map + evidence tags (005/029) |
| Problem generator | explorer (009/027/028/030): picks the next informative experiment |
| Internal state (model-based reflex) | position marker `*` on the map during a call |

The explorer's explore/exploit rule of thumb: **explore** (unknown words,
silence probes, synonym checks) on the practice robot; **exploit** (known
short words from the map) on the real line and near the queue.

## 5. Ch. 18 extract: learning from examples

**Inductive learning** (§18.1): from a set of *examples* (input–output
pairs), find a *hypothesis* (a function) from a *hypothesis space* that fits
them and generalises to new inputs. Three load-bearing terms:

- **Hypothesis space**: the set of candidate explanations the learner can
  even express. A small space learns fast but may miss the truth.
- **Inductive bias** (§18.2): any preference for one hypothesis over
  another beyond the data (e.g. prefer simpler trees — Occam's razor).
  Learning is impossible without bias: data alone never picks a unique
  hypothesis.
- **Overfitting** (§18.3–18.4): a hypothesis that memorises the training
  examples (noise included) and fails on new ones. Cures: prefer simpler
  hypotheses, validate on held-out examples, gather more data.

§18.3's workhorse is **decision-tree learning**: each example is classified
by walking from the root through attribute tests to a leaf. The tree is a
direct fit for menu dialogs: node = prompt heard, edge = what we said,
leaf = where we ended up.

## 6. Ch. 18 mapped onto our learning problem

| Ch. 18 term | Holdmate meaning |
|---|---|
| Example | One step in a step file: (prompt heard, utterance/key/silence, what happened next) |
| Hypothesis | A menu-map edge or keyword-table entry: "at state S, saying W leads to S′" |
| Hypothesis space | All maps buildable from the candidate vocabulary (the *parlör*) + observed states |
| Inductive bias / prior knowledge | Website menus and published phone facts in `schemas/public-authority-ivr-target-seeds.json` (Target model): they say *what to try first*, never *what is true* |
| Learned theory | The Observed model: evidence-tagged map entries (observed/inferred/untested, FN-REQ-IVR-029) |
| Overfitting | A map that replays one lucky call and breaks on the next: same-state confusion, memorised queue numbers, one-word-per-state brittleness |
| Training set / test set | Practice-robot calls (train, unlimited) vs real-line calls (test, a few, user present — NF-REQ-IVR-003) |
| Active learning | Explorer (FN-REQ-IVR-009/027/028): synonym-equivalence, no-input vs no-match, and recovery probes are *chosen* examples, not random ones |

## 7. Answers to Rickard's terminology questions

- **The vocabulary word list ("parlör")** = in ch. 2 terms, part of the
  agent's **built-in knowledge** and the **action vocabulary** (what the
  actuators can say); in ch. 18 terms, the **inductive bias** that bounds
  the **hypothesis space**. Concretely: `candidate_utterances` in the
  target seeds JSON feed the keyword table (FN-REQ-IVR-004). It belongs to
  Holdmate (the agent), not to the practice robot (the environment) — the
  robot must react from its own script so training stays honest.
- **The map/knowledge** = in ch. 2 terms, the agent's learned **transition
  model** ("what my actions do"); in ch. 18 terms, the **learned
  hypothesis**. Target model (expectations) and Observed model (evidence)
  stay separate exactly so bias never masquerades as data.
- **Explore vs exploit** is AIMA vocabulary too, but lives in ch. 4
  (online search) / ch. 21–22 (reinforcement learning), not ch. 2.

## 8. What this changes (proposals, not decisions)

1. Score exploration explicitly: "map grew / new state confirmed" is the
   explorer's performance measure (FN-REQ-IVR-009), separate from the
   caller's "reached the queue".
2. Treat every map edge as a hypothesis with a revision rule (029): one
   counter-observation revises or rejects — the ch. 18 update step.
3. Keep a held-out practice script the explorer never trains on, as the
   overfitting check before any real-line test (NF-REQ-IVR-003).
