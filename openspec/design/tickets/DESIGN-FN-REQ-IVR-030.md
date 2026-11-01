# DESIGN-FN-REQ-IVR-030: Handle silence and timeouts

- REQ ticket: [`### FN-REQ-IVR-030 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/practice-robot/spec.md`](../../specs/practice-robot/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`robot, line`)
- Priority: post (after hackathon)

## New or changed parts

- CHANGED `robot`: silence → repeated no-input prompts, then timeout or fallback.
- CHANGED `line.listen`: timeout parameter.

## Tests

- Unit: silence → repeated prompt → timeout/fallback.
- Client-style: silent run against the practice robot.
- Integration: explorer silence experiment → map fallback.
