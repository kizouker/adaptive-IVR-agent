"""English-language calls (ticket #173, v0.4.0): en keywords, en confirm."""
from pathlib import Path

from adaptive_ivr_agent.reactive import (
    CONFIRM_REPLY,
    CONFIRM_REPLY_EN,
    NOT_UNDERSTOOD,
    NOT_UNDERSTOOD_EN,
    ReactiveRobot,
)
from adaptive_ivr_agent.talk import RoksolanaCall

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BOOKS = DATA_DIR / "role-phrasebooks.json"
EN_WORD = "register"
EN_ERRAND = "Register as a job seeker"


def test_english_keyword_hit_matches_and_replies_english():
    robot = ReactiveRobot.from_phrasebooks(BOOKS, lang="en")
    reply, matched = robot.respond(EN_WORD)
    assert matched == EN_WORD
    assert EN_WORD in reply
    assert CONFIRM_REPLY_EN in reply
    assert robot._known[EN_WORD] == EN_ERRAND


def test_english_miss_is_not_understood_in_english():
    robot = ReactiveRobot.from_phrasebooks(BOOKS, lang="en")
    assert robot.respond("blalajka") == (NOT_UNDERSTOOD_EN, None)


def test_english_confirm_takes_yes_and_no():
    robot = ReactiveRobot.from_phrasebooks(BOOKS, lang="en")
    assert robot.confirm("yes") == CONFIRM_REPLY_EN
    assert robot.confirm("no") == CONFIRM_REPLY_EN
    assert robot.confirm("ja") == NOT_UNDERSTOOD_EN
    assert robot.confirm("kanske") == NOT_UNDERSTOOD_EN


def test_swedish_default_still_ja_nej():
    robot = ReactiveRobot.from_phrasebooks(BOOKS)
    assert robot.confirm("ja") == CONFIRM_REPLY
    assert robot.confirm("nej") == CONFIRM_REPLY
    assert robot.confirm("yes") == NOT_UNDERSTOOD
    reply, matched = robot.respond("aktivitetsrapport")
    assert matched == "aktivitetsrapport"
    assert CONFIRM_REPLY in reply


def _make_call(**kwargs):
    args = dict(
        opening="welcome, what is it?",
        examples="for example say vab",
        yesno="are you enrolled?",
        yesno_reprompt="please answer yes or no.",
        transfer="transferring you.",
        identify_line="identify with bankid or freja.",
        identified_line="identification worked.",
        served_line="connecting you now.",
        queue_line="you are placed in queue.",
        place_template="you are place 1 in queue.",
        respond=lambda heard: ("sorry", None),
    )
    args.update(kwargs)
    return RoksolanaCall(**args)


def test_roksolana_call_default_yesno_is_swedish():
    call = _make_call()
    assert call.reply_to("nej", 2).matched == "nej"
    assert call.reply_to("no", 2).misses == 3


def test_roksolana_call_english_yesno_pair_confirms():
    call = _make_call(yesno_words=("yes", "no"))
    assert call.reply_to("yes", 2).matched == "yes"
    assert call.reply_to("no", 2).matched == "no"
    assert call.reply_to("nej", 2).misses == 3
