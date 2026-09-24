#!/usr/bin/env python3
"""
Generate branded cover images (1280x720) for the four Gumroad listings.

Design: dark navy family look, per-product accent color, simple vector
motif, price badge, trust line. Output: packaging/covers/*.png

    python3 packaging/make_covers.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "covers"
OUT.mkdir(exist_ok=True)

W, H = 1280, 720
BG = (15, 23, 34)          # deep navy
PANEL = (23, 33, 48)       # slightly lighter navy
INK = (238, 242, 247)      # near-white
MUTED = (148, 163, 184)    # slate gray
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

def font(size, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(FONT_DIR + name, size)


def base_canvas():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # subtle dot grid
    for x in range(40, W, 52):
        for y in range(40, H, 52):
            d.ellipse((x, y, x + 2, y + 2), fill=(30, 41, 59))
    # brand row
    d.rounded_rectangle((56, 44, 62, 74), 3, fill=(224, 76, 63))
    d.text((74, 44), "MR T's DIY TOOLBOX", font=font(22), fill=MUTED)
    return img, d


def badge(d, xy, text, fill):
    x, y = xy
    tw = d.textlength(text, font=font(26))
    d.rounded_rectangle((x, y, x + tw + 44, y + 52), 26, fill=fill)
    d.text((x + 22, y + 11), text, font=font(26), fill=(10, 15, 22))


def footer(d, accent):
    d.text((56, H - 74), "open source (MIT)  ·  $0/month to run  ·  runs on YOUR machine",
           font=font(24, bold=False), fill=MUTED)
    d.line((56, H - 108, W - 56, H - 108), fill=(30, 41, 59), width=2)
    d.text((W - 56 - d.textlength("mrtscomputers.com", font=font(24, bold=False)),
            H - 74), "mrtscomputers.com", font=font(24, bold=False),
           fill=accent)


def title(d, lines, accent, y=120):
    for i, line in enumerate(lines):
        d.text((56, y + i * 74), line, font=font(58), fill=INK)
    d.rectangle((56, y + len(lines) * 74 + 8, 56 + 96, y + len(lines) * 74 + 14),
                fill=accent)


# ---------------------------------------------------------------- product 1
def cover_scraper():
    accent = (34, 197, 94)  # green
    img, d = base_canvas()
    title(d, ["LOCAL", "LEAD SCRAPER"], accent)
    badge(d, (56, 320), "$14.99 · one-time", accent)
    # CSV motif
    x0, y0, cw, ch = 700, 130, 180, 52
    headers = ["name", "phone", "email"]
    d.rounded_rectangle((x0 - 14, y0 - 14, x0 + 3 * cw - 66, y0 + 5 * ch),
                        12, fill=PANEL, outline=accent, width=2)
    for c, htxt in enumerate(headers):
        d.text((x0 + c * cw, y0), htxt, font=font(22), fill=accent)
    for r in range(1, 5):
        for c in range(3):
            cx, cy = x0 + c * cw, y0 + r * ch
            d.rounded_rectangle((cx, cy + 8, cx + cw - 18, cy + 40), 6,
                                fill=(32, 45, 63))
            d.ellipse((cx + 6, cy + 18, cx + 12, cy + 24), fill=accent)
    d.text((x0 - 14, y0 + 5 * ch + 18), "→  leads.csv",
           font=font(30), fill=INK)
    footer(d, accent)
    img.save(OUT / "01-lead-scraper.png")


# ---------------------------------------------------------------- product 2
def cover_outreach():
    accent = (59, 130, 246)  # blue
    img, d = base_canvas()
    title(d, ["AI OUTREACH", "PACK"], accent)
    badge(d, (56, 320), "$9.99 · one-time", accent)
    # email bubbles motif
    bx, by = 720, 120
    d.rounded_rectangle((bx, by, bx + 440, by + 90), 16, fill=PANEL,
                        outline=accent, width=2)
    d.text((bx + 24, by + 18), "Hi Riverbend Roofing —", font=font(24), fill=INK)
    d.text((bx + 24, by + 52), "one quick idea for your site…",
           font=font(24, bold=False), fill=MUTED)
    d.rounded_rectangle((bx + 60, by + 120, bx + 500, by + 210), 16,
                        fill=PANEL, outline=(72, 88, 110), width=2)
    d.text((bx + 84, by + 138), "7 prompt modes", font=font(24), fill=accent)
    d.text((bx + 84, by + 172), "local AI · drafts only · opt-out built in",
           font=font(22, bold=False), fill=MUTED)
    # sparkle
    for dx, dy, s in ((60, 40, 14), (30, 70, 9)):
        d.line((bx - dx - s, by - dy, bx - dx + s, by - dy), fill=accent, width=3)
        d.line((bx - dx, by - dy - s, bx - dx, by - dy + s), fill=accent, width=3)
    footer(d, accent)
    img.save(OUT / "02-ai-outreach-pack.png")


# ---------------------------------------------------------------- product 3
def cover_intake():
    accent = (245, 158, 11)  # amber
    img, d = base_canvas()
    title(d, ["n8n INTAKE", "BLUEPRINT"], accent)
    badge(d, (56, 320), "$19.99 · one-time", accent)
    # node-flow motif
    labels = ["Form", "Sheet", "Discord", "Email"]
    bx, by, bw, bh, gap = 720, 150, 170, 74, 46
    yc = by + bh // 2
    for i, lab in enumerate(labels):
        x = bx + i * (bw + gap)
        d.rounded_rectangle((x, by, x + bw, by + bh), 14, fill=PANEL,
                            outline=accent, width=2)
        d.ellipse((x + 14, by + 28, x + 26, by + 40), fill=accent)
        d.text((x + 38, by + 22), lab, font=font(24), fill=INK)
        if i < 3:
            ax = x + bw + 6
            d.line((ax, yc, ax + gap - 14, yc), fill=accent, width=4)
            d.polygon([(ax + gap - 14, yc - 8), (ax + gap - 14, yc + 8),
                       (ax + gap - 2, yc)], fill=accent)
    d.text((bx, by + bh + 34), "import one JSON · live in 10 minutes",
           font=font(26, bold=False), fill=MUTED)
    footer(d, accent)
    img.save(OUT / "03-n8n-intake-blueprint.png")


# ---------------------------------------------------------------- product 4
def cover_complete():
    accent = (168, 85, 247)  # purple
    img, d = base_canvas()
    title(d, ["COMPLETE", "DIY TOOLBOX"], accent)
    badge(d, (56, 320), "$29.99 · save 33%", accent)
    # three tiles motif
    tiles = [("Scraper", (34, 197, 94)), ("AI Outreach", (59, 130, 246)),
             ("Intake", (245, 158, 11))]
    tx, ty, tw, th, tg = 740, 120, 200, 96, 22
    for i, (lab, col) in enumerate(tiles):
        y = ty + i * (th + tg // 2)
        d.rounded_rectangle((tx, y, tx + tw, y + th), 14, fill=PANEL,
                            outline=col, width=3)
        d.text((tx + 20, y + 14), lab, font=font(26), fill=INK)
        d.text((tx + 20, y + 54), "included", font=font(20, bold=False),
               fill=MUTED)
    d.rounded_rectangle((tx, ty + 3 * (th + tg // 2) - 6, tx + tw + 40,
                         ty + 3 * (th + tg // 2) + 46), 14, fill=accent)
    d.text((tx + 20, ty + 3 * (th + tg // 2) + 4),
           "one download", font=font(26), fill=(10, 15, 22))
    footer(d, accent)
    img.save(OUT / "complete-toolbox.png")


if __name__ == "__main__":
    cover_scraper()
    cover_outreach()
    cover_intake()
    cover_complete()
    for p in sorted(OUT.glob("*.png")):
        print(f"  {p.name}  {p.stat().st_size // 1024} KB  ({W}x{H})")
    print("Done →", OUT)
