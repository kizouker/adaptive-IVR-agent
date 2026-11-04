"""DTMF connecting beeps for the handover: stdlib WAV synth, no dependencies.

When Roksolana hands over, the call beeps like touch tones (tyt-tyt-tyt) while
connecting, then the officer answers. If Rickard drops a DTMF
library into the repo, this module is the seam to swap it in.
"""

import math
import struct
from pathlib import Path

from adaptive_ivr_agent.wavio import write_wav

SAMPLE_RATE = 44100
AMPLITUDE = 0.35
BEEP_SECONDS = 0.2
GAP_SECONDS = 0.2
BEEPS = 3
CONNECT_DIGIT = "1"

# Standard DTMF pad: (low Hz, high Hz) per key.
DTMF_FREQS = {
    "1": (697, 1209),
    "2": (697, 1336),
    "3": (697, 1477),
    "4": (770, 1209),
    "5": (770, 1336),
    "6": (770, 1477),
    "7": (852, 1209),
    "8": (852, 1336),
    "9": (852, 1477),
    "0": (941, 1336),
    "*": (941, 1209),
    "#": (941, 1477),
}


def dtmf_samples(digit: str, seconds: float) -> list[float]:
    """Mixed dual-tone sine samples for DIGIT; raises on unknown keys."""
    if digit not in DTMF_FREQS:
        raise ValueError(f"not a DTMF key: {digit!r}")
    low, high = DTMF_FREQS[digit]
    count = int(SAMPLE_RATE * seconds)
    return [
        AMPLITUDE * math.sin(2 * math.pi * low * i / SAMPLE_RATE)
        + AMPLITUDE * math.sin(2 * math.pi * high * i / SAMPLE_RATE)
        for i in range(count)
    ]


def write_beeps(
    path: str | Path,
    digit: str = CONNECT_DIGIT,
    beeps: int = BEEPS,
    beep_seconds: float = BEEP_SECONDS,
    gap_seconds: float = GAP_SECONDS,
) -> str:
    """Write BEEPS touch-tone beeps with gaps to a mono WAV file."""
    frames: list[float] = []
    gap = [0.0] * int(SAMPLE_RATE * gap_seconds)
    tone = dtmf_samples(digit, beep_seconds)
    for _ in range(beeps):
        frames.extend(tone)
        frames.extend(gap)
    raw = struct.pack(f"<{len(frames)}h", *[int(s * 32767) for s in frames])
    return write_wav(path, raw, SAMPLE_RATE)
