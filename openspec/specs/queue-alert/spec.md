# Queue Alert Specification

## Purpose

Find the queue number in transcribed speech and alert the caller, first on the Mac. From 04 step 5, 01 Goal 5, v2 and v5, and the README.md goal.

## User stories

- US-IVR-005: As a job seeker calling The Castle, I want the wait to be easy and to use the time for other things, knowing my place without listening. (The AirPods call, 03.)

## Requirements

### Requirement: FN-REQ-IVR-011 Find the queue number

The system SHALL find the caller's place in the queue in transcribed text. (Story: US-IVR-005)

#### Scenario: "Det är N samtal före dig"

- **WHEN** the text holds "Det är 38 samtal före dig"
- **THEN** the queue place is 38

#### Scenario: "anropare nummer N"

- **WHEN** the text holds "anropare nummer 12"
- **THEN** the queue place is 12

#### Scenario: "Din plats är: <number>"

- **WHEN** the text holds "Din plats är: 47"
- **THEN** the queue place is 47

### Requirement: FN-REQ-IVR-012 Alert on the Mac near the front

The system SHALL alert on the Mac when the queue is near the front. (Story: US-IVR-005)

#### Scenario: Alert at number 2

- **WHEN** the queue place reaches 2
- **THEN** the Mac alerts

### Requirement: FN-REQ-IVR-013 Queue counts down

The system SHALL show the queue counting down so the caller knows their place without listening. (Story: US-IVR-005)

#### Scenario: Place known without listening

- **WHEN** the queue place changes
- **THEN** the shown number updates without the caller listening to the call
