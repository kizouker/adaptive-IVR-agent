"""AirPods target the physical device; device switch replays the line (S13).

Resolver unit tests run everywhere; the pty replay test needs 1s key slices
and runs in CI (skips where ptys are unavailable). The playback harness is
shared with tests/test_playback.py.
"""
import os
import pty
import subprocess
import time
from pathlib import Path

import pytest

from tests.test_playback import ROOT, STUBS, TALK, extract, stub_bin


def extract_one(name):
    """Shell source of one function from sh/talk.sh."""
    text = TALK.read_text(encoding="utf-8").splitlines(keepends=True)
    start = next(
        i for i, line in enumerate(text) if line.startswith(f"{name}() {{")
    )
    end = next(i for i in range(start, len(text)) if text[i] == "}\n")
    return "".join(text[start : end + 1])


def test_find_airpods_picks_physical_device(tmp_path):
    script = (
        "SwitchAudioSource() {\n"
        '  printf "%s\\n" "Hogtalare i MacBook Pro" "IVR_Agent_Output" "Ricks AirPods"\n'
        "}\n" + extract_one("find_airpods") + 'found="$(find_airpods)"\n'
        '[ "$found" = "Ricks AirPods" ] || { echo "got: $found"; exit 1; }\n'
        "echo AIRPODS-OK\n"
    )
    done = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=30)
    assert done.returncode == 0, done.stderr
    assert "AIRPODS-OK" in done.stdout


def test_find_airpods_empty_when_absent(tmp_path):
    script = (
        "SwitchAudioSource() {\n"
        '  printf "%s\\n" "Hogtalare i MacBook Pro" "IVR_Agent_Speakers"\n'
        "}\n" + extract_one("find_airpods") + 'found="$(find_airpods)"\n'
        '[ -z "$found" ] || { echo "got: $found"; exit 1; }\n'
        "echo ABSENT-OK\n"
    )
    done = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=30)
    assert done.returncode == 0, done.stderr
    assert "ABSENT-OK" in done.stdout


def test_playback_restarts_when_output_device_changes(tmp_path):
    try:
        primary, replica = pty.openpty()
    except OSError:
        pytest.skip("no pty devices on this machine")
    vol = tmp_path / ".talk-volume"
    vol.write_text("0.7", encoding="utf-8")
    current = tmp_path / "current-device"
    current.write_text("Speakers", encoding="utf-8")
    src = tmp_path / "line.aiff"
    src.write_text("fake", encoding="utf-8")
    script = (
        STUBS
        + extract()
        + f"""
VOLUME_FILE="{vol}"
QUIET=0
TALK_VOLUME="0.7"
play_skippable "{src}"
echo PLAYBACK-DONE
"""
    )
    bins = tmp_path / "bin"
    stub_bin(bins)
    (bins / "SwitchAudioSource").write_text(
        f'#!/bin/bash\ncat "{current}"\n', encoding="utf-8"
    )
    (bins / "SwitchAudioSource").chmod(0o755)
    env = dict(os.environ, PATH=f"{bins}{os.pathsep}{os.environ['PATH']}",
               AFPLAY_LOG=str(tmp_path / "afplay.log"),
               FFMPEG_LOG=str(tmp_path / "ffmpeg.log"))
    proc = subprocess.Popen(
        ["bash", "-c", script], stdin=replica, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, env=env,
    )
    os.close(replica)
    try:
        time.sleep(1.2)
        current.write_text("Pods", encoding="utf-8")  # output switched mid-line
        out = proc.communicate(timeout=25)[0]
    finally:
        os.close(primary)
        if proc.poll() is None:
            proc.kill()
    assert proc.returncode == 0, out
    assert "PLAYBACK-DONE" in out
    assert vol.read_text(encoding="utf-8") == "0.7"  # volume untouched
    calls = (tmp_path / "afplay.log").read_text(encoding="utf-8").splitlines()
    assert len(calls) >= 2, calls
    assert calls[0].startswith("afplay -v 0.7")
    assert any(" -v 0.7 " in call and "boost" not in call for call in calls[1:]), calls
