@future
Feature: Agency MCP
  Agencies offer MCP servers; Holdmate talks to them directly and spans cases.

  @FN-REQ-IVR-024 @FN-REQ-IVR-024-S01
  Scenario: No phone robot needed
    When an agency offers an MCP server
    Then Holdmate uses it directly instead of calling

  @FN-REQ-IVR-025 @FN-REQ-IVR-025-S01
  Scenario: a-kassa to Försäkringskassan
    When a case moves between the unemployment fund and the Swedish Social Insurance Agency
    Then Holdmate handles it with the caller in the loop
