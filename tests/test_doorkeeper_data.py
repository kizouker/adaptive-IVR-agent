"""Documented Doorkeeper lines + role phrasebooks (T-039). Sound stays injected."""
import json
from pathlib import Path

from tests.test_data import (
    DOORKEEPER_LINES_NAME,
    MIN_DOORKEEPER_LINES,
    MIN_ROLES,
    ROLE_PHRASEBOOKS_NAME,
    STEP_FILE_NAME,
)
from adaptive_ivr_agent.robot import PracticeRobot, load_lines

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_doorkeeper_lines_load_in_order(tmp_path):
    lines = load_lines(DATA_DIR / DOORKEEPER_LINES_NAME)
    assert len(lines) >= MIN_DOORKEEPER_LINES
    assert all(line.strip() for line in lines)
    spoken = []
    PracticeRobot(lines[:MIN_DOORKEEPER_LINES], speak=spoken.append).run(
        tmp_path / STEP_FILE_NAME
    )
    assert spoken == lines[:MIN_DOORKEEPER_LINES]


def test_role_phrasebooks_have_roles_with_words():
    raw = json.loads((DATA_DIR / ROLE_PHRASEBOOKS_NAME).read_text(encoding="utf-8"))
    roles = raw["roles"]
    assert len(roles) >= MIN_ROLES
    for role in roles:
        assert role["id"] and role["af_sections"] and role["vocabulary"]
        assert role["goal"] and role["errand"]


def test_served_and_english_lines_have_verbatim_flags():
    raw = json.loads((DATA_DIR / DOORKEEPER_LINES_NAME).read_text(encoding="utf-8"))
    by_id = {line["id"]: line for line in raw["lines"]}
    assert by_id["L30"]["text"] == "Jag ska strax koppla fram dig till en ledig handläggare."
    assert by_id["L30"]["verbatim"] is False
    for line_id in ("L31", "L32", "L33", "L34", "L35"):
        assert by_id[line_id]["verbatim"] is True
        assert by_id[line_id]["lang"] == "en"
    assert by_id["L36"]["verbatim"] is False  # cut off: "in the..."
    assert by_id["L37"]["verbatim"] is False  # no English served line on tape
    assert by_id["L38"]["verbatim"] is False  # no English success line on tape
    assert by_id["L39"]["verbatim"] is False  # invented officer opening
    assert "handläggare" in by_id["L39"]["text"]
    assert by_id["L40"]["verbatim"] is False
    assert by_id["L40"]["lang"] == "en"
