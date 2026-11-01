Feature: Safety
  Rules that always hold: AI disclosure, privacy, restraint with the real line.

  @FN-REQ-IVR-020
  Scenario: Disclosure on the practice robot
    When Holdmate talks in a v5 run
    Then it says it is an AI

  @FN-REQ-IVR-020
  Scenario: Disclosure on the real line
    When Holdmate talks in a real call
    Then it says it is an AI

  @NF-REQ-IVR-002
  Scenario: Staff part is cut
    When a recording reaches the point where a staff member answers
    Then the file is cut there before storing

  @NF-REQ-IVR-002
  Scenario: Scan finds nothing
    When logs, demos and the repo are checked
    Then they hold no ID numbers, staff names or staff voices

  @NF-REQ-IVR-003
  Scenario: Practice robot by default
    When testing during the hackathon
    Then all testing runs against the practice robot

  @NF-REQ-IVR-005
  Scenario: 112 is out of bounds
    When test targets are picked
    Then 112 is never among them

  @NF-REQ-IVR-006
  Scenario: No human agent occupied
    Given an experiment plan against a real line
    When the plan is reviewed
    Then it reaches no human agent and disrupts no service

  @NF-REQ-IVR-006
  Scenario: Limited and controlled
    Given the approval in NF-REQ-IVR-003
    When real-system experiments run
    Then the number of calls stays within the approved limit
