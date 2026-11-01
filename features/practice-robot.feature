Feature: Practice robot
  A copy of AF Agda to test against instead of the real line.

  @FN-REQ-IVR-006 @FN-REQ-IVR-006-S01
  Scenario: Three lines play
    When the mini robot runs
    Then it plays 3 AF Agda lines made with "say"

  @FN-REQ-IVR-006 @FN-REQ-IVR-006-S02
  Scenario: Each line is saved as a step
    When a line plays
    Then it is saved as a step

  @FN-REQ-IVR-007 @FN-REQ-IVR-007-S01
  Scenario: Known word or key moves on
    When the caller says a known word or presses a known key
    Then the robot plays the next line

  @FN-REQ-IVR-007 @FN-REQ-IVR-007-S02
  Scenario: Unknown input is not understood
    When the caller says something unknown
    Then the robot answers with its "not understood" line

  @FN-REQ-IVR-007 @FN-REQ-IVR-007-S03
  Scenario: Yes and no are accepted at confirm
    When the robot asks a yes/no question
    Then "ja" and "nej" move on and other words stay

  @FN-REQ-IVR-030 @FN-REQ-IVR-030-S01
  Scenario: Silence gets a repeated prompt
    Given the robot waits for an answer
    When the caller stays silent
    Then the robot repeats the prompt

  @FN-REQ-IVR-030 @FN-REQ-IVR-030-S02
  Scenario: Repeated silence times out
    Given the caller has stayed silent before
    When the caller stays silent again
    Then the robot times out or follows its fallback path
