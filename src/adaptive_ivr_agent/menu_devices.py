"""Audio device helpers for the Holdmate menu launcher (split from menu.py)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
VOLUME_FILE = ROOT / ".talk-volume"
INPUT_FILE = ROOT / ".talk-input"


def clamp_volume(value: float) -> float:
    return round(min(4.0, max(0.1, value)), 1)


def read_volume() -> float:
    try:
        value = float(VOLUME_FILE.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return 0.7
    if 0.1 <= value <= 4.0:
        return value
    return 0.7


def _system_devices(kind: str) -> list[str]:
    exe = shutil.which("SwitchAudioSource")
    if not exe:
        return []
    proc = subprocess.run([exe, "-a", "-t", kind], capture_output=True,
                          text=True, timeout=10)
    return [line for line in (line.strip() for line in proc.stdout.splitlines())
            if line]


def system_outputs() -> list[str]:
    return _system_devices("output")


def system_inputs() -> list[str]:
    return _system_devices("input")


def read_input_name() -> str:
    try:
        return INPUT_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
