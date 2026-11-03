"""Talk startup: volume untouched by default, quiet remembered (#122, #123).

Runs sh/talk.sh check with stubbed audio tools so it works anywhere
(including Linux containers, #216): SwitchAudioSource answers device
queries, ffmpeg answers the mic index query, say/afplay/whisper-cli/ffprobe
are presence stubs for the tool preflight, and a fake Whisper model stands
in via HOME. Quiet state goes to a tmp file via TALK_QUIET_FILE.
"""
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash not installed (minimal container)"
)

ROOT = Path(__file__).resolve().parent.parent
TALK = ROOT / "sh" / "talk.sh"

SWITCH_STUB = """#!/bin/bash
# No AirPods, fixed mic, fixed output.
if [ "$1" = "-a" ]; then
  case "$3" in
    output) printf 'IVR_Agent_Speakers\\nHgtalare i MacBook Pro\\n' ;;
    input) printf 'MacBook Pro-mikrofon\\n' ;;
  esac
elif [ "$1" = "-c" ]; then
  printf 'Hgtalare i MacBook Pro\\n'
fi
"""

FFMPEG_STUB = """#!/bin/bash
printf 'audio devices:\\n[0] MacBook Pro-mikrofon\\n'
"""

# Check mode never runs these beyond the `command -v` preflight, so a bare
# presence stub is enough (and keeps macOS runs hermetic too).
NOOP_STUB = "#!/bin/bash\nexit 0\n"


def run_check(tmp_path, *args, quiet_seed=None):
    binder = tmp_path / "bin"
    binder.mkdir()
    stubs = {
        "SwitchAudioSource": SWITCH_STUB,
        "ffmpeg": FFMPEG_STUB,
        "ffprobe": NOOP_STUB,
        "whisper-cli": NOOP_STUB,
        "say": NOOP_STUB,
        "afplay": NOOP_STUB,
    }
    for name, body in stubs.items():
        stub = binder / name
        stub.write_text(body, encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    home = tmp_path / "home"
    (home / "models" / "whisper").mkdir(parents=True)
    (home / "models" / "whisper" / "ggml-small.bin").write_text(
        "fake model for talk.sh check", encoding="utf-8"
    )
    quiet_file = tmp_path / "q"
    if quiet_seed is not None:
        quiet_file.write_text(quiet_seed, encoding="utf-8")
    env = dict(os.environ, TALK_QUIET_FILE=str(quiet_file), HOME=str(home))
    env["PATH"] = f"{binder}{os.pathsep}{env['PATH']}"
    proc = subprocess.run(
        ["bash", str(TALK), "check", *args],
        capture_output=True, text=True, cwd=ROOT, env=env, check=False,
    )
    return proc, quiet_file


def test_check_leaves_volume_untouched_by_default(tmp_path):
    proc, _ = run_check(tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "leaves the system volume untouched" in proc.stdout
    assert "quiet mode: type + read" not in proc.stdout


def test_check_floor_reports_raise(tmp_path):
    proc, _ = run_check(tmp_path, "--floor")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "would unmute + raise" in proc.stdout


def test_check_remembers_quiet(tmp_path):
    proc, _ = run_check(tmp_path, quiet_seed="1")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "quiet mode: type + read" in proc.stdout


def test_check_sound_overrides_and_saves(tmp_path):
    proc, quiet_file = run_check(tmp_path, "--sound", quiet_seed="1")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "quiet mode: type + read" not in proc.stdout
    assert quiet_file.read_text(encoding="utf-8") == "0"


def test_check_quiet_flag_saves(tmp_path):
    proc, quiet_file = run_check(tmp_path, "--quiet")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "quiet mode: type + read" in proc.stdout
    assert quiet_file.read_text(encoding="utf-8") == "1"
