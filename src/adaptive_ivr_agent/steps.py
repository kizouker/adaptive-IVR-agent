"""Step files: one saved exchange per step of a call (FN-REQ-IVR-003)."""
import json
from dataclasses import asdict, dataclass
from pathlib import Path

ENCODING = "utf-8"


@dataclass
class Step:
    index: int
    speaker: str
    text: str


class StepFile:
    """Save and load runs as JSON step files."""

    @staticmethod
    def save(path: str | Path, steps: list[Step]) -> Path:
        target = Path(path)
        target.write_text(
            json.dumps([asdict(s) for s in steps], ensure_ascii=False, indent=2),
            encoding=ENCODING,
        )
        return target

    @staticmethod
    def load(path: str | Path) -> list[Step]:
        raw = json.loads(Path(path).read_text(encoding=ENCODING))
        return [Step(**item) for item in raw]
