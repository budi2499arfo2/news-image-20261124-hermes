#!/usr/bin/env python3
"""The World in Eight — sum up 24 November 2026 in one image.

Writes one 1024x1024 PNG to /output/entry.png: an 8-panel news grid,
each panel one of the day's top stories, researched from live news
(Reuters world summary, 24 Nov 2026). Header carries the date;
footer reads "8 stories, 1 day".

Stories (all reported on 24 Nov 2026):
  01 NATO sends an AWACS early-warning jet to Poland after three
     Russian missiles landed in the country.
  02 Ukraine sinks a Russian naval corvette in a Libyan port with
     maritime drones — the war spreading beyond Europe.
  03 At least 24 dead in a candy-factory fire in Indonesia, about
     30 people still missing.
  04 COP31 climate talks collapse with no fossil-fuel deal.
  05 Western intelligence warns Russia could put a nuclear weapon
     in orbit within weeks.
  06 Jensen Huang returns as Nvidia CEO after Trump intervened;
     Nvidia's value jumps almost $1tn.
  07 Iran vows "every means" against the US naval blockade as new
     sanctions hit its shadow banking networks.
  08 Carlos Alcaraz beats Alexander Zverev in Turin for his first
     ATP Finals title.
"""

import os
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HEADER_H = 96
FOOTER_H = 64
COLS, ROWS = 2, 4
PANEL_W = W // COLS
PANEL_H = (H - HEADER_H - FOOTER_H) // ROWS

NAVY = (15, 42, 68)
INK = (30, 30, 30)
GREY = (70, 70, 70)
WHITE = (255, 255, 255)

# (strong color, light tint, headline, summary, icon kind)
STORIES = [
    ((27, 79, 114), (214, 234, 248),
     "NATO SENDS AWACS TO POLAND",
     "Three Russian missiles landed in Poland — NATO sends an early-warning jet east.",
     "radar"),
    ((146, 43, 33), (250, 219, 216),
     "UKRAINE SINKS RUSSIAN WARSHIP",
     "Maritime drones sank a Russian corvette in Libya — the war spreads beyond Europe.",
     "ship"),
    ((147, 81, 22), (253, 235, 208),
     "24 DEAD IN INDONESIA FIRE",
     "A candy-factory fire killed at least 24; rescuers search for about 30 still missing.",
     "flame"),
    ((30, 132, 73), (213, 245, 227),
     "COP31 COLLAPSES, NO DEAL",
     "Climate talks ended with no fossil-fuel deal; Pacific nations voiced despair.",
     "globe"),
    ((108, 52, 131), (232, 218, 239),
     "RUSSIA'S SPACE NUKE WARNING",
     "Western intel: Moscow could put a nuclear weapon in orbit within weeks.",
     "satellite"),
    ((17, 122, 101), (209, 242, 235),
     "HUANG RETURNS TO NVIDIA",
     "Huang is CEO again after Trump intervened; Nvidia's value jumped almost $1tn.",
     "chip"),
    ((123, 36, 28), (245, 203, 167),
     "IRAN DEFIES US BLOCKADE",
     "Tehran vows 'every means' against the US naval blockade as new sanctions hit.",
     "anchor"),
    ((125, 102, 8), (252, 243, 207),
     "ALCARAZ WINS ATP FINALS",
     "Carlos Alcaraz beat Alexander Zverev in Turin for his first ATP Finals title.",
     "trophy"),
]

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to a max pixel width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_icon(draw, kind, cx, cy, s, color):
    """Simple geometric icon centred at (cx, cy), size s, in color."""
    if kind == "radar":
        draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=4)
        draw.ellipse([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2],
                     outline=color, width=3)
        draw.line([cx, cy, cx + s, cy - s], fill=color, width=4)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=color)
    elif kind == "ship":
        draw.polygon([(cx - s, cy + s // 3), (cx + s, cy + s // 3),
                      (cx + s // 2, cy + s), (cx - s // 2, cy + s)],
                     fill=color)
        draw.line([cx, cy - s, cx, cy + s // 3], fill=color, width=4)
        draw.polygon([(cx, cy - s), (cx + s // 2, cy - s // 3), (cx, cy - s // 3)],
                     fill=color)
        draw.arc([cx - s, cy + s // 2, cx + s, cy + s + 12], 0, 180,
                 fill=color, width=3)
    elif kind == "flame":
        draw.polygon([(cx, cy - s), (cx + s // 2, cy - s // 4),
                      (cx + s, cy + s // 2), (cx + s // 2, cy + s),
                      (cx - s // 2, cy + s), (cx - s, cy + s // 2),
                      (cx - s // 2, cy - s // 4)], fill=color)
        # Inner flame in a lighter tone for a readable flame shape.
        draw.polygon([(cx, cy - s // 3), (cx + s // 3, cy + s // 4),
                      (cx, cy + s // 2), (cx - s // 3, cy + s // 4)],
                     fill=(252, 243, 207))
    elif kind == "globe":
        draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=4)
        draw.line([cx - s, cy, cx + s, cy], fill=color, width=3)
        draw.line([cx, cy - s, cx, cy + s], fill=color, width=3)
        draw.line([cx - s, cy - s // 2, cx + s, cy + s // 2], fill=color, width=3)
    elif kind == "satellite":
        draw.rectangle([cx - s // 2, cy - s // 3, cx + s // 2, cy + s // 3],
                       fill=color)
        draw.rectangle([cx - s, cy - s // 4, cx - s // 2, cy + s // 4],
                       outline=color, width=3)
        draw.rectangle([cx + s // 2, cy - s // 4, cx + s, cy + s // 4],
                       outline=color, width=3)
        draw.ellipse([cx - s - 6, cy - s - 6, cx + s + 6, cy + s + 6],
                     outline=color, width=2)
    elif kind == "chip":
        draw.rectangle([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2],
                       fill=color)
        draw.rectangle([cx - s // 4, cy - s // 4, cx + s // 4, cy + s // 4],
                       fill=WHITE)
        for dx in (-s // 4, 0, s // 4):
            draw.line([cx + dx, cy - s, cx + dx, cy - s // 2], fill=color, width=3)
            draw.line([cx + dx, cy + s // 2, cx + dx, cy + s], fill=color, width=3)
            draw.line([cx - s, cy + dx, cx - s // 2, cy + dx], fill=color, width=3)
            draw.line([cx + s // 2, cy + dx, cx + s, cy + dx], fill=color, width=3)
    elif kind == "anchor":
        draw.line([cx, cy - s, cx, cy + s], fill=color, width=5)
        draw.ellipse([cx - s // 3, cy - s, cx + s // 3, cy - s // 3],
                     outline=color, width=4)
        draw.arc([cx - s // 2, cy, cx + s // 2, cy + s], 0, 180,
                 fill=color, width=5)
        draw.line([cx - s // 2, cy - s // 4, cx + s // 2, cy - s // 4],
                  fill=color, width=5)
    elif kind == "trophy":
        draw.polygon([(cx - s // 2, cy - s), (cx + s // 2, cy - s),
                      (cx + s // 3, cy + s // 3), (cx - s // 3, cy + s // 3)],
                     fill=color)
        draw.arc([cx - s, cy - s, cx - s // 4, cy - s // 4], 90, 270,
                 fill=color, width=4)
        draw.arc([cx + s // 4, cy - s, cx + s, cy - s // 4], -90, 90,
                 fill=color, width=4)
        draw.line([cx, cy + s // 3, cx, cy + s // 2], fill=color, width=5)
        draw.line([cx - s // 2, cy + s // 2, cx + s // 2, cy + s // 2],
                  fill=color, width=5)


def build(path):
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # Header bar.
    draw.rectangle([0, 0, W, HEADER_H], fill=NAVY)
    f_title = font("DejaVuSans-Bold.ttf", 46)
    f_date = font("DejaVuSans-Bold.ttf", 20)
    draw.text((24, 22), "THE WORLD IN EIGHT", font=f_title, fill=WHITE)
    date = "TUESDAY, 24 NOVEMBER 2026"
    dw = draw.textlength(date, font=f_date)
    draw.text((W - 24 - dw, 36), date, font=f_date, fill=(180, 210, 235))

    f_num = font("DejaVuSans-Bold.ttf", 44)
    f_head = font("DejaVuSans-Bold.ttf", 25)
    f_sum = font("DejaVuSans.ttf", 19)

    for i, (strong, tint, headline, summary, icon) in enumerate(STORIES):
        r, c = divmod(i, COLS)
        x0, y0 = c * PANEL_W, HEADER_H + r * PANEL_H
        draw.rectangle([x0, y0, x0 + PANEL_W, y0 + PANEL_H], fill=tint)
        # Left accent bar + thin grid lines.
        draw.rectangle([x0, y0, x0 + 10, y0 + PANEL_H], fill=strong)
        draw.line([x0, y0 + PANEL_H - 1, x0 + PANEL_W, y0 + PANEL_H - 1],
                  fill=(200, 200, 200), width=1)
        if c == 1:
            draw.line([x0, y0, x0, y0 + PANEL_H], fill=(200, 200, 200), width=1)

        tx = x0 + 28
        ty = y0 + 18
        # Big number.
        draw.text((tx, ty), f"{i + 1:02d}", font=f_num, fill=strong)
        # Icon top-right.
        draw_icon(draw, icon, x0 + PANEL_W - 52, y0 + 46, 26, strong)
        # Headline (max 2 lines).
        head_lines = wrap(draw, headline, f_head, PANEL_W - 130)[:2]
        hy = ty + 58
        for line in head_lines:
            draw.text((tx, hy), line, font=f_head, fill=INK)
            hy += 30
        # Summary (max 3 lines).
        sum_lines = wrap(draw, summary, f_sum, PANEL_W - 56)[:3]
        sy = hy + 6
        for line in sum_lines:
            draw.text((tx, sy), line, font=f_sum, fill=GREY)
            sy += 24

    # Footer bar.
    draw.rectangle([0, H - FOOTER_H, W, H], fill=NAVY)
    f_foot = font("DejaVuSans-Bold.ttf", 24)
    foot = "8 STORIES, 1 DAY"
    fw = draw.textlength(foot, font=f_foot)
    draw.text(((W - fw) / 2, H - FOOTER_H + 18), foot, font=f_foot, fill=WHITE)

    img.save(path, "PNG")
    return path


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    build(path)
    # Verify the gate: PNG, <=1024x1024, <=1 MiB.
    with Image.open(path) as im:
        if im.format != "PNG":
            print("entry.png is not PNG", file=sys.stderr)
            return 1
        if im.size[0] > 1024 or im.size[1] > 1024:
            print(f"entry.png too big: {im.size}", file=sys.stderr)
            return 1
    size = os.path.getsize(path)
    if size > 1024 * 1024:
        print(f"entry.png over 1 MiB: {size} bytes", file=sys.stderr)
        return 1
    print(f"wrote entry.png (1024x1024, {size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
