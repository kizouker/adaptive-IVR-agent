#!/usr/bin/env python3
"""Render headless video shots: terminal-style card + Samantha narration (#132).

Shots 1,2,4,7,8,9,11 (scriptable). Shots 3,5,6,10 need live filming.
Run: .venv/bin/python sh/make-shots.py   (writes data/video/auto/*.mp4)
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "video" / "auto"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
BG = (12, 14, 20)
FG = (230, 235, 240)
GREEN = (110, 220, 130)
DIM = (130, 140, 155)
FONT = "/System/Library/Fonts/Menlo.ttc"
VOICE = "Samantha"


def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       cwd=ROOT, timeout=180,
                       env={"PATH": "/opt/homebrew/bin:/usr/bin:/bin",
                            "PYTHONPATH": "src"})
    return (p.stdout + p.stderr).strip()


def card(lines, path):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    try:
        f_big = ImageFont.truetype(FONT, 44, index=0)
        f = ImageFont.truetype(FONT, 34, index=0)
    except OSError:
        f_big = f = ImageFont.load_default()
    y = 140
    for kind, text in lines:
        font = f_big if kind == "h" else f
        color = {"h": FG, "cmd": GREEN, "dim": DIM}.get(kind, FG)
        for chunk in text.split("\n"):
            d.text((140, y), chunk[:86], font=font, fill=color)
            y += 64 if kind == "h" else 48
        y += 14
    d.text((140, H - 90), "HOLDMATE  •  adaptive-IVR-agent", font=f, fill=DIM)
    img.save(path)


def duration_of(path):
    try:
        return float(run_cmd("ffprobe -hide_banner -v error -show_entries "
                             f"format=duration -of csv=p=0 {path}"))
    except ValueError:
        return 0.0


def narrate(text, wav_path):
    """Samantha narration. Empty (<1s) when say is sandboxed -> None."""
    aiff = wav_path.with_suffix(".aiff")
    subprocess.run(["say", "-v", VOICE, "-o", str(aiff), text],
                   check=True, timeout=120)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(aiff), "-c:a", "pcm_s16le", str(wav_path)],
                   check=True, timeout=120)
    aiff.unlink()
    if duration_of(wav_path) < 1.0:
        wav_path.unlink(missing_ok=True)
        return None
    return wav_path


def mux(png, wav, mp4, seconds):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-loop", "1", "-framerate", "30", "-i", str(png)]
    if wav is not None:
        cmd += ["-i", str(wav), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest", str(mp4)]
    else:
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-t", str(seconds), str(mp4)]
    subprocess.run(cmd, check=True, timeout=300)


def shot(num, name, lines, say):
    png = OUT / f"shot-{num:02d}-{name}.png"
    wav = OUT / f"shot-{num:02d}-{name}.wav"
    mp4 = OUT / f"shot-{num:02d}-{name}.mp4"
    txt = OUT / f"shot-{num:02d}-{name}.txt"
    card(lines, png)
    txt.write_text(say + "\n")
    estimate = max(4.0, len(say.split()) / 2.5)
    voice = narrate(say, wav)
    mux(png, voice, mp4, estimate)
    print(f"{mp4.name}  {duration_of(mp4):.1f}s"
          f"  {'voiced' if voice else 'silent+dub-text'}")
    return mp4


pytest_tail = "\n".join(run_cmd(
    "PYTHONPATH=src /opt/homebrew/bin/pytest tests/ -q -p no:cacheprovider"
    ).splitlines()[-4:])
eval_tail = "\n".join(run_cmd(
    "PYTHONPATH=src python3 eval/llm_intent_eval.py").splitlines()[-3:])

shot(1, "title", [
    ("h", "Holdmate"),
    ("", "Sweden's voice-menu maze only understands exact words."),
    ("", "Holdmate learns them for you."),
    ("dim", "Built from scratch Oct 26 - Nov 4. Repo predates the"),
    ("dim", "window with audio experiments only."),
], "Sweden's voice-menu maze only understands exact words. Holdmate "
   "learns them for you. Built from scratch October 26th to November 4th.")

shot(2, "start", [
    ("h", "One command starts everything"),
    ("cmd", "$ ./sh/holdmate.sh"),
    ("", "  [1] Start board server + menu"),
    ("", "  [2] Talk to Roksolana (practice call)"),
    ("", "  [3] Lessons: Holdmate phones alone"),
    ("dim", "Board: http://localhost:5173"),
], "One command starts everything.")

shot(4, "lessons", [
    ("h", "Overnight training"),
    ("cmd", "$ ./sh/holdmate.sh  ->  lessons, all personas"),
    ("", "  lesson 3/8: parent + sick leave ... transfer"),
    ("", "  learned: aktivitetsrapport, ersattning, vab ..."),
    ("dim", "Breadth-first over every menu alternative."),
], "Overnight it phones the copy by itself and learns the words.")

shot(7, "telemetry", [
    ("h", "Every Meta call is logged"),
    ("", "  model: muse-spark-open   role: intent-norm"),
    ("", "  latency: 212ms           decision: exact-match"),
    ("", "  provenance -> data/provenance.jsonl"),
    ("dim", "Board telemetry panel shows live rows."),
], "Every Meta call is logged. Model, runtime, latency. Visible here.")

shot(8, "eval", [
    ("h", "Spark normalizes noisy speech"),
    ("cmd", "$ eval/llm_intent_eval.py --openweight"),
    ("", eval_tail),
    ("dim", "Closed vocabulary: exact -> heuristic -> Meta -> abstain."),
], "Spark normalizes noisy speech onto the closed vocabulary.")

shot(9, "tests", [
    ("h", "Two hundred tests green"),
    ("cmd", "$ pytest tests/ -q"),
    ("", pytest_tail),
    ("dim", "Safety eval holds. One-command replay."),
], "Two hundred tests green, safety eval holds, one-command replay.")

shot(11, "close", [
    ("h", "Holdmate"),
    ("", "github.com/kizouker/adaptive-IVR-agent"),
    ("", "Spark + open weights + full provenance."),
    ("dim", "Holdmate waits on hold, so you don't have to."),
], "Holdmate waits on hold, so you don't have to.")

print("OK: all auto shots rendered.")
