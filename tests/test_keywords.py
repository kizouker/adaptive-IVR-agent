"""Keyword table (FN-REQ-IVR-004). Test-first: implementation follows."""
import pytest

from tests.test_data import (
    KEYWORD_COMPENSATION,
    KEYWORD_TABLE,
    OUTCOME_COMPENSATION,
    UNKNOWN_WORD,
)
from adaptive_ivr_agent.keywords import KeywordTable


@pytest.fixture
def table():
    t = KeywordTable()
    for keyword, outcome in KEYWORD_TABLE.items():
        t.add(keyword, outcome)
    return t


def test_keyword_to_outcome(table):
    assert table.outcome_for(KEYWORD_COMPENSATION) == OUTCOME_COMPENSATION


def test_outcome_to_words(table):
    assert table.words_for(OUTCOME_COMPENSATION) == KEYWORD_COMPENSATION


def test_unknown_keyword_raises(table):
    with pytest.raises(KeyError):
        table.outcome_for(UNKNOWN_WORD)
