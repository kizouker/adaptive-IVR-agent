@future
Feature: Real-line calling
  After the hackathon: real calls with the user present, then fully on its own.

  @FN-REQ-IVR-021 @FN-REQ-IVR-021-S01
  Scenario: Few calls, user there
    When a real call runs
    Then the user is present, Holdmate says it is an AI, and the user approves the identity check

  @FN-REQ-IVR-022 @FN-REQ-IVR-022-S01
  Scenario: Caller only where they must
    When a case runs end to end
    Then the caller steps in only for the identity check or to talk to a person
