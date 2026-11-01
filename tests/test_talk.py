"""Agda talk script: open question -> examples -> yes/no -> transfer. No audio."""

from adaptive_ivr_agent.reactive import ReactiveRobot
from adaptive_ivr_agent.talk import AgdaCall, with_aliases

MISS = ("sorry", None)
HIT = ("thanks", "vab")


def make_call(respond):
    return AgdaCall(
        opening="welcome, what is it?",
        examples="for example say vab",
        yesno="are you enrolled?",
        transfer="transferring you.",
        respond=respond,
    )


def test_first_miss_gives_examples():
    reply, matched, done, misses = make_call(lambda heard: MISS).reply_to("blabla", 0)
    assert (reply, matched, done, misses) == ("for example say vab", None, False, 1)


def test_second_miss_asks_yesno():
    reply, matched, done, misses = make_call(lambda heard: MISS).reply_to("blabla", 1)
    assert (reply, matched, done, misses) == ("are you enrolled?", None, False, 2)


def test_yesno_answer_transfers_and_hangs_up():
    reply, matched, done, misses = make_call(lambda heard: MISS).reply_to("nej", 2)
    assert (reply, matched, done) == ("transferring you.", None, True)


def test_keyword_hit_transfers_straight_away():
    reply, matched, done, _ = make_call(lambda heard: HIT).reply_to("vab", 0)
    assert (reply, matched, done) == ("thanks transferring you.", "vab", True)


def test_real_robot_ears_drive_the_script():
    robot = ReactiveRobot({"vab": "some errand"})
    call = make_call(robot.respond)
    _, _, done, misses = call.reply_to("blalajka", 0)
    assert (done, misses) == (False, 1)
    _, matched, done, _ = call.reply_to("vab", 1)
    assert (matched, done) == ("vab", True)


def test_learned_alias_translates_before_matching():
    robot = ReactiveRobot({"vab": "some errand"})
    respond = with_aliases(robot.respond, {"vabba": "vab"})
    _, matched = respond("  Vabba ")
    assert matched == "vab"


def test_unknown_without_alias_still_misses():
    robot = ReactiveRobot({"vab": "some errand"})
    respond = with_aliases(robot.respond, {"vabba": "vab"})
    _, matched = respond("blalajka")
    assert matched is None


def test_skipped_alias_passes_through():
    robot = ReactiveRobot({"vab": "some errand"})
    respond = with_aliases(robot.respond, {"vabba": None})
    _, matched = respond("vabba")
    assert matched is None
