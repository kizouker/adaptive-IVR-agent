"""Mini practice robot: plays fixed lines, saves each as a step (FN-REQ-IVR-006)."""
import shutil
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

from adaptive_ivr_agent.steps import Step, StepFile

ROBOT_SPEAKER = "robot"
SAY_COMMAND = "say"


def mac_say(text: str) -> None:
    """Speak one line with the Mac `say` command (real runs only, never tests)."""
    if shutil.which(SAY_COMMAND) is None:
        raise RuntimeError(f"{SAY_COMMAND} is not available on this machine")
    subprocess.run([SAY_COMMAND, text], check=True)


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
