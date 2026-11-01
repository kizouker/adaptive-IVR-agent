#!/usr/bin/env python3
"""Bake doorkeeper lines into a board-state.json file.

Usage: bake-board.py --board <board-state.json> --lines <doorkeeper-lines.json>

The board's fake CLI needs the real robot lines (id + Swedish + English).
Idempotent: rerunning overwrites the same `lines` key.
"""
import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Bake lines into board state.")
    parser.add_argument("--board", required=True)
    parser.add_argument("--lines", required=True)
    args = parser.parse_args()
    board_path = Path(args.board)
    board = json.loads(board_path.read_text(encoding="utf-8"))
    lines = json.loads(Path(args.lines).read_text(encoding="utf-8"))["lines"]
    board["lines"] = [
        {"id": entry["id"], "text": entry["text"], "en": entry.get("en")}
        for entry in lines
    ]
    board_path.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print(f"baked {len(board['lines'])} lines into {board_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
