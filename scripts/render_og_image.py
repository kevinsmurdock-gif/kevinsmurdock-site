#!/usr/bin/env python3
"""Render the typographic social card for kevinsmurdock.com.

Provenance: generated from the site's own name, role, and city. It is not a
photograph, portrait, or credential. No outside image is embedded.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "og-image.png"

NAVY = (13, 27, 42)
CREAM = (246, 241, 232)
GOLD = (230, 195, 106)

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def main() -> None:
    image = Image.new("RGB", (1200, 630), NAVY)
    draw = ImageDraw.Draw(image)
    draw.rectangle((72, 168, 168, 174), fill=GOLD)
    name = ImageFont.truetype(SERIF, 84)
    role = ImageFont.truetype(SANS, 36)
    place = ImageFont.truetype(SANS, 32)
    draw.text((72, 210), "Kevin S. Murdock", font=name, fill=CREAM)
    draw.text((72, 330), "Healthcare entrepreneur", font=role, fill=GOLD)
    draw.text((72, 386), "Greenville, South Carolina", font=place, fill=CREAM)
    image.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
