"""Holdmate calls by itself: BFS lessons, word table, map evidence (S2)."""
import json
import subprocess
from pathlib import Path

import pytest

from adaptive_ivr_agent.holdmate import (
    FIXED_PLACE,
    Knowledge,
    Lesson,
    build_roksolana,
    lesson_call,
    lesson_log,
    main,
    run_call,
    speak_turns,
    wintitle,
)

ROOT = Path(__file__).resolve().parent.parent
PHRASEBOOKS = ROOT / "data" / "role-phrasebooks.json"
LINES = ROOT / "data" / "doorkeeper-lines.json"

FAKE_LINES = {
    "L01": "Welcome. For English, press 0.",
    "L02": "What is your errand?",
    "L03": "Say a, b or c.",
    "L22": "Yes or no?",
    "L19": "Transferring.",
    "L09": "ID please.",
    "L12": "ID failed.",
    "L43": "Please identify first.",
    "L11": "ID ok.",
    "L30": "Served.",
    "L13": "Queued.",
    "L29": "Place 1.",
    "L41": "Please answer yes or no.",
    "L15": "Survey? Press 1.",
    "L16": "Thanks, noted.",
    "L44": "Busy welcome.",
    "L17": "English menu. Press 1, 2 or 4.",
}


def fake_respond(heard):
    """Only 'kw' is known, like one exact AF keyword."""
    if heard.strip().lower() == "kw":
        return "You said kw.", "kw"
    return "Not understood.", None


def make_lesson(candidates, max_misses=2):
    roksolana = build_roksolana(FAKE_LINES, fake_respond)
    return Lesson("test-persona", candidates, roksolana, Knowledge(), max_misses)


def test_bfs_tries_every_pair_once_in_level_order():
    lesson = make_lesson(["kw", "eh"])
    summary = lesson.run()
    pairs = [(s.misses, s.word) for s in lesson.sims]
    assert pairs == [(0, "kw"), (0, "eh"), (1, "kw"), (1, "eh"), (2, "kw"), (2, "eh")]
    assert summary["sims"] == 6
    assert summary["transfers"] == 3  # kw x3 (matched); eh reprompts at 2
    assert summary["matched"] == ["kw"]


def test_transfer_runs_to_handover():
    roksolana = build_roksolana(FAKE_LINES, fake_respond)
    result, turns, _ = run_call(roksolana, "kw", 0)
    assert result.transferred is True
    assert result.matched == "kw"
    assert result.served is True
    assert turns[0] == "YOU: kw"
    assert turns[-2] == "ROKSOLANA: Served."
    assert turns[-1] == "ROKSOLANA: Survey? Press 1. Thanks, noted."


def test_miss_stays_unserved_until_transfer():
    roksolana = build_roksolana(FAKE_LINES, fake_respond)
    result, _, _ = run_call(roksolana, "eh", 0)
    assert result.transferred is False
    assert result.served is False


def test_busy_day_uses_delay_welcome():
    calm = build_roksolana(FAKE_LINES, fake_respond)
    busy = build_roksolana(FAKE_LINES, fake_respond, busy=True)
    assert calm.opening.startswith("Welcome.")
    assert busy.opening.startswith("Busy welcome.")


def test_busy_day_opening_is_language_choice_only():
    busy = build_roksolana(FAKE_LINES, fake_respond, busy=True)
    assert busy.opening == "Busy welcome."
    assert FAKE_LINES["L02"] not in busy.opening


def test_press_zero_reaches_english_menu():
    busy = build_roksolana(FAKE_LINES, fake_respond, busy=True)
    for heard in ("0", "press 0", "For English"):
        answer = busy.reply_to(heard, 0)
        assert answer.reply == "English menu. Press 1, 2 or 4."
        assert (answer.matched, answer.done, answer.identify) == ("0", False, False)
    calm = build_roksolana(FAKE_LINES, fake_respond)
    assert calm.reply_to("0", 0).reply == "English menu. Press 1, 2 or 4."


def test_busy_path_reaches_english_menu_with_real_lines():
    from adaptive_ivr_agent.robot import load_indexed_lines

    lines = load_indexed_lines(LINES)
    busy = build_roksolana(lines, fake_respond, busy=True)
    assert "försenade" in busy.opening
    assert lines["L02"] not in busy.opening
    answer = busy.reply_to("0", 0)
    assert answer.reply == lines["L17"]
    assert answer.reply.startswith("Welcome to Arbetsförmedlingen")


def test_survey_decline_skips_accept_line():
    roksolana = build_roksolana(FAKE_LINES, fake_respond)
    joined = roksolana.after_served(0)
    skipped = roksolana.after_served(0, join=False)
    assert joined.reply == "Survey? Press 1. Thanks, noted."
    assert skipped.reply == "Survey? Press 1."
    assert joined.done is True


def test_run_call_returns_board_exchanges_with_states():
    roksolana = build_roksolana(FAKE_LINES, fake_respond)
    result, turns, exchanges = run_call(roksolana, "kw", 0)
    assert turns[0] == "YOU: kw"
    assert exchanges[0] == ("kw", result and exchanges[0].robot, True, "transfer", None, None)
    assert [e.state for e in exchanges[1:]] == ["queue"] * (FIXED_PLACE + 1) + ["survey"]
    assert exchanges[-1].caller == "1"
    assert result.exchanges == tuple(exchanges)
    missed, _, missed_ex = run_call(roksolana, "eh", 0)
    assert [(e.caller, e.state) for e in missed_ex] == [("eh", "example_words")]
    assert missed.exchanges == tuple(missed_ex)


def test_word_table_records_tries_transfers_keywords():
    lesson = make_lesson(["kw", "eh"])
    lesson.run()
    words = lesson.knowledge.words
    assert words["kw"] == {"tries": 3, "transfers": 3, "keywords": {"kw": 3}}
    assert words["eh"]["tries"] == 3
    assert words["eh"]["transfers"] == 0  # reprompt at misses 2, never transfers
    assert words["eh"]["keywords"] == {}


def test_miss_edge_points_to_next_state_without_success():
    lesson = make_lesson(["eh"], max_misses=0)
    lesson.run()
    edge = next(
        e for e in lesson.knowledge.shown.edges if e.label == "eh"
    )
    assert (edge.source, edge.target) == ("open_question", "example_words")
    assert edge.evidence.tries == 1
    assert edge.evidence.successes == 0


def test_transfer_path_marks_queue_ticks_observed():
    lesson = make_lesson(["kw"], max_misses=0)
    lesson.run()
    by_label = {(e.source, e.target, e.label): e for e in lesson.knowledge.shown.edges}
    assert by_label[("queue", "queue", "tick")].evidence.tries == FIXED_PLACE - 1
    assert by_label[("transfer", "identification", "kopplar")].evidence.successes == 1
    assert by_label[("queue", "officer", "served")].evidence.successes == 1


def test_knowledge_save_load_roundtrip_accumulates(tmp_path):
    target = tmp_path / "knowledge.json"
    first = make_lesson(["kw"], max_misses=0)
    first.run()
    first.knowledge.save(target)
    second = Knowledge.load(target)
    assert second.words["kw"]["tries"] == 1
    again = Lesson("test-persona", ["kw"], build_roksolana(FAKE_LINES, fake_respond),
                   second, max_misses=0)
    again.run()
    assert second.words["kw"]["tries"] == 2
    edge = next(e for e in second.shown.edges if e.label == "kw")
    assert edge.evidence.tries == 2
    base = [e for e in second.shown.edges
            if (e.source, e.target, e.label) == ("transfer", "identification", "kopplar")]
    assert len(base) == 1
    assert base[0].evidence.tries == 2


def test_lesson_log_appends_one_record_per_sim(tmp_path):
    target = tmp_path / "lessons.jsonl"
    lesson = make_lesson(["kw", "eh"], max_misses=0)
    lesson.run()
    for sim in lesson.sims:
        lesson_log(target, sim)
    rows = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    assert rows[0]["word"] == "kw"
    assert rows[0]["transferred"] is True
    assert rows[1]["served"] is False


def test_main_runs_one_persona_headless(tmp_path):
    knowledge = tmp_path / "k.json"
    lessons = tmp_path / "l.jsonl"
    code = main([
        "--phrasebooks", str(PHRASEBOOKS),
        "--lines", str(LINES),
        "--knowledge", str(knowledge),
        "--lessons", str(lessons),
        "--as", "ny-arbetslos",
        "--fresh",
    ])
    assert code == 0
    saved = json.loads(knowledge.read_text(encoding="utf-8"))
    assert saved["lessons"][0]["persona"] == "ny-arbetslos"
    assert saved["lessons"][0]["served"] == saved["lessons"][0]["transfers"]
    assert "skriva in mig" in saved["words"]
    assert len(lessons.read_text(encoding="utf-8").splitlines()) == saved["lessons"][0]["sims"]


def test_main_rejects_unknown_persona(tmp_path):
    code = main([
        "--phrasebooks", str(PHRASEBOOKS),
        "--lines", str(LINES),
        "--knowledge", str(tmp_path / "k.json"),
        "--lessons", str(tmp_path / "l.jsonl"),
        "--as", "atlantis",
    ])
    assert code == 1


def test_main_rejects_bad_depth(tmp_path):
    with pytest.raises(SystemExit):
        main([
            "--phrasebooks", str(PHRASEBOOKS),
            "--lines", str(LINES),
            "--knowledge", str(tmp_path / "k.json"),
            "--lessons", str(tmp_path / "l.jsonl"),
            "--depth", "9",
        ])


def test_wintitle_is_silent_without_a_tty():
    wintitle("lesson 1/8")
    assert True  # must not raise where /dev/tty is missing


def test_interrupt_mid_lesson_keeps_partial_knowledge():
    seen = []

    def exploding(heard):
        seen.append(heard)
        if len(seen) > 2:
            raise KeyboardInterrupt
        return ("nope", None)

    roksolana = build_roksolana(FAKE_LINES, exploding)
    lesson = Lesson("quit-persona", ["a", "b", "c"], roksolana, Knowledge(), 0)
    with pytest.raises(KeyboardInterrupt):
        lesson.run()
    assert len(lesson.sims) == 2
    assert set(lesson.knowledge.words) == {"a", "b"}


def test_speak_turns_layout_indents_wraps_and_spaces(capsys, monkeypatch):
    cmds = []

    class FakeProc:
        returncode = 0

        def wait(self):
            return 0

    def fake_popen(cmd, **kwargs):
        cmds.append(cmd)
        return FakeProc()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    speak_turns(["YOU: hej", "ROKSOLANA: " + "ord " * 40])
    out = capsys.readouterr().out
    assert out.startswith("    You: hej\n")
    assert "\n" + " " * 15 + "ord" in out  # hanging indent, plain width
    assert out.endswith("\n\n")
    assert cmds[0][-1] == "hej"  # speech stays unpainted
    assert all("\x1b" not in part for cmd in cmds for part in cmd)


def test_run_prints_live_line_per_sim(capsys):
    lesson = make_lesson(["kw", "eh"], max_misses=0)
    lesson.run()
    out = capsys.readouterr().out
    assert "✓ kw → transfer (open question)" in out
    assert "✗ eh → miss (open question)" in out


def test_main_prints_plan_and_lesson_progress(capsys, tmp_path):
    code = main([
        "--phrasebooks", str(PHRASEBOOKS),
        "--lines", str(LINES),
        "--knowledge", str(tmp_path / "k.json"),
        "--lessons", str(tmp_path / "l.jsonl"),
        "--as", "ny-arbetslos",
        "--depth", "0",
        "--fresh",
    ])
    assert code == 0
    out = capsys.readouterr().out
    assert "plan: 1 lessons, up to " in out
    assert "lesson 1/1: ny-arbetslos" in out
    assert "matched " in out and " words: " in out


def test_main_writes_lesson_board_with_words(tmp_path):
    board = tmp_path / "board.json"
    code = main([
        "--phrasebooks", str(PHRASEBOOKS),
        "--lines", str(LINES),
        "--knowledge", str(tmp_path / "k.json"),
        "--lessons", str(tmp_path / "l.jsonl"),
        "--as", "ny-arbetslos",
        "--depth", "0",
        "--fresh",
        "--board-out", str(board),
    ])
    assert code == 0
    raw = json.loads(board.read_text(encoding="utf-8"))
    assert raw["calls"][0]["persona"] == "ny-arbetslos"
    assert raw["calls"][0]["errand_en"] == "Register as a job seeker"
    assert set(raw["calls"][0]["turns"][0]["state_name"]) == {"sv", "en"}
    assert raw["lessons"][0]["persona"] == "ny-arbetslos"
    assert raw["words"]["skriva in mig"]["transfers"] == 1
    assert "I will connect you to an officer." in raw["calls"][0]["turns"][0]["robot_en"]
    assert raw["coverage"]["tried"] > 0
    assert raw["coverage"]["total"] >= raw["coverage"]["tried"]


def test_run_call_carries_queue_places():
    roksolana = build_roksolana(FAKE_LINES, fake_respond)
    _, _, exchanges = run_call(roksolana, "kw", 0)
    places = [e.queue_place for e in exchanges if e.state == "queue"]
    assert places and places[0] == FIXED_PLACE
    assert all(p is None or p >= 0 for p in places)


def test_lesson_call_keeps_queue_place_on_board():
    lesson = make_lesson(["kw"])
    lesson.run()
    role = {"id": "test-persona", "label": "Test", "errand": "x"}
    call = lesson_call(role, lesson, {})
    turns = [t for t in call.turns if t["state"] == "queue"]
    assert turns and turns[0]["queue_place"] == FIXED_PLACE


def test_build_roksolana_english_uses_english_lines():
    from adaptive_ivr_agent.robot import load_indexed_lines

    lines = load_indexed_lines(LINES, lang="en")
    assert lines["L17"].startswith("Welcome to Arbetsförmedlingen")
    roksolana = build_roksolana(lines, fake_respond, lang="en")
    assert roksolana.opening == lines["L17"]
    assert roksolana.opening.startswith("Welcome to Arbetsförmedlingen")
    transfer = roksolana.reply_to("kw", 0)
    assert lines["L37"] in transfer.reply  # handover in English
    assert lines["L32"] in transfer.reply  # identification in English
    assert transfer.identify is True


def test_build_roksolana_english_takes_yes_and_no():
    from adaptive_ivr_agent.robot import load_indexed_lines

    lines = load_indexed_lines(LINES, lang="en")
    roksolana = build_roksolana(lines, fake_respond, lang="en")
    assert roksolana.reply_to("yes", 2).matched == "yes"
    assert roksolana.reply_to("no", 2).matched == "no"
    assert roksolana.reply_to("ja", 2).misses == 3
    calm = build_roksolana(lines, fake_respond, lang="en")
    busy = build_roksolana(lines, fake_respond, busy=True, lang="en")
    assert busy.opening == lines["L17"] == calm.opening


def test_english_run_call_reaches_queue_and_handover_in_english():
    from adaptive_ivr_agent.robot import load_indexed_lines

    from adaptive_ivr_agent.reactive import ReactiveRobot

    lines = load_indexed_lines(LINES, lang="en")
    ears = ReactiveRobot.from_phrasebooks(PHRASEBOOKS, lang="en")
    roksolana = build_roksolana(lines, ears.respond, lang="en")
    result, _, exchanges = run_call(roksolana, "register", 0)
    assert result.transferred is True
    assert result.matched == "register"
    assert result.served is True
    robots = [e.robot for e in exchanges]
    assert any(lines["L32"] in robot for robot in robots)
    assert any(lines["L35"] in robot for robot in robots)
    assert any("You are number 3 in the queue." in robot for robot in robots)
    assert any(robot == lines["L37"] for robot in robots)  # served/handover
    assert robots[-1] == f"{lines['L15']} {lines['L16']}"  # survey tail in English


def test_main_english_lessons_produce_english_sims(tmp_path):
    knowledge = tmp_path / "k.json"
    lessons = tmp_path / "l.jsonl"
    board = tmp_path / "board.json"
    code = main([
        "--phrasebooks", str(PHRASEBOOKS),
        "--lines", str(LINES),
        "--knowledge", str(knowledge),
        "--lessons", str(lessons),
        "--as", "ny-arbetslos",
        "--depth", "0",
        "--fresh",
        "--lang", "en",
        "--board-out", str(board),
    ])
    assert code == 0
    saved = json.loads(knowledge.read_text(encoding="utf-8"))
    assert saved["lessons"][0]["persona"] == "ny-arbetslos"
    assert "register" in saved["words"]
    assert "skriva in mig" not in saved["words"]
    raw = json.loads(board.read_text(encoding="utf-8"))
    robots = [t["robot"] for t in raw["calls"][0]["turns"]]
    assert any("If you wish to register, press 1." in r for r in robots)
    assert any("You will now be placed in a queue" in r for r in robots)
    assert any("You are number" in r for r in robots)
    assert raw["words"]["register"]["transfers"] == 1
    assert any(c["token"] == "register" and c["tried"]
               for c in raw["coverage"]["cells"])


def test_main_rejects_bad_lang(tmp_path):
    with pytest.raises(SystemExit):
        main([
            "--phrasebooks", str(PHRASEBOOKS),
            "--lines", str(LINES),
            "--knowledge", str(tmp_path / "k.json"),
            "--lessons", str(tmp_path / "l.jsonl"),
            "--lang", "xx",
        ])
