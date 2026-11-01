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
