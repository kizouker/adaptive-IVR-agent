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

  @FN-REQ-IVR-007 @FN-REQ-IVR-007-S04
  Scenario: Role-play call as one persona
    Given a persona with an errand and vocabulary
    When Rickard calls with --as for that persona
    Then he sees the role card and his rounds are tagged with the persona for Holdmate training

  @FN-REQ-IVR-007 @FN-REQ-IVR-007-S05
  Scenario: Faked identification before the queue
    Given a talk call that reaches transfer
    When Agda asks for BankID or Freja identification
    Then the terminal offers a pre-filled test number, typed input is ignored, digits are never logged, and the call lands in the queue

  @FN-REQ-IVR-007 @FN-REQ-IVR-007-S06
  Scenario: Skip keys and live volume during a call
    Given a talk call is recording or Agda is speaking
    When Rickard presses any key
    Then recording stops early or playback skips, and + / - adjusts her volume within the call

  @FN-REQ-IVR-007 @FN-REQ-IVR-007-S07
  Scenario: Pressing 0 opens the English branch
    Given a talk call in the Swedish flow
    When Rickard presses 0
    Then Agda speaks the call-5 English path (menu, sub-menu, SMS, identification, queue) on DTMF digits with an English voice, and the board follows the english map to an officer

  @FN-REQ-IVR-007 @FN-REQ-IVR-007-S08
  Scenario: Handover beeps, then the officer answers
    Given a talk call that reaches the handover line
    When Agda finishes the served line
    Then DTMF beeps play while connecting and an officer answers in a different voice with its own speaker label on the board

  @FN-REQ-IVR-007 @FN-REQ-IVR-007-S09
  Scenario: Output toggles between speakers and AirPods mid-call
    Given a talk call is recording or Agda is speaking
    When Rickard presses a
    Then system output switches to the other device without restarting, and a missing device only warns

  @FN-REQ-IVR-007 @FN-REQ-IVR-007-S10
  Scenario: Quiet practice by typing and reading
    Given Rickard must work silently
    When he starts with --quiet
    Then he types instead of speaking (/sound at the prompt or t during waits turns sound on), muted lines still pause for keys, and the board still gets audio plus captions
