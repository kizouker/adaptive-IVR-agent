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
        identify_line="identify with bankid or freja.",
        identified_line="identification worked.",
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


def test_yesno_answer_transfers_and_asks_for_id():
    answer = make_call(lambda heard: MISS).reply_to("nej", 2)
    assert answer.matched is None
    assert (answer.done, answer.identify, answer.queue_place) == (False, True, None)
    assert answer.reply == "transferring you. identify with bankid or freja."


def test_keyword_hit_transfers_and_asks_for_id():
    answer = make_call(lambda heard: HIT).reply_to("vab", 0)
    assert (answer.matched, answer.done, answer.identify) == ("vab", False, True)
    assert answer.reply.startswith("thanks transferring you.")


def test_after_identified_enters_queue_with_place_number():
    call = make_call(lambda heard: MISS, queue_place=lambda: 3)
    answer = call.after_identified(2)
    assert (answer.done, answer.identify, answer.queue_place) == (True, False, 3)
    assert answer.reply == ("identification worked. you are placed in queue. "
                            "you are place 3 in queue.")


def test_default_queue_place_is_a_small_number():
    answer = make_call(lambda heard: HIT).after_identified(0)
    assert 2 <= answer.queue_place <= 5


def test_real_robot_ears_drive_the_script():
    robot = ReactiveRobot({"vab": "some errand"})
    call = make_call(robot.respond, queue_place=lambda: 4)
    first = call.reply_to("blalajka", 0)
    assert (first.done, first.misses) == (False, 1)
    second = call.reply_to("vab", 1)
    assert (second.matched, second.done, second.identify) == ("vab", False, True)
    third = call.after_identified(second.misses)
    assert (third.done, third.queue_place) == (True, 4)


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
