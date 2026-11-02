"""Mini practice robot: plays fixed lines, saves each as a step (FN-REQ-IVR-006)."""
import hashlib
import json
import shutil
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

from adaptive_ivr_agent.steps import Step, StepFile

ROBOT_SPEAKER = "robot"
SAY_COMMAND = "say"
SAY_VOICE = "Alva"
CALLER_VOICE = "Oskar"
LINES_KEY = "lines"
LINE_TEXT_KEY = "text"
ENCODING = "utf-8"


def mac_say(text: str, voice: str = SAY_VOICE) -> None:
    """Speak one line with the Mac `say` command (real runs only, never tests)."""
    if shutil.which(SAY_COMMAND) is None:
        raise RuntimeError(f"{SAY_COMMAND} is not available on this machine")
    subprocess.run([SAY_COMMAND, "-v", voice, text], check=True)


def load_lines(path: str | Path) -> list[str]:
    """Load robot-side lines in order from a doorkeeper-lines JSON file."""
    raw = json.loads(Path(path).read_text(encoding=ENCODING))
    return [entry[LINE_TEXT_KEY] for entry in raw[LINES_KEY]]


def load_indexed_lines(path: str | Path) -> dict[str, str]:
    """Load doorkeeper lines keyed by id (L01, L02, ...) for scripted calls."""
    raw = json.loads(Path(path).read_text(encoding=ENCODING))
    return {entry["id"]: entry[LINE_TEXT_KEY] for entry in raw[LINES_KEY]}


def opening_cache_path(
    cache_dir: str | Path, voice: str, en_voice: str, text: str
) -> Path:
    """Path of the cached rendered opening aiff for these exact inputs.

    The filename is the sha1 of voice + en_voice + text, so identical
    openings reuse one file while any change renders fresh. Creates
    cache_dir when missing.
    """
    digest = hashlib.sha1(
        "\0".join([voice, en_voice, text]).encode(ENCODING),
        usedforsecurity=False,
    ).hexdigest()
    directory = Path(cache_dir)
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"opening-{digest}.aiff"


class PracticeRobot:
    """Plays lines through an injected speaker and records a step file."""

    def __init__(
        self,
        lines: Sequence[str],
        speak: Callable[[str], None],
        speaker: str = ROBOT_SPEAKER,
    ) -> None:
        self._lines = list(lines)
        self._speak = speak
        self._speaker = speaker

    def run(self, path: str | Path) -> list[Step]:
        steps = []
        for index, line in enumerate(self._lines):
            self._speak(line)
            steps.append(Step(index, self._speaker, line))
        StepFile.save(path, steps)
        return steps
