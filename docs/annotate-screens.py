#!/usr/bin/env python3
"""Overlay big step-number badges on README screenshots.

Reads docs/images/raw/*.png (created from the plain shots on first run),
writes numbered docs/images/board-*.png. Re-runnable: badges always come
from the raw originals, never stacked.

Usage (needs Pillow in the project .venv): python3 docs/annotate-screens.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

IMAGES = Path(__file__).resolve().parent / "images"
RAW = IMAGES / "raw"
SHOTS = (
    ("board-overview.png", "1"),
    ("board-queue.png", "2"),
    ("board-lessons.png", "3"),
    ("board-pacman.png", "4"),
    ("iphone-queue.png", "5"),
)
RADIUS = 64
CENTER = (104, 104)
TEAL = (20, 184, 166)
WHITE = (255, 255, 255)
INK = (17, 24, 39)
FONTS = (
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
)


def load_font(size: int):
    for path in FONTS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def main() -> None:
    RAW.mkdir(exist_ok=True)
    font = load_font(110)
    for name, number in SHOTS:
        plain = IMAGES / name
        raw = RAW / name
        if not raw.exists():
            raw.write_bytes(plain.read_bytes())
        img = Image.open(raw).convert("RGB")
        draw = ImageDraw.Draw(img)
        x, y = CENTER
        draw.ellipse(
            [x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS],
            fill=WHITE, outline=TEAL, width=8,
        )
        draw.text((x, y - 6), number, font=font, fill=INK, anchor="mm")
        img.save(plain)
        print(f"badged {name} as {number}")


if __name__ == "__main__":
    main()
