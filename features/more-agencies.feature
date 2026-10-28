@future
Feature: More agencies
  After The Castle: more lines with the same approach.

  @FN-REQ-IVR-023
  Scenario: Same approach, new line
    When a new agency line is added
    Then training, mapping and assisted calling work as on The Castle
