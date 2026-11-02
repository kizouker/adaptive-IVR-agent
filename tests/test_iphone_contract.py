"""Board JSON contract: the shape web/iPhone/Watch/widget readers agree on (#158).

Swift structs (BoardState/BoardCall/BoardTurn) decode these keys; if the
Python writers rename one, the devices silently show N/A. This pins them.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "ui" / "board" / "public" / "board-state.sample.json"


def test_sample_matches_reader_contract():
    board = json.loads(SAMPLE.read_text(encoding="utf-8"))
    assert "generated" in board
    assert "maps" in board and "swedish" in board["maps"]
    assert board["calls"], "sample needs at least one call"
    call = board["calls"][-1]
    assert "position" in call and "turns" in call
    assert call["turns"], "sample call needs at least one turn"
    turn = call["turns"][-1]
    for key in ("caller", "robot", "matched", "state"):
        assert key in turn, f"turn missing {key}"
    # Optional queue keys must be int-or-absent, never another type.
    for key in ("queue_place", "queue_total"):
        assert not isinstance(turn.get(key), bool)
        assert turn.get(key) is None or isinstance(turn.get(key), int)


def test_live_board_matches_reader_contract():
    live = ROOT / "ui" / "board" / "public" / "board-state.json"
    if not live.exists():
        return
    board = json.loads(live.read_text(encoding="utf-8"))
    assert "calls" in board
    for call in board["calls"]:
        assert "position" in call and "turns" in call
        for turn in call["turns"]:
            place = turn.get("queue_place")
            assert place is None or isinstance(place, int)
