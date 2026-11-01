"""AF Agda for talk mode: a scripted doorkeeper, dumb on purpose.

The caller (Rickard) speaks, Agda answers from the real recorded lines:
welcome + open question, then examples on a miss, then a yes/no question,
then transfer. A keyword hit at any point transfers straight away.
"""

from collections.abc import Callable


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


class AgdaCall:
    """One scripted call. Stateless across rounds: the miss count travels
    with the caller (the shell keeps it between recordings)."""

    def __init__(
        self,
        opening: str,
        examples: str,
        yesno: str,
        transfer: str,
        respond: Callable[[str], tuple[str, str | None]],
    ) -> None:
        self.opening = opening
        self._examples = examples
        self._yesno = yesno
        self._transfer = transfer
        self._respond = respond

    def reply_to(self, heard: str, misses: int) -> tuple[str, str | None, bool, int]:
        """Answer HEARD text after MISSES misses. Returns (reply, matched,
        done, new_misses)."""
        confirm, matched = self._respond(heard)
        if matched is not None:
            return f"{confirm} {self._transfer}", matched, True, misses
        if misses >= 2:
            return self._transfer, None, True, misses
        if misses == 1:
            return self._yesno, None, False, 2
        return self._examples, None, False, 1
