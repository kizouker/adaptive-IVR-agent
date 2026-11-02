Feature: Intent normalizer
  On keyword miss, a normalizer maps noisy STT onto the closed
  persona vocab or abstains back to the miss ladder.

  Scenario: Noisy utterance is rescued
    When the caller says a noisy variant of a vocab word
    Then the normalizer maps it to the closed keyword

  Scenario: Garbage abstains
    When the caller says something outside the vocab
    Then the normalizer abstains and the ladder continues

  Scenario: Exact hits never consult the normalizer
    When the caller says an exact vocab word
    Then it resolves without calling the normalizer
