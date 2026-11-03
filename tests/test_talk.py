"""Agda talk script: open question -> examples -> yes/no -> transfer. No audio."""

from adaptive_ivr_agent.reactive import ReactiveRobot
from adaptive_ivr_agent.talk import AgdaCall, with_aliases

MISS = ("sorry", None)
HIT = ("thanks", "vab")


def make_call(respond, queue_place=None, english_menu=""):
    return AgdaCall(
        english_menu=english_menu,
        opening="welcome, what is it?",
        examples="for example say vab",
        yesno="are you enrolled?",
        yesno_reprompt="please answer yes or no.",
        transfer="transferring you.",
        identify_line="identify with bankid or freja.",
        identified_line="identification worked.",
        failed_line="identification failed.",
        served_line="connecting you now.",
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
    assert answer.matched == "nej"
    assert (answer.done, answer.identify, answer.queue_place) == (False, True, None)
    assert answer.reply == "transferring you. identify with bankid or freja."


def test_yesno_sentence_gets_one_reprompt():
    answer = make_call(lambda heard: MISS).reply_to("jag vet inte riktigt", 2)
    assert (answer.reply, answer.matched, answer.done, answer.misses) == (
        "please answer yes or no.", None, False, 3)
    assert (answer.identify, answer.queue_place) == (False, None)


def test_silence_never_matches_and_counts_as_miss():
    answer = make_call(lambda heard: HIT).reply_to("(silence)", 0)
    assert (answer.reply, answer.matched, answer.misses) == (
        "for example say vab", None, 1)


def test_silence_at_yesno_gets_reprompt():
    answer = make_call(lambda heard: HIT).reply_to("(silence)", 2)
    assert (answer.reply, answer.misses) == ("please answer yes or no.", 3)


def test_third_miss_transfers():
    answer = make_call(lambda heard: MISS).reply_to("fortfarande oklart", 3)
    assert (answer.done, answer.identify, answer.misses) == (False, True, 3)


def test_keyword_hit_transfers_and_asks_for_id():
    answer = make_call(lambda heard: HIT).reply_to("vab", 0)
    assert (answer.matched, answer.done, answer.identify) == ("vab", False, True)
    assert answer.reply.startswith("thanks transferring you.")


def test_after_identified_enters_queue_with_place_number():
    call = make_call(lambda heard: MISS, queue_place=lambda: 3)
    answer = call.after_identified(2)
    assert (answer.done, answer.identify, answer.queue_place) == (False, False, 3)
    assert answer.reply == ("identification worked. you are placed in queue. "
                            "you are place 3 in queue.")


def test_failed_identification_still_queues_with_failed_line():
    call = make_call(lambda heard: MISS, queue_place=lambda: 3)
    answer = call.after_identified(2, ok=False)
    assert (answer.done, answer.identify, answer.queue_place) == (False, False, 3)
    assert answer.reply == ("identification failed. you are placed in queue. "
                            "you are place 3 in queue.")


def test_queue_tick_counts_down_and_serves_at_one():
    call = make_call(lambda heard: MISS)
    step = call.queue_tick(3, 1)
    assert (step.reply, step.done, step.queue_place) == ("you are place 2 in queue.", False, 2)
    last = call.queue_tick(1, 1)
    assert (last.reply, last.done, last.queue_place) == ("connecting you now.", True, 0)


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
    assert (third.done, third.queue_place) == (False, 4)
    fourth = call.queue_tick(third.queue_place, third.misses)
    assert (fourth.done, fourth.queue_place) == (False, 3)


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


def test_zero_without_english_menu_stays_a_miss():
    answer = make_call(lambda heard: MISS).reply_to("0", 0)
    assert (answer.reply, answer.matched, answer.misses) == (
        "for example say vab", None, 1)


def test_zero_with_english_menu_answers_the_menu():
    call = make_call(lambda heard: MISS, english_menu="english menu here.")
    answer = call.reply_to("0", 1)
    assert (answer.reply, answer.matched, answer.misses) == (
        "english menu here.", "0", 1)
    assert (answer.done, answer.identify, answer.queue_place) == (
        False, False, None)
