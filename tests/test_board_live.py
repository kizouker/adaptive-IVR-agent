"""One-command live board packaging (#249)."""
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None or shutil.which("npm") is None,
    reason="node/npm not installed",
)

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "sh" / "board-live.sh"


def test_check_mode_passes_preflight():
    proc = subprocess.run(
        ["bash", str(SCRIPT), "check"],
        capture_output=True, text=True, timeout=60, cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "OK: preflight" in proc.stdout
    assert "check only: nothing started" in proc.stdout


def test_bad_port_fails_fast():
    proc = subprocess.run(
        ["bash", str(SCRIPT), "--port=abc"],
        capture_output=True, text=True, timeout=60, cwd=ROOT,
    )
    assert proc.returncode != 0
    assert "--port needs a number" in proc.stderr


def test_unknown_arg_fails_fast():
    proc = subprocess.run(
        ["bash", str(SCRIPT), "wat"],
        capture_output=True, text=True, timeout=60, cwd=ROOT,
    )
    assert proc.returncode != 0
    assert "unknown arg" in proc.stderr
