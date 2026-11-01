Feature: Queue ticket widget
  A small always-on-top window shows the queue ticket without opening
  the full board.

  Scenario: Ticket parses from board state
    When board state holds queue turns
    Then the widget shows the latest place and total

  Scenario: Board unreachable shows a dash
    When the board server cannot be reached
    Then the widget shows a dash instead of a number
