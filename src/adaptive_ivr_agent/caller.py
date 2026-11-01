"""Caller: Holdmate picks words from the keyword table (FN-REQ-IVR-008)."""
from adaptive_ivr_agent.keywords import KeywordTable


class Caller:
    """Says the table's words for a wanted outcome."""

    def __init__(self, table: KeywordTable) -> None:
        self._table = table

    def speak_for(self, outcome: str) -> str:
        """Return the word to say for a wanted outcome.

        Raises KeyError for outcomes the table never learned — the caller
        may only speak confirmed words, never guesses.
        """
        return self._table.words_for(outcome)
