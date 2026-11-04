#!/usr/bin/env python3
"""Mirror the tail of model-call provenance rows to the board's telemetry.json.

Usage: telemetry-live.py [--once] [--interval 2]
    [--provenance data/provenance.jsonl] [--out ui/board/public/telemetry.json]

The board polls telemetry.json every 5s; run this next to a talk/lessons run
so the Model calls panel stays live. Rows from the unit-test stub host
(x.test) are skipped, never real model calls; the skipped count is logged.
"""
import argparse
import json
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TELEMETRY_TAIL = 20


def tail_rows(path: Path, n: int = TELEMETRY_TAIL) -> tuple[list, int]:
    """Last n real provenance rows + skipped test-stub count. Never raises."""
    rows: list = []
    skipped = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return rows, skipped
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        host = urllib.parse.urlparse(str(row.get("endpoint", ""))).hostname or ""
        if host == "x.test":
            skipped += 1
            continue
        rows.append(row)
    return rows[-n:], skipped


def write_telemetry(provenance: Path, out: Path) -> int:
    rows, skipped = tail_rows(provenance)
    out.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    if skipped:
        print(f"telemetry-live: skipped {skipped} x.test rows", file=sys.stderr)
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep board telemetry.json live.")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--provenance", default=str(ROOT / "data" / "provenance.jsonl"))
    parser.add_argument("--out", default=str(ROOT / "ui" / "board" / "public" / "telemetry.json"))
    args = parser.parse_args()
    provenance = Path(args.provenance)
    out = Path(args.out)
    count = write_telemetry(provenance, out)
    print(f"telemetry-live: {count} rows -> {out}")
    if args.once:
        return 0
    last_mtime = provenance.stat().st_mtime if provenance.exists() else 0.0
    try:
        while True:
            time.sleep(max(0.5, args.interval))
            try:
                mtime = provenance.stat().st_mtime
            except OSError:
                continue
            if mtime != last_mtime:
                last_mtime = mtime
                count = write_telemetry(provenance, out)
                print(f"telemetry-live: {count} rows -> {out}")
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
