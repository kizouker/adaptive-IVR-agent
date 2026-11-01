# Real-line Calling Specification (future)

## Purpose

After the hackathon: a few real calls with the user present, then fully on its own once the legal questions are clear. From 04 step 6 and 01 "Later – fully on its own".

## Requirements

### Requirement: FN-REQ-IVR-021 (future) Real calls with the caller present

Holdmate SHALL place real-line calls with the caller present, saying it is an AI, while the caller does the identity check.

#### Scenario: Few calls, user there

- **WHEN** a real call runs
- **THEN** the user is present, Holdmate says it is an AI, and the user approves the identity check

### Requirement: FN-REQ-IVR-022 (future) Fully on its own

Holdmate SHALL handle a case from start to end, bringing the caller in only for the identity check or when a person needs to talk.

#### Scenario: Caller only where they must

- **WHEN** a case runs end to end (after the hackathon, once the legal questions are clear – OQ-14)
- **THEN** the caller steps in only for the identity check or to talk to a person
