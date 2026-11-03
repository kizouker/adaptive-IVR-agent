"""Bake lines + model-call telemetry for the board (#177)."""
import importlib.util
import json
import sys
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parent.parent / "sh" / "bake-board.py"
    spec = importlib.util.spec_from_file_location("bake_board", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bake_board = _load()


def _write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def test_bake_writes_lines_and_telemetry(tmp_path, monkeypatch, capsys):
    board = tmp_path / "board-state.json"
    _write(board, {"generated": "test"})
    lines = tmp_path / "lines.json"
    _write(lines, {"lines": [{"id": "L01", "text": "hej", "en": "hi"}]})
    prov = tmp_path / "provenance.jsonl"
    prov.write_text(
        '{"model": "m", "runtime": "spark-hosted", "latency_ms": 12.5}\n',
        encoding="utf-8",
    )
    telemetry = tmp_path / "telemetry.json"
    monkeypatch.setattr(
        sys, "argv",
        ["bake-board.py", "--board", str(board), "--lines", str(lines),
         "--provenance", str(prov), "--telemetry-out", str(telemetry)],
    )
    assert bake_board.main() == 0
    baked = json.loads(board.read_text(encoding="utf-8"))
    assert baked["lines"] == [{"id": "L01", "text": "hej", "en": "hi"}]
    rows = json.loads(telemetry.read_text(encoding="utf-8"))
    assert rows == [{"model": "m", "runtime": "spark-hosted", "latency_ms": 12.5}]
    assert "baked 1 lines" in capsys.readouterr().out


def test_bake_missing_provenance_writes_empty_telemetry(tmp_path, monkeypatch):
    board = tmp_path / "board-state.json"
    _write(board, {"generated": "test"})
    lines = tmp_path / "lines.json"
    _write(lines, {"lines": []})
    telemetry = tmp_path / "telemetry.json"
    monkeypatch.setattr(
        sys, "argv",
        ["bake-board.py", "--board", str(board), "--lines", str(lines),
         "--provenance", str(tmp_path / "absent.jsonl"),
         "--telemetry-out", str(telemetry)],
    )
    assert bake_board.main() == 0
    assert json.loads(telemetry.read_text(encoding="utf-8")) == []
