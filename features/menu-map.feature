Feature: Menu map
  Save each call as steps; keep the keyword table; draw the map with the position marked.

  @FN-REQ-IVR-003
  Scenario: One run creates a step file
    When the mini practice robot runs
    Then one run creates a step file

  @FN-REQ-IVR-003
  Scenario: A logged call becomes steps
    When a call is written down
    Then its lines are stored as steps the map can be drawn from

  @FN-REQ-IVR-004
  Scenario: Keyword to outcome
    When asked what a keyword gets done
    Then the table returns where it leads

  @FN-REQ-IVR-004
  Scenario: Outcome to words
    When asked "I want to do X"
    Then the table returns which words to say

  @FN-REQ-IVR-005
  Scenario: Star sits on the right step
    When the map is drawn during a call
    Then the "*" marks the step the caller is on

  @FN-REQ-IVR-029
  Scenario: Observation tagged with evidence
    Given a reply heard on the practice robot
    When it is added to the map
    Then it is tagged as observed fact with its supporting evidence

  @FN-REQ-IVR-029
  Scenario: Hypothesis revised on counter-evidence
    Given an inferred hypothesis in the map
    When a new observation contradicts it
    Then the hypothesis is revised or rejected
