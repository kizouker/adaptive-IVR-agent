Feature: Recording the robot voice
  Record the robot side of a call on the Mac for transcription and steps.

  @FN-REQ-IVR-001
  Scenario: Robot voice lands in a dated file
    When a recording runs against "BlackHole 16ch"
    Then ffmpeg saves mono 16000 Hz audio to "data/recordings/robot-YYYYMMDD-HHMMSS.wav"

  @FN-REQ-IVR-001
  Scenario: Sound switches back when done
    When the record script ends
    Then the Mac switches back to the earlier output and microphone via a trap

  @FN-REQ-IVR-001
  Scenario: Own mic is not recorded
    When a call is recorded
    Then the file holds only the other side of the call
