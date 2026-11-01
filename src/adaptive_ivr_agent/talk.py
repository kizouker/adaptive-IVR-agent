"""AF Agda for talk mode: a scripted doorkeeper, dumb on purpose.

The caller (Rickard) speaks, Agda answers from the real recorded lines:
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


class AgdaReply(NamedTuple):
    """One scripted answer. identify asks for ID next; queue_place is set
    once the call reaches the queue."""

    reply: str
    matched: str | None
    done: bool
    misses: int
    identify: bool
    queue_place: int | None


class AgdaCall:
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
    ) -> None:
        self.opening = opening
        self._examples = examples
        self._yesno = yesno
        self._yesno_reprompt = yesno_reprompt
        self._transfer = transfer
        self._identify_line = identify_line
        self._identified_line = identified_line
        self._served_line = served_line
        self._queue_line = queue_line
        self._place_template = place_template
        self._respond = respond
        self._queue_place = queue_place or (lambda: random.randint(2, 5))

    def reply_to(self, heard: str, misses: int) -> AgdaReply:
        """Answer HEARD text after MISSES misses."""
        confirm, matched = self._respond(heard)
        if normalize(heard) == "(silence)":
            matched = None
        if matched is not None:
            return self._ask_for_id(f"{confirm} {self._transfer}", matched, misses)
        if misses >= 3:
            return self._ask_for_id(self._transfer, None, misses)
        if misses == 2:
            word = normalize(heard)
            if word in ("ja", "nej"):
                return self._ask_for_id(self._transfer, word, misses)
            return AgdaReply(self._yesno_reprompt, None, False, 3, False, None)
        if misses == 1:
            return AgdaReply(self._yesno, None, False, 2, False, None)
        return AgdaReply(self._examples, None, False, 1, False, None)

    def _ask_for_id(self, prefix: str, matched: str | None, misses: int) -> AgdaReply:
        """Transfer and ask for identification (verified order: ID before queue)."""
        return AgdaReply(f"{prefix} {self._identify_line}", matched, False, misses, True, None)

    def after_identified(self, misses: int) -> AgdaReply:
        """Confirm the (faked) identification and enter the simulated queue."""
        place = self._queue_place()
        line = f"{self._identified_line} {self._queue_line} {self._placed(place)}"
        return AgdaReply(line, None, False, misses, False, place)

    def _placed(self, place: int) -> str:
        # place_template is a recorded "plats 1" line; only the digit changes
        return self._place_template.replace("1", str(place), 1)

    def queue_tick(self, place: int, misses: int) -> AgdaReply:
        """One step closer: announce the next number, or hand over at 1."""
        if place <= 1:
            return AgdaReply(self._served_line, None, True, misses, False, 0)
        return AgdaReply(self._placed(place - 1), None, False, misses, False, place - 1)
