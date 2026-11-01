"""v1 walking skeleton (FN-REQ-IVR-003 + FN-REQ-IVR-004 + FN-REQ-IVR-006)."""
from tests.test_data import (
    EXPECTED_LINE_COUNT,
    KEYWORD_COMPENSATION,
    OUTCOME_COMPENSATION,
    V1_LINES,
    V1_STEP_FILE_NAME,
)
from adaptive_ivr_agent.keywords import KeywordTable
from adaptive_ivr_agent.robot import PracticeRobot
from adaptive_ivr_agent.steps import StepFile


def test_one_run_creates_a_step_file(tmp_path):
    table = KeywordTable()
    table.add(KEYWORD_COMPENSATION, OUTCOME_COMPENSATION)
    assert table.words_for(OUTCOME_COMPENSATION) == KEYWORD_COMPENSATION

    spoken = []
    robot = PracticeRobot(V1_LINES, speak=spoken.append)
    path = tmp_path / V1_STEP_FILE_NAME
    robot.run(path)

    assert len(spoken) == EXPECTED_LINE_COUNT
    assert path.exists()
    assert len(StepFile.load(path)) == EXPECTED_LINE_COUNT
