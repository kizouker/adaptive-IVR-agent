"""Shared constants and data structures for the v1 test suite.

Single source for every literal the tests use, so a wording change
touches one place. Test-first: the src API these mirror is not built yet.
"""

SPEAKER_ROBOT = "robot"
SPEAKER_CALLER = "caller"

WELCOME_LINE = "Welcome to The Castle."
TOPIC_LINE = "Say your concern."
CONFIRM_LINE = "Did you say compensation?"
ROBOT_LINES = [WELCOME_LINE, TOPIC_LINE, CONFIRM_LINE]

V1_LINES = ["Welcome.", "Say your concern.", "You said ersättning."]
EXPECTED_LINE_COUNT = 3

ROBOT_QUESTION = "What is your concern?"
CALLER_SIGNUP = "I want to sign up"

KEYWORD_COMPENSATION = "ersättning"
OUTCOME_COMPENSATION = "compensation"
KEYWORD_OFFICER = "handläggare"
OUTCOME_OFFICER = "case officer queue"

KEYWORD_TABLE = {
    KEYWORD_COMPENSATION: OUTCOME_COMPENSATION,
    KEYWORD_OFFICER: OUTCOME_OFFICER,
}

UNKNOWN_WORD = "nonsense"

STEP_FILE_NAME = "run.json"
V1_STEP_FILE_NAME = "v1-run.json"

DOORKEEPER_LINES_NAME = "doorkeeper-lines.json"
ROLE_PHRASEBOOKS_NAME = "role-phrasebooks.json"
MIN_DOORKEEPER_LINES = 3
MIN_ROLES = 8
