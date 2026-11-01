# DESIGN-FN-REQ-IVR-024: Talk through agency MCP

- REQ ticket: [`### FN-REQ-IVR-024 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/agency-mcp/spec.md`](../../specs/agency-mcp/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`mcp, explorer`), D11
- Priority: future

## New or changed parts

- NEW `mcp.client`: stdio MCP client; `explorer` picks MCP route when a server is offered, else dials.

## Tests

- Unit: client calls against a mock MCP server.
- Client-style: case via MCP; assert no phone call was placed (line untouched).
- Integration: end-to-end case against the mock server.
