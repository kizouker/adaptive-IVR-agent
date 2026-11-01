"""Agda talk script: open question -> examples -> yes/no -> transfer. No audio."""

from adaptive_ivr_agent.reactive import ReactiveRobot
from adaptive_ivr_agent.talk import AgdaCall, with_aliases

MISS = ("sorry", None)
HIT = ("thanks", "vab")


def make_call(respond, queue_place=None):
    return AgdaCall(
        opening="welcome, what is it?",
        examples="for example say vab",
        yesno="are you enrolled?",
        transfer="transferring you.",
        queue_line="you are placed in queue.",
        place_template="you are place 1 in queue.",
        respond=respond,
        queue_place=queue_place,
    )


def test_first_miss_gives_examples():
    answer = make_call(lambda heard: MISS).reply_to("blabla", 0)
    assert (answer.reply, answer.matched, answer.done, answer.misses) == (
        "for example say vab", None, False, 1)
    assert answer.queue_place is None


def test_second_miss_asks_yesno():
    answer = make_call(lambda heard: MISS).reply_to("blabla", 1)
    assert (answer.reply, answer.matched, answer.done, answer.misses) == (
        "are you enrolled?", None, False, 2)


def test_yesno_answer_enters_queue_with_place_number():
    answer = make_call(lambda heard: MISS, queue_place=lambda: 3).reply_to("nej", 2)
    assert answer.matched is None
    assert answer.done is True
    assert answer.queue_place == 3
    assert answer.reply == ("transferring you. you are placed in queue. "
                            "you are place 3 in queue.")


def test_keyword_hit_transfers_straight_into_queue():
    answer = make_call(lambda heard: HIT, queue_place=lambda: 2).reply_to("vab", 0)
    assert (answer.matched, answer.done, answer.queue_place) == ("vab", True, 2)
    assert answer.reply.startswith("thanks transferring you.")


def test_default_queue_place_is_a_small_number():
    answer = make_call(lambda heard: HIT).reply_to("vab", 0)
    assert 2 <= answer.queue_place <= 5


def test_real_robot_ears_drive_the_script():
    robot = ReactiveRobot({"vab": "some errand"})
    call = make_call(robot.respond, queue_place=lambda: 4)
    first = call.reply_to("blalajka", 0)
    assert (first.done, first.misses) == (False, 1)
    second = call.reply_to("vab", 1)
    assert (second.matched, second.done, second.queue_place) == ("vab", True, 4)


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
