# Safety Specification

## Purpose

Rules that always hold: AI disclosure, privacy by design, restraint with the real line and real numbers. From 01 Rules (always).

## Requirements

### Requirement: FN-REQ-IVR-020 Say it is an AI

Holdmate SHALL say it is an AI when it talks.

#### Scenario: Disclosure on the practice robot

- **WHEN** Holdmate talks in a v5 run
- **THEN** it says it is an AI

#### Scenario: Disclosure on the real line

- **WHEN** Holdmate talks in a real call
- **THEN** it says it is an AI

### Requirement: NF-REQ-IVR-002 No personal data kept

The system SHALL keep no ID numbers, staff names or staff voices in logs, demos or GitHub.

#### Scenario: Staff part is cut

- **WHEN** a recording reaches the point where a staff member answers
- **THEN** the file is cut there before storing

#### Scenario: Scan finds nothing

- **WHEN** logs, demos and the repo are checked
- **THEN** they hold no ID numbers, staff names or staff voices

### Requirement: NF-REQ-IVR-003 Real-line restraint

The team SHALL use the real phone line only a few times and only with the user present; most testing happens against the practice robot.

#### Scenario: Practice robot by default

- **WHEN** testing during the hackathon
- **THEN** all testing runs against the practice robot ("a few" still open – OQ-13)

### Requirement: NF-REQ-IVR-005 Never test against 112

Tests SHALL never use 112 – it is for emergencies only.

#### Scenario: 112 is out of bounds

- **WHEN** test targets are picked
- **THEN** 112 is never among them

### Requirement: NF-REQ-IVR-006 Real-system experiments stay harmless

Real-system experiments SHALL be limited and controlled, and SHALL avoid disrupting services or occupying human agents unnecessarily.

#### Scenario: No human agent occupied

- **GIVEN** an experiment plan against a real line
- **WHEN** the plan is reviewed
- **THEN** it reaches no human agent and disrupts no service

#### Scenario: Limited and controlled

- **GIVEN** the approval in NF-REQ-IVR-003
- **WHEN** real-system experiments run
- **THEN** the number of calls stays within the approved limit
