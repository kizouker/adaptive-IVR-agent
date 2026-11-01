Feature: Transcription
  Turn the newest recording into text with Whisper.

  @FN-REQ-IVR-002
  Scenario: Swedish by default
    When transcription runs with no language set
    Then whisper-cli writes a ".txt" with the same name next to the wav and prints it, in Swedish

  @FN-REQ-IVR-002
  Scenario: English on request
    When transcription runs with "WHISPER_LANG=en"
    Then the text is transcribed in English

  @FN-REQ-IVR-002
  Scenario: Language guessed on request
    When transcription runs with "WHISPER_LANG=auto"
    Then Whisper guesses the language
