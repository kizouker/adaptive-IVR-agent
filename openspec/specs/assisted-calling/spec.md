# Assisted Calling Specification

## Purpose

Hand the whole call to the app: chat or talk intake, identity-check ping, handover to the caller. From 01 "A good day" and Goals 4, 6–7. After the hackathon (not in v1–v6).

## User stories

- US-IVR-004: As a job seeker calling The Castle, I want the call to feel welcome instead of frustrating and stressful.
- US-IVR-006: As a job seeker calling The Castle, I want to reach a person with my question clear, and not have to call again.
- US-IVR-007: As a job seeker calling The Castle, I want to hand the whole call to the app, by chat or by clicking in the menu tree.

## Requirements

### Requirement: FN-REQ-IVR-014 Intake in own words

Holdmate SHALL ask "What's your concern?" by chat or talk and accept the answer in the caller's own words. (Story: US-IVR-007)

#### Scenario: Chat or talk intake

- **WHEN** the caller opens Holdmate and describes the concern in their own words
- **THEN** Holdmate takes it as the call goal

### Requirement: FN-REQ-IVR-015 Two ways to start a call

The system SHALL offer two ways in: write in a chat what you need to call about, or click it in the menu tree and press Call; the app does the rest as far as it can. (Story: US-IVR-007)

#### Scenario: Start from chat

- **WHEN** the caller writes the concern in the chat
- **THEN** the app starts the call and steers as far as it can

#### Scenario: Start from the menu tree

- **WHEN** the caller clicks the concern in the menu tree and presses Call
- **THEN** the app starts the call and steers as far as it can

### Requirement: FN-REQ-IVR-016 Identity-check ping

The system SHALL ping the caller for the identity check; the caller approves on their phone and Holdmate never does it. (Story: US-IVR-007)

#### Scenario: Ping at the identity step

- **WHEN** the call reaches the identity check (in Sweden: BankID – type the personal ID number, approve in the app)
- **THEN** Holdmate pings the caller and waits for the approval

### Requirement: FN-REQ-IVR-017 Handover when a person answers

The system SHALL ping when a person answers, show the queue number, and hand the call over or keep both in the call. (Story: US-IVR-007)

#### Scenario: "You are number 3", then handover

- **WHEN** a person is about to answer ("You are number 3")
- **THEN** the phone buzzes, the queue number shows in a web widget, and the call is handed over to the caller – or both stay in the call

Note: the source also names the iPhone, but the iPhone app is "Not now" (04) – web widget first.

### Requirement: FN-REQ-IVR-018 Handover with a clear question

The system SHALL hand over with the caller's question clear and ready. (Story: US-IVR-006)

#### Scenario: Question ready at handover

- **WHEN** the call is handed over
- **THEN** the question is clear and ready ("ready and calm ... don't have to call again" still open – OQ-12)

### Requirement: FN-REQ-IVR-019 Any phone line

The system SHALL work for any phone line – The Castle is just one case. (Story: US-IVR-007)

#### Scenario: New line learned by training

- **WHEN** a new line is trained (explored and mapped)
- **THEN** assisted calls work on it

### Requirement: NF-REQ-IVR-001 (draft) Helpful and kind

Holdmate SHALL be helpful and kind, knowing the caller may be having a hard time. (Story: US-IVR-004)

#### Scenario: Kind voice in v5

- **WHEN** Holdmate talks in a full run from welcome to alert
- **THEN** it talks kindly (how kindness is tested still open – OQ-11)

### Requirement: NF-REQ-IVR-004 (draft) Any language

Holdmate SHALL serve callers in any language, whatever their situation, starting with the English branch (press 0).

#### Scenario: English branch first

- **WHEN** the caller presses 0 for English
- **THEN** the call continues in English (what the branch offers still open – OQ-05)
