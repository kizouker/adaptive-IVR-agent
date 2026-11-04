"""Spark fallback in the talk loop: one rescue call on word-step miss (#205)."""
import json
from pathlib import Path

from adaptive_ivr_agent.holdmate import (
    Knowledge,
    Lesson,
    build_roksolana,
    lesson_call,
    main,
    run_call,
)
from adaptive_ivr_agent.intent import SparkFallback, maybe_spark_normalizer
from adaptive_ivr_agent.live_view import LiveCall
from adaptive_ivr_agent.talk import RoksolanaCall

ROOT = Path(__file__).resolve().parent.parent
PHRASEBOOKS = ROOT / "data" / "role-phrasebooks.json"
LINES = ROOT / "data" / "doorkeeper-lines.json"
VOCAB = ["handläggare", "vab"]

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


def exact_respond(heard):
    clean = heard.strip().lower()
    if clean in VOCAB:
        return f"You said {clean}.", clean
    return "Not understood.", None


class Scripted:
    """Fake normalizer: scripted verdict, counts calls."""

    def __init__(self, keyword=None, conf=0.9):
        self.keyword = keyword
        self.conf = conf
        self.calls = 0

    def map(self, heard, vocab):
        self.calls += 1
        return self.keyword, self.conf


def make_call(respond):
    return RoksolanaCall(
        opening="welcome, what is it?",
        examples="for example say vab",
        yesno="are you enrolled?",
        yesno_reprompt="please answer yes or no.",
        transfer="transferring you.",
        identify_line="identify please.",
        identified_line="identification worked.",
        failed_line="identification failed.",
        served_line="connecting you now.",
        queue_line="you are placed in queue.",
        place_template="you are place 1 in queue.",
        respond=respond,
    )


def test_exact_hit_never_consults_spark():
    spark = Scripted("vab")
    fallback = SparkFallback(exact_respond, spark, VOCAB)
    assert fallback.respond("vab") == ("You said vab.", "vab")
    assert spark.calls == 0
    assert fallback.last is None


def test_miss_triggers_exactly_one_spark_call_and_rescues():
    spark = Scripted("vab", 0.85)
    fallback = SparkFallback(exact_respond, spark, VOCAB)
    reply, matched = fallback.respond("vabb?")
    assert matched == "vab"
    assert "vab" in reply
    assert spark.calls == 1
    assert fallback.last == {"word": "vab", "confidence": 0.85}


def test_spark_abstain_keeps_miss():
    spark = Scripted(None)
    fallback = SparkFallback(exact_respond, spark, VOCAB)
    assert fallback.respond("blabla") == ("Not understood.", None)
    assert spark.calls == 1
    assert fallback.last is None


def test_spark_error_never_raises():
    class Down:
        def map(self, heard, vocab):
            raise TimeoutError("slow")

    fallback = SparkFallback(exact_respond, Down(), VOCAB)
    assert fallback.respond("blabla") == ("Not understood.", None)
    assert fallback.last is None


def test_maybe_spark_normalizer_keyless_returns_none(monkeypatch):
    monkeypatch.delenv("SPARK_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    assert maybe_spark_normalizer(True) is None


def test_maybe_spark_normalizer_disabled_returns_none(monkeypatch):
    monkeypatch.setenv("MODEL_API_KEY", "k")
    assert maybe_spark_normalizer(False) is None


def test_roksolana_call_transfers_on_spark_rescue():
    fallback = SparkFallback(exact_respond, Scripted("vab", 0.92), VOCAB)
    answer = make_call(fallback.respond).reply_to("vabb?", 0)
    assert answer.matched == "vab"
    assert answer.identify is True
    assert fallback.last == {"word": "vab", "confidence": 0.92}


def test_roksolana_call_miss_without_fallback_stays_miss():
    answer = make_call(exact_respond).reply_to("vabb?", 0)
    assert (answer.matched, answer.misses) == (None, 1)


def test_live_call_carries_spark_badge():
    call = LiveCall()
    call.add_turn("vabb?", "transferring.", True, "transfer",
                  spark={"word": "vab", "confidence": 0.85})
    turn = call.snapshot()["turns"][0]
    assert turn["spark"] == {"word": "vab", "confidence": 0.85}


def test_live_call_without_spark_has_no_badge():
    call = LiveCall()
    call.add_turn("blabla", "say a, b or c.", False, "example_words")
    assert "spark" not in call.snapshot()["turns"][0]


def fake_holdmate_respond(heard):
    if heard.strip().lower() == "kw":
        return "You said kw.", "kw"
    return "Not understood.", None


def test_run_call_attaches_spark_to_exchange():
    fallback = SparkFallback(fake_holdmate_respond, Scripted("kw", 0.88), ["kw"])
    roksolana = build_roksolana(FAKE_LINES, fallback.respond)
    result, _, exchanges = run_call(roksolana, "k w?", 0, fallback)
    assert result.matched == "kw"
    assert result.transferred is True
    assert exchanges[0].spark == {"word": "kw", "confidence": 0.88}


def test_run_call_keyless_has_no_spark():
    roksolana = build_roksolana(FAKE_LINES, fake_holdmate_respond)
    result, _, exchanges = run_call(roksolana, "eh", 0)
    assert result.matched is None
    assert exchanges[0].spark is None


def test_lesson_rescue_lands_on_board_call():
    fallback = SparkFallback(fake_holdmate_respond, Scripted("kw", 0.88), ["kw"])
    roksolana = build_roksolana(FAKE_LINES, fallback.respond)
    lesson = Lesson("test-persona", ["kw", "eh"], roksolana, Knowledge(), 0,
                    spark_fallback=fallback)
    lesson.run()
    assert lesson.sims[1].matched == "kw"  # "eh" rescued at depth 0
    role = {"id": "test-persona", "label": "Test", "errand": "test errand"}
    call = lesson_call(role, lesson, {})
    rescued = [t for t in call.snapshot()["turns"] if t.get("spark")]
    assert rescued and rescued[0]["spark"] == {"word": "kw", "confidence": 0.88}


def test_main_spark_keyless_keeps_sim_running(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("SPARK_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
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
        "--spark",
    ])
    assert code == 0
    assert "keyless" in capsys.readouterr().out
    raw = json.loads(board.read_text(encoding="utf-8"))
    assert raw["calls"][0]["turns"]
    assert all("spark" not in turn for turn in raw["calls"][0]["turns"])
