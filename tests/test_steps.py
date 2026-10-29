"""Step files (FN-REQ-IVR-003). Test-first: implementation follows."""
from tests.test_data import (
    CALLER_SIGNUP,
    KEYWORD_COMPENSATION,
    ROBOT_QUESTION,
    SPEAKER_CALLER,
    SPEAKER_ROBOT,
    STEP_FILE_NAME,
    TOPIC_LINE,
    WELCOME_LINE,
)

from adaptive_ivr_agent.steps import Step, StepFile


def test_one_run_creates_a_step_file(tmp_path):
    path = tmp_path / STEP_FILE_NAME
    StepFile.save(path, [Step(0, SPEAKER_ROBOT, WELCOME_LINE), Step(1, SPEAKER_ROBOT, TOPIC_LINE)])
    assert path.exists()


def test_loaded_steps_keep_order_speaker_and_text(tmp_path):
    path = tmp_path / STEP_FILE_NAME
    steps = [Step(0, SPEAKER_ROBOT, WELCOME_LINE), Step(1, SPEAKER_CALLER, KEYWORD_COMPENSATION)]
    StepFile.save(path, steps)
    assert StepFile.load(path) == steps


def test_hand_logged_call_stores_as_steps(tmp_path):
    pairs = [(SPEAKER_ROBOT, ROBOT_QUESTION), (SPEAKER_CALLER, CALLER_SIGNUP)]
    steps = [Step(i, speaker, text) for i, (speaker, text) in enumerate(pairs)]
    path = tmp_path / STEP_FILE_NAME
    StepFile.save(path, steps)
    loaded = StepFile.load(path)
    assert [(s.speaker, s.text) for s in loaded] == pairs
