"""Chiptune music synthesis for the Holdmate menu launcher (split from menu.py)."""
from __future__ import annotations

import math
import struct
import tempfile
from pathlib import Path

from adaptive_ivr_agent.wavio import write_wav

ROOT = Path(__file__).resolve().parent.parent.parent

MUSIC_OVERRIDE = ROOT / "data" / "audio" / "menu-theme.wav"
MUSIC_RENDERED = Path(tempfile.gettempdir()) / "holdmate-menu-music.wav"
MUSIC_RATE = 16000
MUSIC_BEAT_S = 0.21
MUSIC_REPEATS = 8

# Original Giana-style chiptune loop: (note, beats). Not the real theme.
MUSIC_LEAD = [
    ("C5", 0.5), ("E5", 0.5), ("G5", 0.5), ("C6", 0.5),
    ("B5", 0.5), ("G5", 0.5), ("A5", 0.5), ("G5", 0.5),
    ("E5", 0.5), ("G5", 0.5), ("A5", 0.5), ("G5", 0.5),
    ("E5", 0.5), ("D5", 0.5), ("C5", 0.5), ("D5", 0.5),
    ("E5", 0.5), ("G5", 0.5), ("A5", 0.5), ("C6", 0.5),
    ("D6", 0.5), ("C6", 0.5), ("A5", 0.5), ("G5", 0.5),
    ("A5", 0.5), ("G5", 0.5), ("E5", 0.5), ("D5", 0.5),
    ("C5", 1.0), (None, 0.5), ("G4", 0.5),
]
MUSIC_BASS = [
    ("C3", 1.0), ("G2", 1.0), ("A2", 1.0), ("F2", 1.0),
    ("G2", 1.0), ("C3", 1.0), ("F2", 1.0), ("G2", 1.0),
    ("C3", 1.0), ("G2", 1.0), ("A2", 1.0), ("F2", 1.0),
    ("G2", 1.0), ("G2", 1.0), ("C3", 1.0), ("C3", 1.0),
]

_NOTE_BASE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9,
              "B": 11}


def _note_freq(name: str) -> float:
    midi = 12 + 12 * int(name[1:]) + _NOTE_BASE[name[0]]
    return 440.0 * 2 ** ((midi - 69) / 12)


def _squareish(freq: float, i: int) -> float:
    t = 2 * math.pi * freq * i / MUSIC_RATE
    return (math.sin(t) + 0.3 * math.sin(3 * t)
            + 0.12 * math.sin(5 * t))


def _sine(freq: float, i: int) -> float:
    return math.sin(2 * math.pi * freq * i / MUSIC_RATE)


def _render_voice(notes, level: float, wave_fn) -> list[float]:
    samples: list[float] = []
    for name, beats in notes:
        count = int(MUSIC_RATE * MUSIC_BEAT_S * beats)
        if name is None:
            samples.extend([0.0] * count)
            continue
        freq = _note_freq(name)
        edge = min(count, 160)
        for i in range(count):
            env = min(1.0, i / edge, (count - i) / edge)
            samples.append(level * env * wave_fn(freq, i))
    return samples


def render_menu_music(path: str | Path = MUSIC_RENDERED) -> str:
    """Render the original chiptune loop to a wav file."""
    lead = _render_voice(MUSIC_LEAD, 0.30, _squareish)
    bass = _render_voice(MUSIC_BASS, 0.22, _sine)
    if len(bass) < len(lead):
        bass += [0.0] * (len(lead) - len(bass))
    else:
        lead += [0.0] * (len(bass) - len(lead))
    loop = [a + b for a, b in zip(lead, bass)]
    data = loop * MUSIC_REPEATS
    peak = max([1.0] + [abs(v) for v in data])
    raw = struct.pack(
        f"<{len(data)}h",
        *(int(max(-1.0, min(1.0, v / peak)) * 30000) for v in data))
    return write_wav(path, raw, MUSIC_RATE)


def menu_music_path() -> str:
    """User override wins, else the rendered loop (rendered once)."""
    if MUSIC_OVERRIDE.exists():
        return str(MUSIC_OVERRIDE)
    if not MUSIC_RENDERED.exists():
        render_menu_music(MUSIC_RENDERED)
    return str(MUSIC_RENDERED)
