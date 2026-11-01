# DESIGN-FN-REQ-IVR-014: Intake in own words

- REQ ticket: [`### FN-REQ-IVR-014 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/assisted-calling/spec.md`](../../specs/assisted-calling/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`intake`)
- Priority: post (after hackathon)

## New or changed parts

- NEW `intake.goal_from_text(text)`: chat message → call goal. Talk input later, same return type.

## Tests

- Unit: free-word text → goal object.
- Client-style: chat 'I need to sign up again' → goal taken.
- Integration: intake goal starts an explorer run.
