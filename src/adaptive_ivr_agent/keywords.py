"""Keyword table: keyword <-> outcome in both directions (FN-REQ-IVR-004)."""


class KeywordTable:
    """Two-way map between spoken keywords and what they get done."""

    def __init__(self) -> None:
        self._by_keyword: dict[str, str] = {}
        self._by_outcome: dict[str, str] = {}

    def add(self, keyword: str, outcome: str) -> None:
        self._by_keyword[keyword] = outcome
        self._by_outcome[outcome] = keyword

    def outcome_for(self, keyword: str) -> str:
        return self._by_keyword[keyword]

    def words_for(self, outcome: str) -> str:
        return self._by_outcome[outcome]
