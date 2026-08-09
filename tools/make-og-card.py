#!/usr/bin/env python3
"""Generate assets/img/og-card.png (1200x630) for Open Graph previews.

Run by hand: python3 tools/make-og-card.py
Requires Pillow. Colours are copied from assets/css/tokens.css.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "og-card.png"

CREAM, BROWN, INK, INK2, LINE = "#FAF8F5", "#8A6A55", "#221D19", "#6B6058", "#E7DED4"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"

STAGES = ["Requirements", "Architecture", "Simulation",
          "Assurance", "Verification", "Digital twin"]

img = Image.new("RGB", (1200, 630), CREAM)
d = ImageDraw.Draw(img)

d.rounded_rectangle((72, 64, 136, 128), radius=18, fill=BROWN)
d.text((93, 76), "P", font=ImageFont.truetype(BOLD, 48), fill=CREAM)
d.text((156, 82), "Principia", font=ImageFont.truetype(BOLD, 40), fill=INK)

headline = ImageFont.truetype(BOLD, 64)
d.text((72, 200), "Change a requirement.", font=headline, fill=INK)
d.text((72, 274), "Watch it ripple to the twin.", font=headline, fill=INK)
d.text((72, 376), "SysML v2 · Modelica · GSN · CSP · Dafny · Isabelle",
       font=ImageFont.truetype(REGULAR, 29), fill=INK2)

# thread strip along the bottom
x, y, w, gap = 72, 470, 168, 12
small = ImageFont.truetype(BOLD, 18)
for i, stage in enumerate(STAGES):
    left = x + i * (w + gap)
    last = i == len(STAGES) - 1
    d.rounded_rectangle((left, y, left + w, y + 76), radius=12,
                        fill=INK if last else "#FFFFFF",
                        outline=None if last else LINE, width=2)
    if not last:
        d.rounded_rectangle((left, y, left + 5, y + 76), radius=2, fill=BROWN)
        ax = left + w + 1
        d.line((ax, y + 38, ax + gap - 2, y + 38), fill=BROWN, width=3)
    d.text((left + 18, y + 29), stage, font=small, fill=CREAM if last else INK)

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, optimize=True)
print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024}KB)")
