"""Learning loop: pending misses, review answers, known words. Quiet tests."""

import json
from pathlib import Path

from adaptive_ivr_agent.learn import known_words, pending_misses, read_misses, review

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_pending_dedups_and_skips_reviewed():
    records = [
        {"heard": "  Vabba "},
        {"heard": "vabba"},
        {"heard": "blalajka"},
        {"heard": "   "},
        {"heard": "ersättning"},
    ]
    assert pending_misses(records, {"ersättning": "ersättning", "gammalt": None}) == [
        "vabba",
        "blalajka",
    ]


def test_review_maps_approve_skip_and_quit():
    answers = iter(["vab", "", None])
    result = review(["vabba", "blalajka", "aldrig frågad"], lambda heard: next(answers))
    assert result == {"vabba": "vab", "blalajka": None}


def test_review_normalizes_keywords():
    result = review(["vabba"], lambda heard: "  VAB ")
    assert result == {"vabba": "vab"}


def test_read_misses_tolerates_missing_file(tmp_path):
    assert read_misses(tmp_path / "nope.jsonl") == []


def test_known_words_come_from_phrasebooks():
    words = known_words(DATA_DIR / "role-phrasebooks.json")
    assert "vab" in words
    assert all(word == word.lower() for word in words)


def test_miss_record_roundtrip(tmp_path):
    path = tmp_path / "misses.jsonl"
    path.write_text(json.dumps({"heard": "vabba", "round": 1}) + "\n", encoding="utf-8")
    assert read_misses(path) == [{"heard": "vabba", "round": 1}]
