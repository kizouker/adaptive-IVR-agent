"""Secrets must never reach Git: .env ignored everywhere, never tracked."""
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_env_ignored_at_root_and_board():
    out = subprocess.run(
        ["git", "check-ignore", ".env", "ui/board/.env"],
        capture_output=True, text=True, cwd=REPO)
    assert ".env" in out.stdout
    assert "ui/board/.env" in out.stdout


def test_env_not_tracked():
    out = subprocess.run(["git", "ls-files"], capture_output=True,
                         text=True, cwd=REPO)
    tracked = out.stdout.splitlines()
    assert ".env" not in tracked
    assert "ui/board/.env" not in tracked


def test_env_example_has_no_secrets():
    example = (REPO / ".env.example").read_text()
    for line in example.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            name, _ = line.split("=", 1)
            if any(tag in name for tag in ("KEY", "PASS", "SECRET", "TOKEN")):
                assert line.endswith("="), f"secret in .env.example: {name}"
