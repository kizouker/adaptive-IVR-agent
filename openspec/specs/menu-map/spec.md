# Menu Map Specification

## Purpose

Save each call as steps and draw the map from them: the keyword table and the menu graph with *. From 04 step 2, 01 Goals 1–2, v1 and v3.

## User stories

- US-IVR-001: As a job seeker calling The Castle, I want to understand the menu of The Doorkeeper, so that I know the exact keywords it understands.
- US-IVR-002: As a job seeker calling The Castle, I want to know where I am in the menu during the call.

## Requirements

### Requirement: FN-REQ-IVR-003 Save each call as steps

The system SHALL save each call as steps in a step file. (Story: US-IVR-002)

#### Scenario: One run creates a step file

- **WHEN** the mini practice robot runs
- **THEN** one run creates a step file

#### Scenario: A logged call becomes steps

- **WHEN** a call is written down (today by hand – "7 calls written down by hand")
- **THEN** its lines are stored as steps the map can be drawn from

### Requirement: FN-REQ-IVR-004 Keyword table

The system SHALL keep a table mapping each keyword to what it gets done, and the other way: "I want to do X → say Y". (Story: US-IVR-001)

#### Scenario: Keyword to outcome

- **WHEN** asked what a keyword gets done
- **THEN** the table returns where it leads

#### Scenario: Outcome to words

- **WHEN** asked "I want to do X"
- **THEN** the table returns which words to say (Y)

### Requirement: FN-REQ-IVR-005 Menu map with position

The system SHALL draw the menu map from the steps and mark the current position with a *. (Story: US-IVR-002)

#### Scenario: Star sits on the right step

- **WHEN** the map is drawn during a call
- **THEN** the * marks the step the caller is on

### Requirement: FN-REQ-IVR-029 Tag evidence levels in the map

The system SHALL tag every map entry as observed fact, inferred hypothesis or untested possibility, and allow hypotheses to be revised or rejected. (Story: US-IVR-002)

#### Scenario: Observation tagged with evidence

- **GIVEN** a reply heard on the practice robot
- **WHEN** it is added to the map
- **THEN** it is tagged as observed fact with its supporting evidence

#### Scenario: Hypothesis revised on counter-evidence

- **GIVEN** an inferred hypothesis in the map
- **WHEN** a new observation contradicts it
- **THEN** the hypothesis is revised or rejected
