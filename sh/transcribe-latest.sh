#!/usr/bin/env bash
# Turn a recording into text with whisper.cpp.
# No argument = the newest file in data/recordings.
# The text is saved next to the recording, as a .txt file with the same name.
set -euo pipefail

MODEL="$HOME/models/whisper/ggml-small.bin"
# Language: sv (default), en, or auto. Example: WHISPER_LANG=en ./sh/transcribe-latest.sh
LANGUAGE="${WHISPER_LANG:-sv}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/data/recordings"

if [ ! -f "$MODEL" ]; then
  echo "Model not found: $MODEL"
  echo "Download it first (see docs/recording-setup.md, step 7)."
  exit 1
fi

FILE="${1:-$(ls -t "$REC_DIR"/*.wav 2>/dev/null | head -1 || true)}"
if [ -z "$FILE" ]; then
  echo "No recordings found in $REC_DIR"
  exit 1
fi

# Don't run Whisper on silence: it makes up text when there is nothing to hear
if ! "$SCRIPT_DIR/check-recording.sh" "$FILE"; then
  echo "Skipping Whisper."
  exit 1
fi

echo "Transcribing $FILE (language: $LANGUAGE) ..."
# -mc 0  = don't use earlier text as a hint (stops loops like the same sentence over and over)
# -sns   = skip non-speech sounds like music and beeps
whisper-cli -m "$MODEL" -l "$LANGUAGE" -np -mc 0 -sns -otxt -of "${FILE%.wav}" -f "$FILE"

echo
echo "Saved: ${FILE%.wav}.txt"
cat "${FILE%.wav}.txt"
