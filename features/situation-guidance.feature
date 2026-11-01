@future
Feature: Situation guidance
  Version 2: say the right thing for your situation.

  @FN-REQ-IVR-026
  Scenario: Sign-up wording
    When the caller wants to sign up again but is already signed up
    Then Holdmate names the right way to say it
