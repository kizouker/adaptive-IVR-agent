Feature: Queue alert
  Find the queue number in transcribed speech and alert the caller on the Mac.

  @FN-REQ-IVR-011 @FN-REQ-IVR-011-S01
  Scenario: Det är N samtal före dig
    When the text holds "Det är 38 samtal före dig"
    Then the queue place is 38

  @FN-REQ-IVR-011 @FN-REQ-IVR-011-S02
  Scenario: Anropare nummer N
    When the text holds "anropare nummer 12"
    Then the queue place is 12

  @FN-REQ-IVR-011 @FN-REQ-IVR-011-S03
  Scenario: Din plats är number
    When the text holds "Din plats är: 47"
    Then the queue place is 47

  @FN-REQ-IVR-012 @FN-REQ-IVR-012-S01
  Scenario: Alert at number 2
    When the queue place reaches 2
    Then the Mac alerts

  @FN-REQ-IVR-013 @FN-REQ-IVR-013-S01
  Scenario: Place known without listening
    When the queue place changes
    Then the shown number updates without the caller listening to the call
