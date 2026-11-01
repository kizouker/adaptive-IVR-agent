"""Reactive practice robot: answers keywords, handles yes/no (FN-REQ-IVR-007)."""
import json
from pathlib import Path

ENCODING = "utf-8"
NOT_UNDERSTOOD = "Förlåt, jag uppfattade inte."
CONFIRM_REPLY = "Tack. Jag kopplar dig vidare."
YES_WORDS = ("ja",)
NO_WORDS = ("nej",)


class ReactiveRobot:
    """Replies to known keywords, asks again otherwise, takes ja/nej at confirm."""

    def __init__(self, keyword_to_errand: dict[str, str]) -> None:
        self._known = {word.lower(): errand for word, errand in keyword_to_errand.items()}

    @classmethod
    def from_phrasebooks(cls, path: str | Path) -> "ReactiveRobot":
        """Known words are exactly the persona vocabularies; why = the errand."""
        raw = json.loads(Path(path).read_text(encoding=ENCODING))
        known = {}
        for role in raw["roles"]:
            for word in role["vocabulary"]:
                known.setdefault(word, role["errand"])
        return cls(known)

    def respond(self, heard: str) -> tuple[str, str | None]:
        """Reply to one utterance; returns (reply, matched keyword or None)."""
        word = heard.strip().lower()
        if word in self._known:
            return f"Du sa {word}. {CONFIRM_REPLY}", word
        return NOT_UNDERSTOOD, None

    def confirm(self, answer: str) -> str:
        """Yes/no question step: ja and nej move on, anything else stays."""
        if answer.strip().lower() in YES_WORDS + NO_WORDS:
            return CONFIRM_REPLY
        return NOT_UNDERSTOOD
