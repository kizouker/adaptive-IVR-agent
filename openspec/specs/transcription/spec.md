# Transcription Specification

## Purpose

Turn speech into text with Whisper. From 04 step 1 and recording-setup.md §7. v0 done; v2 uses it to find queue numbers.

## Requirements

### Requirement: FN-REQ-IVR-002 Transcribe the newest recording

The system SHALL turn the newest recording into text with Whisper and save the text next to the recording.

#### Scenario: Swedish by default

- **WHEN** transcription runs with no language set
- **THEN** whisper-cli writes a .txt with the same name next to the wav and prints it, in Swedish

#### Scenario: English on request

- **WHEN** WHISPER_LANG=en is set
- **THEN** the text is transcribed in English

#### Scenario: Language guessed on request

- **WHEN** WHISPER_LANG=auto is set
- **THEN** Whisper guesses the language
