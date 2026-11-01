#!/usr/bin/env python3
"""Always-on-top queue ticket for macOS (PoC, #144).

Polls the board server for the latest queue place and shows it in a small
window that stays above other windows. Stdlib only; run with the system
python: /usr/bin/python3 ui/widget/queue_ticket.py [--once]

--once prints one ticket line to stdout without opening a window.
"""
import json
import os
import sys
import urllib.request
from typing import Optional

BOARD_URL = os.environ.get("BOARD_URL", "http://localhost:5173")
POLL_MS = 5000


def parse_ticket(data: dict) -> dict:
    """Latest queue ticket from a board-state dict. Never raises."""
    ticket = {"place": None, "total": None, "state": "-", "updated": data.get("generated", "-")}
    try:
        calls = data.get("calls") or []
        if not calls:
            return ticket
        live = calls[-1]
        ticket["state"] = live.get("position") or "-"
        for turn in reversed(live.get("turns") or []):
            if turn.get("queue_place") is not None:
                ticket["place"] = turn["queue_place"]
                ticket["total"] = turn.get("queue_total")
                break
    except (AttributeError, TypeError):
        pass
    return ticket


def fetch_ticket(url: str = BOARD_URL, timeout: int = 4) -> Optional[dict]:
    """Fetch board-state and parse the ticket. None when unreachable."""
    try:
        with urllib.request.urlopen(f"{url}/board-state.json", timeout=timeout) as res:
            return parse_ticket(json.load(res))
    except Exception:
        return None


def format_once(ticket: Optional[dict]) -> str:
    if ticket is None:
        return "ticket unreachable"
    return (
        f"place={ticket['place']} total={ticket['total']} "
        f"state={ticket['state']} updated={ticket['updated']}"
    )


def run_widget() -> int:
    import tkinter as tk

    root = tk.Tk()
    root.title("Holdmate queue")
    root.attributes("-topmost", True)
    root.resizable(False, False)
    number = tk.Label(root, text="-", font=("Helvetica", 64))
    number.pack(padx=24, pady=(12, 0))
    sub = tk.Label(root, text="starting…", font=("Helvetica", 12))
    sub.pack(padx=24, pady=(0, 12))

    def refresh():
        ticket = fetch_ticket()
        if ticket is None:
            number.config(text="-")
            sub.config(text="board unreachable")
        elif ticket["place"] is None:
            number.config(text="-")
            sub.config(text=f"{ticket['state']} · {ticket['updated']}")
        else:
            number.config(text=str(ticket["place"]))
            total = f"/{ticket['total']}" if ticket["total"] else ""
            sub.config(text=f"in queue{total} · {ticket['updated']}")
        root.after(POLL_MS, refresh)

    refresh()
    root.mainloop()
    return 0


def main(argv: list[str]) -> int:
    if "--once" in argv:
        print(format_once(fetch_ticket()))
        return 0
    return run_widget()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
