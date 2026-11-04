"""Single WAV writer: 16-bit mono PCM files (R3).

One place for every `wave.open(path, "wb")` in the codebase. Callers pass
raw frames and the sample rate; output bytes are identical to the three
writers this replaces (audio rec, DTMF beeps, menu chiptune).
"""
from __future__ import annotations

import wave
from pathlib import Path


def write_wav(path: str | Path, frames: bytes, rate: int) -> str:
    """Write FRAMES as 16-bit mono PCM at RATE Hz; make parents; return str."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(target), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(frames)
    return str(target)
