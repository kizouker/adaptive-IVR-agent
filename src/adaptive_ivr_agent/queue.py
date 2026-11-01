"""Queue number parsing (FN-REQ-IVR-011)."""
import re

PATTERNS = (
    re.compile(r"Det är (\d+) samtal före dig", re.IGNORECASE),
    re.compile(r"anropare nummer (\d+)", re.IGNORECASE),
    re.compile(r"Din plats är: (\d+)", re.IGNORECASE),
    re.compile(r"Du har plats (\d+) i kön", re.IGNORECASE),
    re.compile(r"You are number (\d+) in the", re.IGNORECASE),
)


def find_place(text: str) -> int | None:
    """Return the queue place in a transcript line, or None if absent."""
    for pattern in PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None


class QueueWatch:
    """Latest known queue place from transcript lines (FN-REQ-IVR-013).

    The caller reads .place instead of listening; .history shows the
    countdown. Display on the board is future work.
    """

    def __init__(self) -> None:
        self.place: int | None = None
        self.history: list[int] = []

    def update(self, text: str) -> int | None:
        """Fold one line in; return the latest known place."""
        found = find_place(text)
        if found is not None and found != self.place:
            self.place = found
            self.history.append(found)
        return self.place
