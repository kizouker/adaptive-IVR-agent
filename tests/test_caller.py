"""Caller picks table words for wanted outcomes (FN-REQ-IVR-008)."""
import pytest

from tests.test_data import KEYWORD_TABLE, OUTCOME_COMPENSATION
from adaptive_ivr_agent.caller import Caller
from adaptive_ivr_agent.keywords import KeywordTable


def make_caller():
    table = KeywordTable()
    for keyword, outcome in KEYWORD_TABLE.items():
        table.add(keyword, outcome)
    return Caller(table)


def test_table_word_for_wanted_outcome():
    assert make_caller().speak_for(OUTCOME_COMPENSATION) == "ersättning"


def test_unknown_outcome_raises():
    with pytest.raises(KeyError):
        make_caller().speak_for("moon landing")
