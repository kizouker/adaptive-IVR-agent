"""Launcher menu: even padded rows, bold selection, sound follows output (S82).

Shell functions are extracted from sh/holdmate.sh at test time with stubbed
output switching, so the tests run anywhere bash runs (no audio needed).
"""
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash not installed (minimal container)"
)

ROOT = Path(__file__).resolve().parent.parent
MENU = ROOT / "sh" / "holdmate.sh"


def extract_nested(name):
    """Shell source of the nested draw() function."""
    text = MENU.read_text(encoding="utf-8").splitlines(keepends=True)
    start = next(
        i for i, line in enumerate(text) if line.startswith(f"  {name}() {{")
    )
    end = next(i for i in range(start + 1, len(text)) if text[i] == "  }\n")
    return "draw() {\n" + "".join(text[start + 1 : end + 1])


def extract_top(names):
    """Shell source of top-level functions from sh/holdmate.sh."""
    text = MENU.read_text(encoding="utf-8").splitlines(keepends=True)
    out = []
    for name in names:
        start = next(
            i for i, line in enumerate(text) if line.startswith(f"{name}() {{")
        )
        end = next(i for i in range(start, len(text)) if text[i] == "}\n")
        out.append("".join(text[start : end + 1]))
    return "\n".join(out)


def test_draw_pads_rows_and_marks_selection(tmp_path):
    script = (
        "B='<B>'; C='<C>'; D='<D>'; X='<X>'; sel=2\n"
        + extract_nested("draw")
        + '\ndraw "aa" "bbbb" "c" 2>out.txt\n'
    )
    harness = tmp_path / "draw.sh"
    harness.write_text(script, encoding="utf-8")
    done = subprocess.run(["bash", str(harness)], capture_output=True, text=True,
                          cwd=tmp_path, timeout=30)
    assert done.returncode == 0, done.stderr
    rows = (tmp_path / "out.txt").read_text(encoding="utf-8").splitlines()
    assert rows == [
        "<D>  [1] aa  <X>",
        "<B><C>> [2] bbbb<X>",
        "<D>  [3] c   <X>",
    ]


def test_sync_sound_follows_current_output(tmp_path):
    script = (
        extract_top(("sync_sound",))
        + '\nSwitchAudioSource() { echo "My AirPods"; }\n'
        + 'SOUND="speakers"; SOUND_DIRTY=0; sync_sound\n'
        + '[ "$SOUND" = "airpods" ] || exit 1\n'
        + 'SwitchAudioSource() { echo "Speakers"; }\n'
        + 'SOUND_DIRTY=0; sync_sound\n'
        + '[ "$SOUND" = "speakers" ] || exit 2\n'
        + "echo SYNC-OK\n"
    )
    done = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=30)
    assert done.returncode == 0, done.stderr
    assert "SYNC-OK" in done.stdout


def test_sync_sound_keeps_explicit_pick(tmp_path):
    script = (
        extract_top(("sync_sound",))
        + '\nSwitchAudioSource() { echo "My AirPods"; }\n'
        + 'SOUND="quiet"; SOUND_DIRTY=1; sync_sound\n'
        + '[ "$SOUND" = "quiet" ] || exit 1\n'
        + "echo DIRTY-OK\n"
    )
    done = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=30)
    assert done.returncode == 0, done.stderr
    assert "DIRTY-OK" in done.stdout


def test_sound_labels_capitalized(tmp_path):
    script = (
        extract_top(("sound_label",))
        + '\nSOUND="airpods"; [ "$(sound_label)" = "AirPods" ] || exit 1\n'
        + 'SOUND="quiet"; [ "$(sound_label)" = "Quiet" ] || exit 2\n'
        + 'SOUND="speakers"; [ "$(sound_label)" = "Speakers" ] || exit 3\n'
        + "echo LABELS-OK\n"
    )
    done = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=30)
    assert done.returncode == 0, done.stderr
    assert "LABELS-OK" in done.stdout
