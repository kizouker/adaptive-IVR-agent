# Practice Robot Specification

## Purpose

A copy of AF Agda to test against instead of the real line, built from real calls. From 04 step 3, v1 (mini) and v4 (reactive).

## Requirements

### Requirement: FN-REQ-IVR-006 Mini robot plays three lines

The practice robot SHALL play 3 AF Agda lines made with `say`, and save each line as a step.

#### Scenario: Three lines play

- **WHEN** the mini robot runs
- **THEN** it plays 3 AF Agda lines made with `say`

#### Scenario: Each line is saved as a step

- **WHEN** a line plays
- **THEN** it is saved as a step (see FN-REQ-IVR-003)

### Requirement: FN-REQ-IVR-007 Reactive robot

The practice robot SHALL react to words and key presses, including "not understood" and yes/no.

#### Scenario: Known word or key moves on

- **WHEN** the caller says a known word or presses a known key
- **THEN** the robot plays the next line

#### Scenario: Unknown input is not understood

- **WHEN** the caller says something unknown
- **THEN** the robot answers with its "not understood" line

#### Scenario: Yes and no are accepted at confirm

- **WHEN** the robot asks a yes/no question
- **THEN** "ja" and "nej" move on and other words stay

### Requirement: FN-REQ-IVR-030 Handle silence and timeouts

The practice robot SHALL answer caller silence with no-input prompts, repeated prompts and a timeout.

#### Scenario: Silence gets a repeated prompt

- **GIVEN** the robot waits for an answer
- **WHEN** the caller stays silent
- **THEN** the robot repeats the prompt (no-input)

#### Scenario: Repeated silence times out

- **GIVEN** the caller has stayed silent before
- **WHEN** the caller stays silent again
- **THEN** the robot times out or follows its fallback path
