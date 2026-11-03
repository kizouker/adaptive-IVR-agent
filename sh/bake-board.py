#!/usr/bin/env python3
"""Bake doorkeeper lines into a board-state.json file.

Usage: bake-board.py --board <board-state.json> --lines <doorkeeper-lines.json>
    [--provenance <provenance.jsonl>] [--telemetry-out <telemetry.json>]

The board's fake CLI needs the real robot lines (id + Swedish + English).
The telemetry panel needs the tail of model-call provenance rows (#177).
Idempotent: rerunning overwrites the same `lines` key and telemetry file.
"""
import argparse
import json
from pathlib import Path

TELEMETRY_TAIL = 20


def main() -> int:
    parser = argparse.ArgumentParser(description="Bake lines into board state.")
    parser.add_argument("--board", required=True)
    parser.add_argument("--lines", required=True)
    parser.add_argument("--provenance", default="data/provenance.jsonl")
    parser.add_argument("--telemetry-out", default="")
    args = parser.parse_args()
    board_path = Path(args.board)
    board = json.loads(board_path.read_text(encoding="utf-8"))
    lines = json.loads(Path(args.lines).read_text(encoding="utf-8"))["lines"]
    board["lines"] = [
        {"id": entry["id"], "text": entry["text"], "en": entry.get("en")}
        for entry in lines
    ]
    board_path.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    telemetry_path = (
        Path(args.telemetry_out) if args.telemetry_out
        else board_path.parent / "telemetry.json"
    )
    rows = []
    try:
        text = Path(args.provenance).read_text(encoding="utf-8").splitlines()
        rows = [json.loads(line) for line in text if line.strip()][-TELEMETRY_TAIL:]
    except (OSError, ValueError):
        rows = []
    telemetry_path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    print(f"baked {len(board['lines'])} lines into {board_path}")
    print(f"baked {len(rows)} telemetry rows into {telemetry_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
