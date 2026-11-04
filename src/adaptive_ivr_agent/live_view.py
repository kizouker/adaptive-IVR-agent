"""Live call board data + page rendering (T-045)."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from adaptive_ivr_agent.menu_map import MenuMap
from adaptive_ivr_agent.reactive import ReactiveRobot

ENCODING = "utf-8"
STATE_PLACEHOLDER = "__STATE_JSON__"
WALK = ["open_question", "example_words", "yes_no"]


def utc_stamp() -> str:
    """Board clock: UTC date + time so Pages and local show the same thing."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

STATE_NAMES = {
    "open_question": {"sv": "Öppen fråga", "en": "Open question"},
    "example_words": {"sv": "Exempelord", "en": "Example words"},
    "yes_no": {"sv": "Ja/nej-fråga", "en": "Yes/no question"},
    "transfer": {"sv": "Kopplar vidare", "en": "Transferring"},
    "identification": {"sv": "Identifiering", "en": "Identification"},
    "queue": {"sv": "Kö", "en": "Queue"},
    "survey": {"sv": "Enkät", "en": "Survey"},
    "busy_welcome": {"sv": "Upptaget-hälsning", "en": "Busy-day welcome"},
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
            {"source": e.source, "target": e.target, "label": e.label,
             "label_en": e.label_en or e.label}
            for e in shown.edges
        ],
    }


def build_call(persona_id: str, n_turns: int, phrasebooks: str | Path) -> dict:
    """Simulate the first turns of one persona's call against the robot."""
    path = Path(phrasebooks)
    roles = json.loads(path.read_text(encoding=ENCODING))["roles"]
    persona = next(r for r in roles if r["id"] == persona_id)
    robot = ReactiveRobot.from_phrasebooks(path)
    shown = MenuMap.af_roksolana()
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
        "errand_en": persona["errand_en"],
        "map": "swedish",
        "position": shown.current,
        "turns": turns,
    }


def build_board(specs: list[tuple[str, int]], phrasebooks: str | Path) -> dict:
    """Board state for several (persona, turns) calls sharing one process view."""
    return {
        "generated": utc_stamp(),
        "maps": {
            "swedish": _map_blob(MenuMap.af_roksolana()),
            "english": _map_blob(MenuMap.english_branch()),
            "busy": _map_blob(MenuMap.busy_day()),
        },
        "calls": [build_call(pid, n, phrasebooks) for pid, n in specs],
    }


LIVE_PERSONA = "live-caller"
LIVE_LABEL = "You (live)"
LIVE_ERRAND = "Talking to Roksolana right now"
LIVE_CALLER_NAME = "You"
LIVE_ROBOT_NAME = "AF Roksolana (Alva)"
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


QUEUE_PLACE_SV = re.compile(r"Du har plats (\d+) i kön")
SPECIAL_PROBES = ("ja", "nej", "hej", "tack", "")
ENGLISH_DIGITS = ("1", "2", "4")


def build_coverage(roles: list, knowledge_words: dict) -> dict:
    """Pacman matrix: explorable menu tokens grouped, eaten ones flagged.

    Cells repeat shared tokens per group (each persona's menu); the
    total/tried counts use unique tokens so the share stays honest.
    """
    groups = [(role["id"], list(dict.fromkeys(role["vocabulary"]))) for role in roles]
    groups.append(("special", list(SPECIAL_PROBES)))
    groups.append(("english", list(ENGLISH_DIGITS)))
    cells = []
    seen: dict = {}
    for group, tokens in groups:
        for token in tokens:
            entry = knowledge_words.get(token, {})
            tries = entry.get("tries", 0)
            tried = tries > 0
            cells.append({
                "token": token,
                "label": token if token else "(silence)",
                "group": group,
                "tried": tried,
                "tries": tries,
                "transfers": entry.get("transfers", 0),
            })
            if token not in seen:
                seen[token] = tried
    return {"total": len(seen), "tried": sum(seen.values()), "cells": cells}


def line_translations(path: str | Path) -> dict[str, str]:
    """Swedish-to-English map from the lines file (entries with en only)."""
    raw = json.loads(Path(path).read_text(encoding=ENCODING))
    return {line["text"]: line["en"] for line in raw["lines"] if "en" in line}


def translate_robot(text: str, translations: dict[str, str]) -> str:
    """English rendering of Roksolana's known lines; unknown text passes through."""
    out = text
    for sv, en in sorted(translations.items(), key=lambda kv: -len(kv[0])):
        if sv in out:
            out = out.replace(sv, en)
    match = QUEUE_PLACE_SV.search(out)
    if match:
        out = out.replace(
            match.group(0), f"You are number {match.group(1)} in the queue."
        )
    return out


class LiveCall:
    """One real call's turns, accumulated round by round for the board."""

    def __init__(
        self,
        persona: str = LIVE_PERSONA,
        label: str = LIVE_LABEL,
        errand: str = LIVE_ERRAND,
        map_name: str = LIVE_MAP,
        robot_name: str = LIVE_ROBOT_NAME,
        errand_en: str | None = None,
    ) -> None:
        self._meta = {
            "persona": persona,
            "label": label,
            "errand": errand,
            "errand_en": errand_en or errand,
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
        robot_en: str | None = None,
        spark: dict | None = None,
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
        if robot_en is not None:
            turn["robot_en"] = robot_en
        if spark is not None:
            turn["spark"] = {"word": spark["word"], "confidence": spark["confidence"]}
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
        "generated": utc_stamp(),
        "maps": {
            "swedish": _map_blob(MenuMap.af_roksolana()),
            "english": _map_blob(MenuMap.english_branch()),
        },
        "calls": [call.snapshot() for call in calls],
    }


def carry_board_lines(board: dict, path: str | Path) -> dict:
    """Keep baked CLI lines when talk mode rewrites the board file."""
    try:
        old = json.loads(Path(path).read_text(encoding=ENCODING))
    except (OSError, ValueError):
        return board
    if isinstance(old, dict) and "lines" in old:
        board["lines"] = old["lines"]
    return board


def render_live_page(state: dict, template_path: str | Path) -> str:
    """Fill the template with board state; raises if the placeholder is gone."""
    template = Path(template_path).read_text(encoding=ENCODING)
    if STATE_PLACEHOLDER not in template:
        raise ValueError("template placeholder missing")
    return template.replace(
        STATE_PLACEHOLDER, json.dumps(state, ensure_ascii=False)
    )
