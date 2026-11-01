"""Reactive robot (FN-REQ-IVR-007): keywords move on, ja/nej at confirm."""
from pathlib import Path

from adaptive_ivr_agent.reactive import CONFIRM_REPLY, NOT_UNDERSTOOD, ReactiveRobot

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KNOWN_WORD = "aktivitetsrapport"
UNKNOWN_WORD = "blalajka"


def test_known_word_moves_on():
    robot = ReactiveRobot.from_phrasebooks(DATA_DIR / "role-phrasebooks.json")
    reply, matched = robot.respond(KNOWN_WORD)
    assert matched == KNOWN_WORD
    assert KNOWN_WORD in reply


def test_unknown_word_is_not_understood():
    robot = ReactiveRobot.from_phrasebooks(DATA_DIR / "role-phrasebooks.json")
    reply, matched = robot.respond(UNKNOWN_WORD)
    assert (reply, matched) == (NOT_UNDERSTOOD, None)


def test_ja_and_nej_move_on_at_confirm():
    robot = ReactiveRobot({KNOWN_WORD: "some errand"})
    assert robot.confirm("ja") == CONFIRM_REPLY
    assert robot.confirm("nej") == CONFIRM_REPLY
    assert robot.confirm("kanske") == NOT_UNDERSTOOD


def test_respond_ignores_case_and_surrounding_space():
    robot = ReactiveRobot.from_phrasebooks(DATA_DIR / "role-phrasebooks.json")
    reply, matched = robot.respond("  AKTIVITETSRAPPORT  ")
    assert matched == KNOWN_WORD
    assert KNOWN_WORD in reply


def test_respond_match_confirms_and_moves_on():
    robot = ReactiveRobot.from_phrasebooks(DATA_DIR / "role-phrasebooks.json")
    reply, _ = robot.respond(KNOWN_WORD)
    assert CONFIRM_REPLY in reply


def test_respond_empty_and_partial_words_are_not_understood():
    robot = ReactiveRobot.from_phrasebooks(DATA_DIR / "role-phrasebooks.json")
    for heard in ("", "   ", "aktivitetsrappo", "ja"):
        assert robot.respond(heard) == (NOT_UNDERSTOOD, None)


def test_constructor_keywords_match_case_insensitively():
    robot = ReactiveRobot({"Ersättning": "compensation"})
    reply, matched = robot.respond("ersättning")
    assert matched == "ersättning"
    assert CONFIRM_REPLY in reply


def test_confirm_ignores_case_and_surrounding_space():
    robot = ReactiveRobot({KNOWN_WORD: "some errand"})
    assert robot.confirm(" Ja ") == CONFIRM_REPLY
    assert robot.confirm("NEJ") == CONFIRM_REPLY
    assert robot.confirm("") == NOT_UNDERSTOOD
    assert robot.confirm("jaja") == NOT_UNDERSTOOD


def test_from_phrasebooks_first_role_wins_shared_word(tmp_path):
    book = tmp_path / "books.json"
    book.write_text(
        '{"roles": ['
        '{"id": "a", "errand": "first errand", "vocabulary": ["hej"]}, '
        '{"id": "b", "errand": "second errand", "vocabulary": ["hej", "då"]}'
        "]}",
        encoding="utf-8",
    )
    robot = ReactiveRobot.from_phrasebooks(book)
    assert robot._known["hej"] == "first errand"
    assert robot._known["då"] == "second errand"
