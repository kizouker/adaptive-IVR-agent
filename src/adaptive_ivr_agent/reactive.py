"""Reactive practice robot: answers keywords, handles yes/no (FN-REQ-IVR-007)."""
import json
from pathlib import Path

ENCODING = "utf-8"
NOT_UNDERSTOOD = "Förlåt, jag uppfattade inte."
CONFIRM_REPLY = "Tack. Jag kopplar dig vidare."
YES_WORDS = ("ja",)
NO_WORDS = ("nej",)
NOT_UNDERSTOOD_EN = "Sorry, I did not understand."
CONFIRM_REPLY_EN = "Thank you. I will transfer you."
YES_WORDS_EN = ("yes",)
NO_WORDS_EN = ("no",)


class ReactiveRobot:
    """Replies to known keywords, asks again otherwise, takes ja/nej at confirm."""

    def __init__(self, keyword_to_errand: dict[str, str], lang: str = "sv") -> None:
        self._known = {word.lower(): errand for word, errand in keyword_to_errand.items()}
        self._lang = lang
        if lang == "en":
            self._yes_words = YES_WORDS_EN
            self._no_words = NO_WORDS_EN
            self._not_understood = NOT_UNDERSTOOD_EN
            self._confirm_reply = CONFIRM_REPLY_EN
        else:
            self._yes_words = YES_WORDS
            self._no_words = NO_WORDS
            self._not_understood = NOT_UNDERSTOOD
            self._confirm_reply = CONFIRM_REPLY

    @classmethod
    def from_phrasebooks(cls, path: str | Path, lang: str = "sv") -> "ReactiveRobot":
        """Known words are exactly the persona vocabularies; why = the errand."""
        raw = json.loads(Path(path).read_text(encoding=ENCODING))
        if lang == "en":
            vocab_key, errand_key = "vocabulary_en", "errand_en"
        else:
            vocab_key, errand_key = "vocabulary", "errand"
        known = {}
        for role in raw["roles"]:
            for word in role[vocab_key]:
                known.setdefault(word, role[errand_key])
        return cls(known, lang=lang)

    def respond(self, heard: str) -> tuple[str, str | None]:
        """Reply to one utterance; returns (reply, matched keyword or None)."""
        word = heard.strip().lower()
        if word in self._known:
            if self._lang == "en":
                return f"You said {word}. {self._confirm_reply}", word
            return f"Du sa {word}. {self._confirm_reply}", word
        return self._not_understood, None

    def confirm(self, answer: str) -> str:
        """Yes/no question step: ja/nej (yes/no in English) move on, else stays."""
        if answer.strip().lower() in self._yes_words + self._no_words:
            return self._confirm_reply
        return self._not_understood
