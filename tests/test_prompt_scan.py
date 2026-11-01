"""Prompt self-scan gate: instruction files hold no weakening directives.

Runs sh/check-prompts.sh (OWASP LLM01 baseline) and requires OK.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN = ROOT / "sh" / "check-prompts.sh"


def test_prompt_scan_reports_ok():
    proc = subprocess.run(
        ["bash", str(SCAN)], capture_output=True, text=True, cwd=ROOT, check=False
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "OK: prompt self-scan holds." in proc.stdout
