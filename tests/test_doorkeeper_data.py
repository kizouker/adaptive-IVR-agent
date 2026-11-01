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
