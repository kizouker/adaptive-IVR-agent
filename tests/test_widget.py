"""Queue widget parsing: latest ticket from board-state (#144)."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "queue_ticket", ROOT / "ui" / "widget" / "queue_ticket.py"
)
widget = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(widget)


def test_parse_ticket_finds_latest_place():
    data = {
        "generated": "2026-11-01 23:00 UTC",
        "calls": [
            {"position": "queue", "turns": [
                {"queue_place": 5, "queue_total": 9, "state": "queue"},
                {"queue_place": 3, "queue_total": 9, "state": "queue"},
            ]},
        ],
    }
    assert widget.parse_ticket(data) == {
        "place": 3, "total": 9, "state": "queue",
        "updated": "2026-11-01 23:00 UTC",
    }


def test_parse_ticket_without_queue_is_empty():
    data = {"generated": "x", "calls": [{"position": "open_question", "turns": []}]}
    assert widget.parse_ticket(data)["place"] is None


def test_parse_ticket_tolerates_garbage():
    assert widget.parse_ticket({})["place"] is None
    assert widget.parse_ticket({"calls": []})["place"] is None
    assert widget.format_once(None) == "ticket unreachable"


def test_display_shows_na_without_place():
    assert widget.format_display(None) == ("N/A", "board unreachable")
    line, sub = widget.format_display(
        {"place": None, "total": None, "state": "open_question", "updated": "x"})
    assert line == "N/A"
    assert "open_question" in sub


def test_display_shows_number_in_queue():
    line, sub = widget.format_display(
        {"place": 3, "total": 9, "state": "queue", "updated": "x"})
    assert line == "3"
    assert sub.startswith("in queue/9")
