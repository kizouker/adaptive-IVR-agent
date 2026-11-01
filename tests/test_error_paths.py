"""Edge and error paths for robot, keywords, steps. All silent, no real I/O."""
import json

import pytest

from adaptive_ivr_agent.keywords import KeywordTable
from adaptive_ivr_agent.robot import PracticeRobot, load_lines
from adaptive_ivr_agent.steps import Step, StepFile


def test_run_returns_indexed_steps(tmp_path):
    robot = PracticeRobot(["hej", "då"], speak=lambda text: None)
    steps = robot.run(tmp_path / "run.json")
    assert [(s.index, s.speaker, s.text) for s in steps] == [
        (0, "robot", "hej"),
        (1, "robot", "då"),
    ]


def test_run_with_custom_speaker_and_no_lines(tmp_path):
    spoken = []
    robot = PracticeRobot([], speak=spoken.append, speaker="caller")
    steps = robot.run(tmp_path / "empty.json")
    assert steps == [] and spoken == []
    assert StepFile.load(tmp_path / "empty.json") == []

    robot = PracticeRobot(["hi"], speak=spoken.append, speaker="caller")
    assert robot.run(tmp_path / "one.json")[0].speaker == "caller"


def test_load_lines_missing_file_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_lines(tmp_path / "gone.json")


def test_load_lines_bad_shape_is_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"lines": [{"narrator": "x"}]}', encoding="utf-8")
    with pytest.raises(KeyError):
        load_lines(bad)


def test_words_for_unknown_outcome_raises():
    table = KeywordTable()
    table.add("ersättning", "compensation")
    with pytest.raises(KeyError):
        table.words_for("no-such-outcome")


def test_add_overwrites_both_directions():
    table = KeywordTable()
    table.add("a", "out-a")
    table.add("a", "out-b")
    assert table.outcome_for("a") == "out-b"
    assert table.words_for("out-b") == "a"


def test_save_returns_target_and_round_trips_empty(tmp_path):
    target = StepFile.save(tmp_path / "run.json", [])
    assert target == tmp_path / "run.json"
    assert StepFile.load(target) == []


def test_load_missing_file_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        StepFile.load(tmp_path / "gone.json")


def test_load_broken_json_is_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        StepFile.load(bad)


def test_load_wrong_shape_is_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('[{"index": 0}]', encoding="utf-8")
    with pytest.raises(TypeError):
        StepFile.load(bad)


def test_step_defaults_to_plain_value_object():
    assert Step(0, "robot", "hi") == Step(0, "robot", "hi")
    assert Step(0, "robot", "hi") != Step(1, "robot", "hi")
