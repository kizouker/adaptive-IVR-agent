"""Teach Roksolana words it missed. Review is injected so tests stay quiet.

Flow: talk mode appends misses to data/talk-misses.jsonl, this module picks
the ones worth asking about, and the review answers are saved to
data/learned-words.json as {utterance: keyword} (None = seen, no mapping).
"""

import json
from collections.abc import Callable
from pathlib import Path

from adaptive_ivr_agent.talk import normalize

ENCODING = "utf-8"


def read_misses(path: str | Path) -> list[dict]:
    """Read miss records (one JSON object per line). Missing file = no misses."""
    if not Path(path).exists():
        return []
    records = []
    for line in Path(path).read_text(encoding=ENCODING).splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def pending_misses(records: list[dict], learned: dict[str, str | None]) -> list[str]:
    """Heard texts worth asking about: non-empty, not yet reviewed, first-seen order."""
    pending = []
    seen = set()
    for record in records:
        heard = normalize(record.get("heard", ""))
        if not heard or heard in learned or heard in seen:
            continue
        seen.add(heard)
        pending.append(heard)
    return pending


def known_words(path: str | Path) -> set[str]:
    """Valid keywords: every persona vocabulary, lowercased."""
    raw = json.loads(Path(path).read_text(encoding=ENCODING))
    return {word.lower() for role in raw["roles"] for word in role["vocabulary"]}


def review(
    pending: list[str],
    ask: Callable[[str], str | None],
) -> dict[str, str | None]:
    """Ask about each pending utterance. ASK returns a keyword, "" to skip,
    or None to quit. Returns the new {utterance: keyword-or-None} mappings."""
    new = {}
    for heard in pending:
        answer = ask(heard)
        if answer is None:
            break
        new[heard] = answer.strip().lower() or None
    return new
