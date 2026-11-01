"""Live call board data + page rendering (T-045)."""
import json
from datetime import datetime
from pathlib import Path

from adaptive_ivr_agent.menu_map import MenuMap
from adaptive_ivr_agent.reactive import ReactiveRobot

ENCODING = "utf-8"
STATE_PLACEHOLDER = "__STATE_JSON__"
WALK = ["open_question", "example_words", "yes_no"]

STATE_NAMES = {
    "open_question": {"sv": "Öppen fråga", "en": "Open question"},
    "example_words": {"sv": "Exempelord", "en": "Example words"},
    "yes_no": {"sv": "Ja/nej-fråga", "en": "Yes/no question"},
    "transfer": {"sv": "Kopplar vidare", "en": "Transferring"},
    "identification": {"sv": "Identifiering", "en": "Identification"},
    "queue": {"sv": "Kö", "en": "Queue"},
    "english_menu": {"sv": "Engelsk knappmeny", "en": "English key menu"},
    "english_submenu": {"sv": "Engelsk undermeny", "en": "English sub-menu"},
    "sms": {"sv": "SMS-erbjudande", "en": "SMS offer"},
    "officer": {"sv": "Handläggare", "en": "Officer"},
}


def _map_blob(shown: MenuMap) -> dict:
    return {
        "title": shown.title,
        "states": [
            {"id": s.id, **STATE_NAMES[s.id]} for s in shown.states
        ],
        "edges": [
            {"source": e.source, "target": e.target, "label": e.label}
            for e in shown.edges
        ],
    }


def build_call(persona_id: str, n_turns: int, phrasebooks: str | Path) -> dict:
    """Simulate the first turns of one persona's call against the robot."""
    path = Path(phrasebooks)
    roles = json.loads(path.read_text(encoding=ENCODING))["roles"]
    persona = next(r for r in roles if r["id"] == persona_id)
    robot = ReactiveRobot.from_phrasebooks(path)
    shown = MenuMap.af_agda()
    turns = []
    for word, state_id in zip(persona["vocabulary"][:n_turns], WALK):
        shown.move_to(state_id)
        reply, matched = robot.respond(word)
        turns.append(
            {
                "caller": word,
                "robot": reply,
                "matched": matched is not None,
                "state": state_id,
                "state_name": STATE_NAMES[state_id],
            }
        )
    return {
        "persona": persona_id,
        "label": persona["label"],
        "errand": persona["errand"],
        "map": "swedish",
        "position": shown.current,
        "turns": turns,
    }


def build_board(specs: list[tuple[str, int]], phrasebooks: str | Path) -> dict:
    """Board state for several (persona, turns) calls sharing one process view."""
    return {
        "generated": datetime.now().strftime("%H:%M:%S"),
        "maps": {
            "swedish": _map_blob(MenuMap.af_agda()),
            "english": _map_blob(MenuMap.english_branch()),
        },
        "calls": [build_call(pid, n, phrasebooks) for pid, n in specs],
    }


LIVE_PERSONA = "live-caller"
LIVE_LABEL = "You (live)"
LIVE_ERRAND = "Talking to Agda right now"
LIVE_CALLER_NAME = "You"
LIVE_ROBOT_NAME = "AF Agda (Alva)"
LIVE_MAP = "swedish"
OPEN_STATE = "open_question"


def vtt_timestamp(seconds: float) -> str:
    """Seconds as a WebVTT timestamp (HH:MM:SS.mmm)."""
    total_ms = int(round(seconds * 1000))
    hours, rest = divmod(total_ms, 3600000)
    minutes, rest = divmod(rest, 60000)
    secs, millis = divmod(rest, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def write_captions(path: str | Path, text: str, seconds: float) -> str:
    """Write a one-cue WebVTT subtitle file. Returns the path as a string."""
    cue = f"WEBVTT\n\n00:00.000 --> {vtt_timestamp(seconds)}\n{text.strip()}\n"
    Path(path).write_text(cue, encoding=ENCODING)
    return str(path)


class LiveCall:
    """One real call's turns, accumulated round by round for the board."""

    def __init__(
        self,
        persona: str = LIVE_PERSONA,
        label: str = LIVE_LABEL,
        errand: str = LIVE_ERRAND,
        map_name: str = LIVE_MAP,
        robot_name: str = LIVE_ROBOT_NAME,
    ) -> None:
        self._meta = {
            "persona": persona,
            "label": label,
            "errand": errand,
            "map": map_name,
            "robot_name": robot_name,
        }
        self.turns: list[dict] = []

    def add_turn(
        self,
        caller: str,
        robot: str,
        matched: bool,
        state_id: str,
        caller_audio: str | None = None,
        robot_audio: str | None = None,
        caller_captions: str | None = None,
        robot_captions: str | None = None,
        queue_place: int | None = None,
        queue_total: int | None = None,
        speaker: str | None = None,
    ) -> None:
        """Append one exchange. Media paths are board-relative (audio/...) or None."""
        turn = {
            "caller": caller,
            "robot": robot,
            "matched": matched,
            "state": state_id,
            "state_name": STATE_NAMES[state_id],
        }
        if caller_audio is not None:
            turn["caller_audio"] = caller_audio
        if robot_audio is not None:
            turn["robot_audio"] = robot_audio
        if caller_captions is not None:
            turn["caller_captions"] = caller_captions
        if robot_captions is not None:
            turn["robot_captions"] = robot_captions
        if queue_place is not None:
            turn["queue_place"] = queue_place
        if queue_total is not None:
            turn["queue_total"] = queue_total
        if speaker is not None:
            turn["speaker"] = speaker
        self.turns.append(turn)

    @property
    def position(self) -> str:
        """Latest state, or the open question before the first turn."""
        return self.turns[-1]["state"] if self.turns else OPEN_STATE

    def snapshot(self) -> dict:
        """Board-shaped call: build_call keys plus speaker names and media."""
        return {
            **self._meta,
            "position": self.position,
            "caller_name": LIVE_CALLER_NAME,
            "turns": self.turns,
        }


def build_live_board(calls: list[LiveCall]) -> dict:
    """Board state for live calls. Same top-level shape as build_board."""
    return {
        "generated": datetime.now().strftime("%H:%M:%S"),
        "maps": {
            "swedish": _map_blob(MenuMap.af_agda()),
            "english": _map_blob(MenuMap.english_branch()),
        },
        "calls": [call.snapshot() for call in calls],
    }


def render_live_page(state: dict, template_path: str | Path) -> str:
    """Fill the template with board state; raises if the placeholder is gone."""
    template = Path(template_path).read_text(encoding=ENCODING)
    if STATE_PLACEHOLDER not in template:
        raise ValueError("template placeholder missing")
    return template.replace(
        STATE_PLACEHOLDER, json.dumps(state, ensure_ascii=False)
    )
