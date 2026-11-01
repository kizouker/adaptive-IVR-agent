# Recording Specification

## Purpose

Record calls on the Mac so speech can be turned into text and steps. From 04 step 1 and docs/recording-setup.md. Built in v0 (done).

## Requirements

### Requirement: FN-REQ-IVR-001 Record the robot voice

The system SHALL record the other side of the call (the robot voice) to a wav file in data/recordings.

#### Scenario: Robot voice lands in a dated file

- **WHEN** a recording runs against BlackHole 16ch
- **THEN** ffmpeg saves mono 16000 Hz audio to data/recordings/robot-YYYYMMDD-HHMMSS.wav

#### Scenario: Sound switches back when done

- **WHEN** the script ends (q, Ctrl+C or normal end)
- **THEN** the Mac switches back to the earlier output and microphone via a trap

#### Scenario: Own mic is not recorded

- **WHEN** a call is recorded
- **THEN** the file holds only the other side – "Your own mic is not recorded."
