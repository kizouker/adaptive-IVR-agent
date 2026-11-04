"""Mini practice robot (FN-REQ-IVR-006). Sound is injected, so tests stay silent."""
from pathlib import Path

from tests.test_data import ROBOT_LINES, SPEAKER_ROBOT, STEP_FILE_NAME
from adaptive_ivr_agent.robot import PracticeRobot, load_indexed_lines, opening_cache_path
from adaptive_ivr_agent.steps import StepFile

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_robot_plays_three_lines(tmp_path):
    spoken = []
    robot = PracticeRobot(ROBOT_LINES, speak=spoken.append)
    robot.run(tmp_path / STEP_FILE_NAME)
    assert spoken == ROBOT_LINES


def test_each_line_is_saved_as_a_step(tmp_path):
    robot = PracticeRobot(ROBOT_LINES, speak=lambda text: None)
    path = tmp_path / STEP_FILE_NAME
    robot.run(path)
    steps = StepFile.load(path)
    assert [s.text for s in steps] == ROBOT_LINES
    assert all(s.speaker == SPEAKER_ROBOT for s in steps)


def test_lines_load_by_id_for_scripted_calls():
    lines = load_indexed_lines(DATA_DIR / "doorkeeper-lines.json")
    assert lines["L01"].startswith("Välkommen till Arbetsförmedlingen")
    assert lines["L19"] == "Jag kopplar dig vidare till en handläggare."


def test_lines_load_english_when_lang_en():
    lines = load_indexed_lines(DATA_DIR / "doorkeeper-lines.json", lang="en")
    assert lines["L01"].startswith("Welcome to Arbetsförmedlingen")
    assert lines["L19"] == "I will connect you to an officer."
    assert lines["L41"] == "Please answer yes or no."
    assert len(lines) == 44


def test_opening_cache_path_stable_and_distinct(tmp_path):
    cache = tmp_path / "cache" / "nested"
    first = opening_cache_path(cache, "Alva", "Samantha", "hej")
    assert first.parent == cache
    assert cache.is_dir()
    assert first.suffix == ".aiff"
    assert opening_cache_path(cache, "Alva", "Samantha", "hej") == first
    assert opening_cache_path(cache, "Alva", "Samantha", "hejdå") != first
    assert opening_cache_path(cache, "Klara", "Samantha", "hej") != first
    assert opening_cache_path(cache, "Alva", "Daniel", "hej") != first
