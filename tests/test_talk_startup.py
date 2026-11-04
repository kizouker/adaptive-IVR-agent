"""Talk startup: volume untouched by default, quiet remembered (#122, #123).

Check warns (exit 0) on a clean machine without audio devices, and still
fails loudly when a device list is broken (#213).

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
    output) printf 'IVR_Output_Speakers\\nHgtalare i MacBook Pro\\n' ;;
    input) printf 'MacBook Pro-mikrofon\\n' ;;
  esac
elif [ "$1" = "-c" ]; then
  printf 'Hgtalare i MacBook Pro\\n'
fi
"""

SWITCH_STUB_NO_OUTPUT = """#!/bin/bash
# Clean machine output side: no aggregate, no AirPods. Mic present.
if [ "$1" = "-a" ]; then
  case "$3" in
    output) printf 'Built-in Output\\n' ;;
    input) printf 'MacBook Pro-mikrofon\\n' ;;
  esac
elif [ "$1" = "-c" ]; then
  printf 'Built-in Output\\n'
fi
"""

SWITCH_STUB_NO_MIC = """#!/bin/bash
# Output present, mic name unknown on this machine.
if [ "$1" = "-a" ]; then
  case "$3" in
    output) printf 'IVR_Output_Speakers\\nBuilt-in Output\\n' ;;
    input) printf 'Built-in Microphone\\n' ;;
  esac
elif [ "$1" = "-c" ]; then
  printf 'Built-in Output\\n'
fi
"""

SWITCH_STUB_NO_DEVICES = """#!/bin/bash
# Clean machine: no aggregate, no AirPods, unknown mic.
if [ "$1" = "-a" ]; then
  case "$3" in
    output) printf 'Built-in Output\\n' ;;
    input) printf 'Built-in Microphone\\n' ;;
  esac
elif [ "$1" = "-c" ]; then
  printf 'Built-in Output\\n'
fi
"""

SWITCH_STUB_BROKEN = """#!/bin/bash
# Broken audio setup: every query errors.
echo "SwitchAudioSource: boom" >&2
exit 1
"""

FFMPEG_STUB = """#!/bin/bash
printf 'audio devices:\\n[0] MacBook Pro-mikrofon\\n'
"""

FFMPEG_STUB_EMPTY = """#!/bin/bash
# Broken ffmpeg/avfoundation: no audio devices at all.
printf 'video devices:\\n[0] FaceTime Camera\\n'
"""
# Check mode never runs these beyond the `command -v` preflight, so a bare
# presence stub is enough (and keeps macOS runs hermetic too).
NOOP_STUB = "#!/bin/bash\nexit 0\n"



def _run(tmp_path, argv, switch_stub=None, ffmpeg_stub=None, quiet_seed=None):
    # Hermetic script root (#241): sh/talk.sh derives ROOT from its own
    # location and reads remembered state there ($ROOT/.talk-output,
    # .talk-input, .menu-lang, .talk-volume, .talk-quiet). Running the repo
    # script directly lets a repo-root .talk-output pin the remembered device
    # and mask the default, so run a copy under tmp_path instead. Only the
    # phrasebooks existence check matters in check mode, so stage just that
    # data file (keeps the run from touching repo data/recordings either).
    fakeroot = tmp_path / "root"
    (fakeroot / "sh").mkdir(parents=True)
    shutil.copy(ROOT / "sh" / "talk.sh", fakeroot / "sh" / "talk.sh")
    shutil.copy(ROOT / "sh" / "ui.sh", fakeroot / "sh" / "ui.sh")
    (fakeroot / "data").mkdir()
    shutil.copy(
        ROOT / "data" / "role-phrasebooks.json",
        fakeroot / "data" / "role-phrasebooks.json",
    )
    script = fakeroot / "sh" / "talk.sh"
    binder = tmp_path / "bin"
    binder.mkdir()
    stubs = {
        "SwitchAudioSource": switch_stub or SWITCH_STUB,
        "ffmpeg": ffmpeg_stub or FFMPEG_STUB,
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
        ["bash", str(script), *argv],
        capture_output=True, text=True, cwd=fakeroot, env=env, check=False,
    )
    return proc, quiet_file


def run_check(tmp_path, *args, quiet_seed=None,
              switch_stub=SWITCH_STUB, ffmpeg_stub=FFMPEG_STUB):
    return _run(tmp_path, ["check", *args], switch_stub, ffmpeg_stub, quiet_seed)


def run_talk(tmp_path, *args, switch_stub=SWITCH_STUB, ffmpeg_stub=FFMPEG_STUB):
    """Talk mode. Only safe for fail-fast preflight paths (no switching)."""
    return _run(tmp_path, list(args), switch_stub, ffmpeg_stub)


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


def test_default_output_is_ivr_speakers_aggregate():
    line = next(
        line for line in TALK.read_text(encoding="utf-8").splitlines()
        if line.startswith("OUTPUT_SPEAKERS=")
    )
    assert "IVR_Output_Speakers" in line


def test_check_warns_not_fails_without_output_device(tmp_path):
    proc, _ = run_check(tmp_path, switch_stub=SWITCH_STUB_NO_OUTPUT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "WARN" in proc.stdout
    assert "Output device 'IVR_Output_Speakers' not found" in proc.stdout
    assert "nothing changed" in proc.stdout


def test_check_warns_not_fails_without_mic(tmp_path):
    proc, _ = run_check(tmp_path, switch_stub=SWITCH_STUB_NO_MIC)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "WARN" in proc.stdout
    assert "Mic 'MacBook Pro-mikrofon' not found" in proc.stdout
    assert "ffmpeg mic index: skipped" in proc.stdout
    assert "nothing changed" in proc.stdout


def test_check_clean_machine_warns_and_exits_zero(tmp_path):
    proc, _ = run_check(tmp_path, switch_stub=SWITCH_STUB_NO_DEVICES)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Output device 'IVR_Output_Speakers' not found" in proc.stdout
    assert "Mic 'MacBook Pro-mikrofon' not found" in proc.stdout
    assert "audio devices missing" in proc.stdout
    assert "FAIL" not in proc.stdout


def test_check_airpods_flag_warns_without_airpods(tmp_path):
    proc, _ = run_check(tmp_path, "--airpods")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "No AirPods found among output devices" in proc.stdout
    assert "FAIL" not in proc.stdout


def test_check_fails_when_output_list_broken(tmp_path):
    proc, _ = run_check(tmp_path, switch_stub=SWITCH_STUB_BROKEN)
    assert proc.returncode != 0
    assert "Could not list output devices" in proc.stdout


def test_check_fails_when_ffmpeg_sees_no_devices(tmp_path):
    # Mic exists per SwitchAudioSource but ffmpeg sees nothing: broken.
    proc, _ = run_check(tmp_path, ffmpeg_stub=FFMPEG_STUB_EMPTY)
    assert proc.returncode != 0
    assert "Could not find 'MacBook Pro-mikrofon'" in proc.stdout


def test_talk_mode_still_fails_without_output_device(tmp_path):
    proc, _ = run_talk(tmp_path, switch_stub=SWITCH_STUB_NO_OUTPUT)
    assert proc.returncode != 0
    assert "Output device 'IVR_Output_Speakers' not found" in proc.stdout


def test_talk_mode_still_fails_without_mic(tmp_path):
    proc, _ = run_talk(tmp_path, switch_stub=SWITCH_STUB_NO_MIC)
    assert proc.returncode != 0
    assert "Mic 'MacBook Pro-mikrofon' not found" in proc.stdout
