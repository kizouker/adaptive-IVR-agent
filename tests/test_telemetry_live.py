"""Live telemetry mirror for the board (#249)."""
import importlib.util
import json
import sys
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parent.parent / "sh" / "telemetry-live.py"
    spec = importlib.util.spec_from_file_location("telemetry_live", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


telemetry_live = _load()

ROW = (
    '{"model": "muse-spark-1.3", "runtime": "spark-hosted", "stage": "rescue",'
    ' "endpoint": "https://api.meta.ai/v1", "latency_ms": 12.5,'
    ' "prompt_sha256": "a", "heard_sha256": "b",'
    ' "keyword": "vab", "confidence": 0.8}'
)
TEST_ROW = (
    '{"model": "muse-spark", "runtime": "spark-hosted",'
    ' "endpoint": "https://x.test/v1", "latency_ms": 0.0,'
    ' "prompt_sha256": "c", "heard_sha256": "d"}'
)


def test_tail_skips_test_stub_rows_and_bad_lines(tmp_path):
    prov = tmp_path / "provenance.jsonl"
    prov.write_text(f"{TEST_ROW}\nnot json\n{ROW}\n", encoding="utf-8")
    rows, skipped = telemetry_live.tail_rows(prov)
    assert skipped == 1
    assert len(rows) == 1
    assert rows[0]["stage"] == "rescue"


def test_tail_missing_file_is_empty(tmp_path):
    rows, skipped = telemetry_live.tail_rows(tmp_path / "nope.jsonl")
    assert rows == [] and skipped == 0


def test_once_writes_telemetry_file(tmp_path, monkeypatch, capsys):
    prov = tmp_path / "provenance.jsonl"
    prov.write_text(f"{ROW}\n", encoding="utf-8")
    out = tmp_path / "telemetry.json"
    monkeypatch.setattr(
        sys, "argv",
        ["telemetry-live.py", "--once", "--provenance", str(prov), "--out", str(out)],
    )
    assert telemetry_live.main() == 0
    rows = json.loads(out.read_text(encoding="utf-8"))
    assert len(rows) == 1 and rows[0]["model"] == "muse-spark-1.3"
