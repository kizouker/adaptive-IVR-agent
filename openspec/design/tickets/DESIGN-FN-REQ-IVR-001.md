# DESIGN-FN-REQ-IVR-001: Record the robot voice

- REQ ticket: [`### FN-REQ-IVR-001 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/recording/spec.md`](../../specs/recording/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`cutter (hook point only)`), D8
- Priority: done (v0)

## New or changed parts

- Keep `sh/record-call.sh` as is (done in v0).
- NEW hook point: record the staff-answer timestamp so `cutter` (NF-REQ-IVR-002) can cut later.

## Tests

- Unit: trap restores the audio device on q/Ctrl+C/normal end (mock the switcher).
- Client-style: run the script; dated wav exists, mono 16000 Hz, robot side only.
- Integration: record → transcribe chain with FN-REQ-IVR-002.
