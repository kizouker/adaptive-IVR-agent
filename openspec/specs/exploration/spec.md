# Exploration Specification

## Purpose

Holdmate explores the practice robot by itself: tries words, picks from the keyword table, fills the map, never loops. From 04 step 4, 01 Goal 3, v4.

## User stories

- US-IVR-003: As a job seeker calling The Castle, I want to pick the right choice at once, without "What did you say?" or "Please answer yes or no" loops.

## Requirements

### Requirement: FN-REQ-IVR-008 Pick words from the keyword table

Holdmate SHALL pick words from the keyword table when talking to the practice robot. (Story: US-IVR-003)

#### Scenario: Table word for a wanted outcome

- **WHEN** Holdmate wants outcome X at a topic step
- **THEN** it says the table's Y for X

### Requirement: FN-REQ-IVR-009 Try words and fill the map

Holdmate SHALL try words on the practice robot and fill in the map by itself. (Story: US-IVR-003)

#### Scenario: Map grows with every call

- **WHEN** Holdmate tries a word and hears the reply
- **THEN** the new observation is added to the menu map

### Requirement: FN-REQ-IVR-010 Reach the queue without a loop

Holdmate SHALL reach the right place without getting stuck in a loop. (Story: US-IVR-003)

#### Scenario: Queue reached, no loop

- **WHEN** Holdmate runs against the practice robot
- **THEN** it reaches the queue with no yes/no loop and no name trap

### Requirement: FN-REQ-IVR-027 Probe recovery behaviour

Holdmate SHALL probe how the phone robot handles silence, misunderstanding, correction and fallback. (Story: US-IVR-003)

#### Scenario: No-input versus no-match

- **GIVEN** Holdmate is at a prompt on the practice robot
- **WHEN** it stays silent once and answers unintelligibly once
- **THEN** both the no-input and the no-match replies are recorded and compared

#### Scenario: Correct a misunderstanding

- **GIVEN** the robot has taken Holdmate to the wrong state
- **WHEN** Holdmate issues a correction
- **THEN** the reply shows whether the caller can recover

#### Scenario: Find loops, dead ends and fallback paths

- **GIVEN** an explored map with repeated visits
- **WHEN** Holdmate reviews the transitions
- **THEN** loops, dead ends and fallback paths are identified

### Requirement: FN-REQ-IVR-028 Verify same-state equivalence

Holdmate SHALL verify whether different inputs lead to the same dialog state. (Story: US-IVR-002)

#### Scenario: Synonyms lead to the same state

- **GIVEN** two synonymous expressions for one intent
- **WHEN** Holdmate tries both
- **THEN** the map records whether both reach the same state

#### Scenario: Same state through different routes

- **GIVEN** a known state
- **WHEN** Holdmate approaches it through different routes
- **THEN** the map records which routes reach it

#### Scenario: DTMF equals speech

- **GIVEN** a prompt accepting both keys and speech
- **WHEN** Holdmate answers once by key and once by speech
- **THEN** the map records whether both produce the same outcome
