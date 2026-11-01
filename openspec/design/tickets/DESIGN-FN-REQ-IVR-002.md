# DESIGN-FN-REQ-IVR-002: Transcribe the newest recording

- REQ ticket: [`### FN-REQ-IVR-002 …`](../../tickets.md) (acceptance copied there, not here)
- Spec: [`specs/transcription/spec.md`](../../specs/transcription/spec.md)
- SAD: [`SAD.md`](../SAD.md) §5 (`ears`), D5
- Priority: done (v0)

## New or changed parts

- Keep `sh/transcribe-latest.sh` as is (done in v0).
- NEW `ears.transcribe(path, lang)`: whisper-cli wrapper; `WHISPER_LANG` default `sv`, `en`, `auto` as constants.

## Tests

- Unit: language mapping sv/en/auto (mock whisper-cli).
- Client-style: newest wav → `.txt` next to it, text printed.
- Integration: record → transcribe chain with FN-REQ-IVR-001.
