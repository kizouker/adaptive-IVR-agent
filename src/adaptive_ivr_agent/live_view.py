"""Live call board data + page rendering (T-045)."""
import json
from datetime import datetime, timezone
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
    "queue": {"sv": "Kö", "en": "Queue"},
    "english_menu": {"sv": "Engelsk knappmeny", "en": "English key menu"},
    "english_submenu": {"sv": "Engelsk undermeny", "en": "English sub-menu"},
    "officer": {"sv": "Handläggare", "en": "Officer"},
}


def _map_blob(shown: MenuMap) -> dict:
    return {
        "title": shown.title,
        "states": [
            {"id": s.id, **STATE_NAMES[s.id]} for s in shown.states
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
        "generated": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "maps": {
            "swedish": _map_blob(MenuMap.af_agda()),
            "english": _map_blob(MenuMap.english_branch()),
        },
        "calls": [build_call(pid, n, phrasebooks) for pid, n in specs],
    }


def render_live_page(state: dict, template_path: str | Path) -> str:
    """Fill the template with board state; raises if the placeholder is gone."""
    template = Path(template_path).read_text(encoding=ENCODING)
    if STATE_PLACEHOLDER not in template:
        raise ValueError("template placeholder missing")
    return template.replace(
        STATE_PLACEHOLDER, json.dumps(state, ensure_ascii=False)
    )
