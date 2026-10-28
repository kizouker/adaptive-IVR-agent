# IVR Explorer – Domain Research & Solution Concept

**Status:** Domain research and preliminary solution concept  
**Purpose:** Input for requirements analysis and architectural discussions  
**Not:** An approved requirements specification or technical design

## 1. Background

The project's overall vision has already been communicated and should remain unchanged.

We have subsequently explored how traditional and modern Interactive Voice Response (IVR) systems operate, particularly speech-driven telephone systems and contact center platforms.

The purpose of this document is to transfer the domain knowledge we have acquired and the solution ideas that emerged from our research.

## 2. Domain Knowledge

### Telephony and Communication

- **SIP:** Call signaling and session management
- **RTP/SRTP:** Audio transport
- **DTMF:** Telephone keypad input
- **ASR:** Automatic Speech Recognition
- **TTS:** Text-to-Speech synthesis
- **IVR:** Interactive voice dialogs and call routing

### Dialog Structure

IVR systems can be modeled using concepts such as:

- Dialog states
- State transitions
- Intents – the caller's underlying goals
- Utterances – alternative ways of expressing an intent
- Slots – parameters or information collected during a dialog
- Speech grammars and synonyms
- Routing to queues, services, or human agents

Traditional grammar-based IVR systems and modern intent-based Natural Language Understanding (NLU) systems may implement these concepts differently.

### Error Handling and Navigation

Particularly relevant mechanisms include:

- **No-input:** The caller does not respond
- **No-match:** The caller's response does not match an accepted grammar or interpretation
- Timeouts and repeated prompts
- Fallback strategies and alternative menus
- Interruptions and corrections
- Returning to previous dialog states
- Transferring to a human agent

These mechanisms are especially relevant when investigating whether callers can recover from misunderstandings.

### Technologies and Platforms Investigated

Our research has included:

- Telia CallGuide / Telia ACE
- VoiceXML (VXML)
- Speech Recognition Grammar Specification (SRGS)
- Five9 IVR scripting
- Graphical IVR design tools
- Network-hosted and on-premises IVR architectures

These technologies provide examples of possible implementations.

**Important:** We have not established which IVR platform the Swedish Public Employment Service (Arbetsförmedlingen) currently uses, nor how its internal dialog logic is implemented.

The project should not rely on unverified assumptions about any particular vendor.

## 3. Preliminary Solution Concept

The central concept is an AI agent capable of exploring an unknown IVR system through telephone conversations and learning from the observed behavior.

The agent should not merely execute predefined test scripts. It should formulate hypotheses, select experiments, analyze outcomes, and progressively develop a model of the target system.

### Proposed Exploration and Learning Cycle

1. Observe a prompt or dialog state.
2. Formulate hypotheses about possible responses and transitions.
3. Select an informative experiment.
4. Respond using speech, DTMF, or silence.
5. Analyze the IVR system's response.
6. Update the agent's knowledge model.
7. Select the next experiment.

This resembles model-based testing and active learning, although the precise approach has not yet been selected.

### Preliminary Modeling Concept

We have discussed separating the agent's knowledge into two complementary models.

**Target Model**

Represents prior domain knowledge, expected structures, and hypotheses about how an IVR system might behave.

It may contain candidate intents, utterances, slots, dialog states, and transitions.

**Observed Model**

Represents actual observations collected during experiments, including recorded responses, identified states, tested transitions, supporting evidence, and uncertainty.

This separation would allow the agent to use prior knowledge without confusing assumptions with verified observations.

**This is a proposed architectural concept, not an approved design decision.**

### Knowledge-Guided Exploration

Domain knowledge should help the agent choose meaningful experiments.

Examples include:

- Testing whether synonymous expressions lead to the same dialog state.
- Comparing no-input and no-match behavior.
- Investigating whether callers can correct a misunderstanding.
- Identifying loops, dead ends, and fallback paths.
- Testing whether the same state can be reached through different routes.
- Exploring whether DTMF and spoken responses produce equivalent outcomes.

The agent should distinguish between:

- Observed facts
- Inferred hypotheses
- Untested possibilities

The ability to revise or reject earlier hypotheses is an important part of the concept.

## 4. Open Architectural Questions

The following decisions remain open:

- How should the dialog graph be represented and stored?
- How should the agent determine whether two observations correspond to the same dialog state?
- How should evidence, hypotheses, and uncertainty be modeled?
- How should the agent prioritize experiments?
- How should speech recognition, speech synthesis, DTMF, and call control be integrated?
- How should observations be logged and made reproducible?
- How should the resulting dialog structure be visualized?
- How should exploration quality and learning progress be evaluated?
- How should the system distinguish between a genuinely new state and a variation of an existing state?

These questions should be explored during requirements analysis and architectural evaluation rather than resolved prematurely.

## 5. Scope and Constraints

Initial development and testing should use a controlled, locally simulated IVR environment.

Experiments involving real public-sector telephone systems should be limited, controlled, and designed to avoid disrupting services or occupying human agents unnecessarily.

The solution should aim for general applicability rather than being tightly coupled to a particular organization or IVR vendor.

No assumptions should be made about whether a target system uses VoiceXML, SRGS, Telia ACE, a particular ASR engine, or an intent-based NLU architecture.

Technology selection should follow requirements analysis rather than precede it.

## 6. Assignment for the Requirements Agent

Use this document alongside the project's previously established vision.

Your task is to:

1. Preserve the distinction between vision, domain knowledge, solution concepts, requirements, and technical design.
2. Identify which ideas should become functional or non-functional requirements.
3. Treat the Target Model and Observed Model as architectural hypotheses to evaluate, not established decisions.
4. Identify assumptions, risks, dependencies, and unresolved questions.
5. Consider alternative approaches where appropriate.
6. Propose a minimal demonstrable solution without prematurely committing to specific technologies.
7. Preserve traceability between domain knowledge, proposed requirements, and eventual design decisions.

### Working Principles

Do not treat this research document as a final specification.

Do not silently convert exploratory ideas into mandatory requirements.

Clearly identify which conclusions are supported by domain knowledge and which are proposed design choices.

Challenge assumptions constructively and present relevant alternatives.

**Do not begin implementation yet. First discuss your interpretation of the problem, the proposed requirements, and the most important architectural alternatives with the project owner.**