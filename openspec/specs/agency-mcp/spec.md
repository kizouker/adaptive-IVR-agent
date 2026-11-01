# Agency MCP Specification (future)

## Purpose

Further ahead: agencies offer MCP servers (some built on REST APIs they already have); Holdmate talks to agencies directly and spans cases across them. From 04 step 8 and 01 "Further ahead".

## Requirements

### Requirement: FN-REQ-IVR-024 (future) Talk through agency MCP

Holdmate SHALL talk to the agencies through their MCP servers instead of the phone robots.

#### Scenario: No phone robot needed

- **WHEN** an agency offers an MCP server
- **THEN** Holdmate uses it directly instead of calling

### Requirement: FN-REQ-IVR-025 (future) Cases across agencies

Holdmate SHALL handle cases spanning several agencies with the caller in the loop.

#### Scenario: a-kassa to Försäkringskassan

- **WHEN** a case moves between the unemployment fund (a-kassa) and the Swedish Social Insurance Agency (Försäkringskassan)
- **THEN** Holdmate handles it with the caller in the loop
