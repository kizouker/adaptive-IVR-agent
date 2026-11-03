"""Playback volume follows the slider live (S12): prepare + restart proof.

The shell functions are extracted from sh/talk.sh at test time (no drift),
with stubbed afplay/ffmpeg/ffprobe, so the tests run on CI (ubuntu, no
afplay) as well as on the Mac. The restart test needs a pty for 1s key
slices; where ptys are unavailable it skips (CI runs it).
"""
import os
import pty
import shutil
import subprocess
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash not installed (minimal container)"
)

ROOT = Path(__file__).resolve().parent.parent
TALK = ROOT / "sh" / "talk.sh"
FUNCS = ("wait_keys", "load_volume", "volume_step", "prepare_playback", "play_skippable")

STUBS = """
info() { echo "info: $*" >&2; }
warn() { echo "warn: $*" >&2; }
quit_call() { echo "QUIT"; exit 3; }
fail() { echo "FAIL: $1"; exit 4; }
toggle_output() { :; }
toggle_quiet() { return 1; }
save_volume() { printf '%s' "$TALK_VOLUME" > "$VOLUME_FILE"; }
"""


def extract():
    """Shell source of the playback functions, taken from sh/talk.sh."""
    text = TALK.read_text(encoding="utf-8").splitlines(keepends=True)
    out = []
    for name in FUNCS:
        start = next(
            i for i, line in enumerate(text) if line.startswith(f"{name}() {{")
        )
        end = next(i for i in range(start, len(text)) if text[i] == "}\n")
        out.append("".join(text[start : end + 1]))
    return "\n".join(out)


def stub_bin(path: Path) -> None:
    """Fake afplay (log + sleep), ffmpeg (log + cp) and ffprobe (2.0s)."""
    path.mkdir(parents=True, exist_ok=True)
    (path / "afplay").write_text(
        '#!/bin/bash\necho "afplay $@" >> "$AFPLAY_LOG"\nexec sleep 3\n',
        encoding="utf-8",
    )
    (path / "ffmpeg").write_text(
        '#!/bin/bash\necho "ffmpeg $@" >> "$FFMPEG_LOG"\n'
        'while [ $# -gt 0 ]; do case "$1" in -i) shift; IN="$1";; esac; '
        'LAST="$1"; shift; done\ncp "$IN" "$LAST"\n',
        encoding="utf-8",
    )
    (path / "ffprobe").write_text('#!/bin/bash\necho "2.0"\n', encoding="utf-8")
    for tool in ("afplay", "ffmpeg", "ffprobe"):
        (path / tool).chmod(0o755)


def test_prepare_rebuilds_boost_when_file_changes(tmp_path):
    vol = tmp_path / ".talk-volume"
    vol.write_text("0.7", encoding="utf-8")
    src = tmp_path / "line.aiff"
    src.write_text("fake", encoding="utf-8")
    script = (
        STUBS
        + extract()
        + f"""
VOLUME_FILE="{vol}"
QUIET=0
TALK_VOLUME="0.7"
PLAY_SRC="{src}"
prepare_playback
[ "$PLAY_VOL" = "0.7" ] && [ "$PLAY_FROM" = "0.7" ] && [ "$PLAY_FILE" = "{src}" ] || exit 10
echo "2.5" > "{vol}"
load_volume
[ "$TALK_VOLUME" = "2.5" ] || exit 11
[ "$TALK_VOLUME" != "$PLAY_FROM" ] || exit 12
prepare_playback
[ "$PLAY_VOL" = "1" ] || exit 13
[ "$PLAY_FILE" = "{src}-boost.aiff" ] || exit 14
echo "junk" > "{vol}"
load_volume
[ "$TALK_VOLUME" = "2.5" ] || exit 15
echo PREPARE-OK
"""
    )
    bins = tmp_path / "bin"
    stub_bin(bins)
    env = dict(os.environ, PATH=f"{bins}{os.pathsep}{os.environ['PATH']}",
               FFMPEG_LOG=str(tmp_path / "ffmpeg.log"))
    done = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=30, env=env)
    assert done.returncode == 0, done.stderr
    assert "PREPARE-OK" in done.stdout
    assert "volume=2.5" in (tmp_path / "ffmpeg.log").read_text(encoding="utf-8")


def test_playback_restarts_when_slider_moves(tmp_path):
    try:
        primary, replica = pty.openpty()
    except OSError:
        pytest.skip("no pty devices on this machine")
    vol = tmp_path / ".talk-volume"
    vol.write_text("0.7", encoding="utf-8")
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
        vol.write_text("2.5", encoding="utf-8")  # the slider moves mid-line
        out = proc.communicate(timeout=25)[0]
    finally:
        os.close(primary)
        if proc.poll() is None:
            proc.kill()
    assert proc.returncode == 0, out
    assert "PLAYBACK-DONE" in out
    calls = (tmp_path / "afplay.log").read_text(encoding="utf-8").splitlines()
    assert len(calls) >= 2, calls
    assert calls[0].startswith("afplay -v 0.7")
    assert any(" -v 1 " in call and "boost.aiff" in call for call in calls[1:]), calls
