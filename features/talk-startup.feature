Feature: Talk startup behavior
  Starting a talk must not surprise Rickard: the system volume stays
  untouched unless --floor is given, and the quiet choice is remembered.

  Scenario: System volume untouched by default
    When talk check runs without --floor
    Then it reports the system volume is left untouched

  Scenario: Floor levels the volume when asked
    When talk check runs with --floor
    Then it reports it would unmute and raise below the floor

  Scenario: Quiet choice is remembered
    When the quiet file holds 1 and talk check runs
    Then it starts in quiet mode

  Scenario: Flags override and save the quiet choice
    When talk check runs with --sound
    Then it starts with sound and remembers 0
