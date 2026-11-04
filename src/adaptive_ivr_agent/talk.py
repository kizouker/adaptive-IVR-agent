"""AF Roksolana for talk mode: a scripted doorkeeper, dumb on purpose.

The caller (Rickard) speaks, Roksolana answers from the real recorded lines:
welcome + open question, then examples on a miss, then a yes/no question,
then transfer into a simulated queue with a place number. A keyword hit
at any point transfers straight away.
"""

import random
from collections.abc import Callable
from typing import NamedTuple


def normalize(heard: str) -> str:
    """Same normalization as the robot ears: strip + lowercase."""
    return heard.strip().lower()


def with_aliases(
    respond: Callable[[str], tuple[str, str | None]],
    aliases: dict[str, str | None],
) -> Callable[[str], tuple[str, str | None]]:
    """Wrap RESPOND so learned ALIASES (utterance -> keyword) translate first.

    Falsy values (reviewed but skipped) pass through untouched.
    """
    clean = {normalize(k): v for k, v in aliases.items() if v}
    return lambda heard: respond(clean.get(normalize(heard), heard))


PRESS_ZERO_FORMS = ("0", "press 0", "for english", "english")


class RoksolanaReply(NamedTuple):
    """One scripted answer. identify asks for ID next; queue_place is set
    once the call reaches the queue."""

    reply: str
    matched: str | None
    done: bool
    misses: int
    identify: bool
    queue_place: int | None


class RoksolanaCall:
    """One scripted call. Stateless across rounds: the miss count travels
    with the caller (the shell keeps it between recordings)."""

    def __init__(
        self,
        opening: str,
        examples: str,
        yesno: str,
        yesno_reprompt: str,
        transfer: str,
        identify_line: str,
        identified_line: str,
        served_line: str,
        queue_line: str,
        place_template: str,
        respond: Callable[[str], tuple[str, str | None]],
        queue_place: Callable[[], int] | None = None,
        failed_line: str = "",
        survey_line: str = "",
        survey_done: str = "",
        english_menu: str = "",
        yesno_words: tuple[str, str] = ("ja", "nej"),
    ) -> None:
        self.opening = opening
        self._examples = examples
        self._yesno = yesno
        self._yesno_reprompt = yesno_reprompt
        self._transfer = transfer
        self._identify_line = identify_line
        self._identified_line = identified_line
        self._failed_line = failed_line
        self._survey_line = survey_line
        self._survey_done = survey_done
        self._english_menu = english_menu
        self._served_line = served_line
        self._queue_line = queue_line
        self._place_template = place_template
        self._respond = respond
        self._yesno_words = tuple(w.lower() for w in yesno_words)
        self._queue_place = queue_place or (lambda: random.randint(2, 5))

    def reply_to(self, heard: str, misses: int) -> RoksolanaReply:
        """Answer HEARD text after MISSES misses."""
        if self._english_menu and normalize(heard) in PRESS_ZERO_FORMS:
            return RoksolanaReply(self._english_menu, "0", False, misses, False, None)
        confirm, matched = self._respond(heard)
        if normalize(heard) == "(silence)":
            matched = None
        if matched is not None:
            return self._ask_for_id(f"{confirm} {self._transfer}", matched, misses)
        if misses >= 3:
            return self._ask_for_id(self._transfer, None, misses)
        if misses == 2:
            word = normalize(heard)
            if word in self._yesno_words:
                return self._ask_for_id(self._transfer, word, misses)
            return RoksolanaReply(self._yesno_reprompt, None, False, 3, False, None)
        if misses == 1:
            return RoksolanaReply(self._yesno, None, False, 2, False, None)
        return RoksolanaReply(self._examples, None, False, 1, False, None)

    def _ask_for_id(self, prefix: str, matched: str | None, misses: int) -> RoksolanaReply:
        """Transfer and ask for identification (verified order: ID before queue)."""
        return RoksolanaReply(f"{prefix} {self._identify_line}", matched, False, misses, True, None)

    def after_identified(self, misses: int, ok: bool = True) -> RoksolanaReply:
        """Confirm the identification (or its failure) and enter the queue."""
        place = self._queue_place()
        if ok:
            first = self._identified_line
        else:
            first = self._failed_line or self._identified_line
        line = f"{first} {self._queue_line} {self._placed(place)}"
        return RoksolanaReply(line, None, False, misses, False, place)

    def _placed(self, place: int) -> str:
        # place_template is a recorded "plats 1" line; only the digit changes
        return self._place_template.replace("1", str(place), 1)

    def queue_tick(self, place: int, misses: int) -> RoksolanaReply:
        """One step closer: announce the next number, or hand over at 1."""
        if place <= 1:
            return RoksolanaReply(self._served_line, None, True, misses, False, 0)
        return RoksolanaReply(self._placed(place - 1), None, False, misses, False, place - 1)

    def after_served(self, misses: int, join: bool = True) -> RoksolanaReply:
        """Survey offer after handover; joining plays the accept line."""
        if join and self._survey_done:
            line = f"{self._survey_line} {self._survey_done}"
        else:
            line = self._survey_line
        return RoksolanaReply(line, None, True, misses, False, 0)
