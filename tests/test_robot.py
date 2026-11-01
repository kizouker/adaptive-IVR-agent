"""Mini practice robot (FN-REQ-IVR-006). Sound is injected, so tests stay silent."""
from tests.test_data import ROBOT_LINES, SPEAKER_ROBOT, STEP_FILE_NAME
from adaptive_ivr_agent.robot import PracticeRobot
from adaptive_ivr_agent.steps import StepFile


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
