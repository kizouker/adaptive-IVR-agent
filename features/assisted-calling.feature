Feature: Assisted calling
  Hand the whole call to the app: intake, identity-check ping, handover.

  @FN-REQ-IVR-014 @FN-REQ-IVR-014-S01
  Scenario: Chat or talk intake
    When the caller opens Holdmate and describes the concern in their own words
    Then Holdmate takes it as the call goal

  @FN-REQ-IVR-015 @FN-REQ-IVR-015-S01
  Scenario: Start from chat
    When the caller writes the concern in the chat
    Then the app starts the call and steers as far as it can

  @FN-REQ-IVR-015 @FN-REQ-IVR-015-S02
  Scenario: Start from the menu tree
    When the caller clicks the concern in the menu tree and presses Call
    Then the app starts the call and steers as far as it can

  @FN-REQ-IVR-016 @FN-REQ-IVR-016-S01
  Scenario: Ping at the identity step
    When the call reaches the identity check
    Then Holdmate pings the caller and waits for the approval on their phone

  @FN-REQ-IVR-017 @FN-REQ-IVR-017-S01
  Scenario: You are number 3, then handover
    When a person is about to answer
    Then the phone buzzes, the queue number shows in a web widget, and the call is handed over to the caller or both stay in the call

  @FN-REQ-IVR-018 @FN-REQ-IVR-018-S01
  Scenario: Question ready at handover
    When the call is handed over
    Then the question is clear and ready

  @FN-REQ-IVR-019 @FN-REQ-IVR-019-S01
  Scenario: New line learned by training
    When a new line is trained
    Then assisted calls work on it

  @NF-REQ-IVR-001 @draft @NF-REQ-IVR-001-S01
  Scenario: Kind voice in v5
    When Holdmate talks in a full run from welcome to alert
    Then it talks kindly

  @NF-REQ-IVR-004 @draft @NF-REQ-IVR-004-S01
  Scenario: English branch first
    When the caller presses 0 for English
    Then the call continues in English
