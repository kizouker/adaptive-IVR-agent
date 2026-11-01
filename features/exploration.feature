Feature: Exploration
  Holdmate explores the practice robot by itself and fills the map without looping.

  @FN-REQ-IVR-008 @FN-REQ-IVR-008-S01
  Scenario: Table word for a wanted outcome
    When Holdmate wants outcome X at a topic step
    Then it says the table's Y for X

  @FN-REQ-IVR-009 @FN-REQ-IVR-009-S01
  Scenario: Map grows with every call
    When Holdmate tries a word and hears the reply
    Then the new observation is added to the menu map

  @FN-REQ-IVR-010 @FN-REQ-IVR-010-S01
  Scenario: Queue reached, no loop
    When Holdmate runs against the practice robot
    Then it reaches the queue with no yes/no loop and no name trap

  @FN-REQ-IVR-027 @FN-REQ-IVR-027-S01
  Scenario: No-input versus no-match
    Given Holdmate is at a prompt on the practice robot
    When it stays silent once and answers unintelligibly once
    Then both the no-input and the no-match replies are recorded and compared

  @FN-REQ-IVR-027 @FN-REQ-IVR-027-S02
  Scenario: Correct a misunderstanding
    Given the robot has taken Holdmate to the wrong state
    When Holdmate issues a correction
    Then the reply shows whether the caller can recover

  @FN-REQ-IVR-027 @FN-REQ-IVR-027-S03
  Scenario: Find loops, dead ends and fallback paths
    Given an explored map with repeated visits
    When Holdmate reviews the transitions
    Then loops, dead ends and fallback paths are identified

  @FN-REQ-IVR-028 @FN-REQ-IVR-028-S01
  Scenario: Synonyms lead to the same state
    Given two synonymous expressions for one intent
    When Holdmate tries both
    Then the map records whether both reach the same state

  @FN-REQ-IVR-028 @FN-REQ-IVR-028-S02
  Scenario: Same state through different routes
    Given a known state
    When Holdmate approaches it through different routes
    Then the map records which routes reach it

  @FN-REQ-IVR-028 @FN-REQ-IVR-028-S03
  Scenario: DTMF equals speech
    Given a prompt accepting both keys and speech
    When Holdmate answers once by key and once by speech
    Then the map records whether both produce the same outcome
