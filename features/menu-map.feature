Feature: Menu map
  Save each call as steps; keep the keyword table; draw the map with the position marked.

  @FN-REQ-IVR-003 @FN-REQ-IVR-003-S01
  Scenario: One run creates a step file
    When the mini practice robot runs
    Then one run creates a step file

  @FN-REQ-IVR-003 @FN-REQ-IVR-003-S02
  Scenario: A logged call becomes steps
    When a call is written down
    Then its lines are stored as steps the map can be drawn from

  @FN-REQ-IVR-004 @FN-REQ-IVR-004-S01
  Scenario: Keyword to outcome
    When asked what a keyword gets done
    Then the table returns where it leads

  @FN-REQ-IVR-004 @FN-REQ-IVR-004-S02
  Scenario: Outcome to words
    When asked "I want to do X"
    Then the table returns which words to say

  @FN-REQ-IVR-005 @FN-REQ-IVR-005-S01
  Scenario: Star sits on the right step
    When the map is drawn during a call
    Then the "*" marks the step the caller is on

  @FN-REQ-IVR-029 @FN-REQ-IVR-029-S01
  Scenario: Observation tagged with evidence
    Given a reply heard on the practice robot
    When it is added to the map
    Then it is tagged as observed fact with its supporting evidence

  @FN-REQ-IVR-029 @FN-REQ-IVR-029-S02
  Scenario: Hypothesis revised on counter-evidence
    Given an inferred hypothesis in the map
    When a new observation contradicts it
    Then the hypothesis is revised or rejected

  @FN-REQ-IVR-005 @FN-REQ-IVR-005-S02
  Scenario: Traveled path lights up with branches
    Given a call with turns across several states
    When the board draws the flow graph
    Then visited states are lit, the live position pulses, and observed transitions (including skips) are drawn

  @FN-REQ-IVR-005 @FN-REQ-IVR-005-S03
  Scenario: New phrases type out live
    Given a new turn arrives on the board
    When it is shown the first time
    Then its text types out, or appears instantly with reduced motion

  @FN-REQ-IVR-005 @FN-REQ-IVR-005-S04
  Scenario: Details tab shows the traveled path as a tree
    Given a call with turns across several states
    When the details tab draws the tree
    Then visited states nest rightward with counts, edges carry the caller's words, and the live position is marked

  @FN-REQ-IVR-005 @FN-REQ-IVR-005-S05
  Scenario: Conversation shows latest first with show all
    Given a call with more than two turns
    When the thread renders
    Then the two latest turns show first with fast typing, and a button reveals the rest

  @FN-REQ-IVR-005 @FN-REQ-IVR-005-S06
  Scenario: Cinema subtitles with history behind a click
    Given a live call with turns
    When the details tab renders
    Then one phrase at a time shows as big subtitles, and a history button reveals all turns latest-first
