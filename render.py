#!/usr/bin/env python3
"""render.py — THE SATURDAY GAZETTE (news-image-20261121).

Build-time only renderer (PIL allowed here). Rebuilds entry.png from the
spec in RESEARCH.md + REFRESH-RESULT.md: Saturday 21 November 2026, 38
stories. Layout follows the v1 broadsheet (masthead, 3 lead banners,
12 illustrated tiles, world-map band, 24-item ALSO, sources footer).

Three Saturday-night outcomes are applied (REFRESH-RESULT.md):
  1. BepiColombo ARRIVED in orbit (was "due tonight").
  2. Verstappen WON the Las Vegas GP (was a qualifying tile).
  3. Bitcoin daily candle finalised: low $55,130, close $57,884.
Everything else keeps its v1 wording exactly.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BASE = "/home/hatch/workspace/makefun/news-image-20261121"

CREAM = (242, 232, 208)
PAPER = (247, 240, 222)
INK = (25, 25, 25)
NAVY = (29, 42, 68)
NAVY_DK = (20, 30, 52)
RED = (179, 39, 46)
RED_DK = (140, 28, 34)
TAN = (217, 196, 154)
GOLD = (201, 162, 39)
GOLD_LT = (226, 196, 110)
GREEN = (74, 107, 58)
OLIVE = (122, 122, 58)
BROWN = (107, 74, 47)
GRAY = (110, 105, 95)
WHITE = (250, 248, 242)

SERIF = BASE + "/fonts/DejaVuSerif-Bold.ttf"
SANS = BASE + "/fonts/DejaVuSans.ttf"
SANSB = BASE + "/fonts/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def stamp(text, size, color=RED):
    """A small rotated rubber-stamp label (RGBA)."""
    f = F(SANSB, size)
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    tw = int(d.textlength(text, font=f)) + 16
    th = size + 12
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 2, tw - 3, th - 3], outline=color + (255,), width=3)
    d.text((8, 5), text, font=f, fill=color + (255,))
    return img.rotate(-8, expand=True, resample=Image.BICUBIC)


def paste_stamp(base, st, x, y):
    base.paste(st, (x, y), st)


# ---------------------------------------------------------------- canvas
img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)
random.seed(21)

# subtle warm paper variation: faint horizontal banding, like newsprint
for y in range(0, H, 4):
    shade = random.randint(-3, 3)
    d.line([(0, y), (W, y)], fill=(CREAM[0] + shade, CREAM[1] + shade, CREAM[2] + shade))

M = 12
CW = W - 2 * M

# ---------------------------------------------------------------- masthead
f_title = F(SERIF, 54)
d.text((W // 2, 6), "THE SATURDAY GAZETTE", font=f_title, fill=INK, anchor="ma")
d.line([(M, 66), (W - M, 66)], fill=INK, width=2)
f_date = F(SANSB, 15)
d.text((M, 72), "SATURDAY 21 NOVEMBER 2026", font=f_date, fill=INK)
d.text((W - M, 72), "38 STORIES \u2022 5 CONTINENTS", font=f_date, fill=RED, anchor="ra")

# ---------------------------------------------------------------- leads
LEAD_Y, LEAD_H = 92, 186
LEAD_W = (CW - 16) // 3
LEAD_X = [M, M + LEAD_W + 8, M + 2 * (LEAD_W + 8)]


def lead(i, kicker, kicker_bg, draw_image, headline, subs, source):
    x = LEAD_X[i]
    y = LEAD_Y
    d.rectangle([x, y, x + LEAD_W, y + LEAD_H], outline=INK, width=1)
    d.rectangle([x, y, x + LEAD_W, y + 20], fill=kicker_bg)
    d.text((x + 8, y + 4), kicker, font=F(SANSB, 12), fill=WHITE)
    draw_image(x + 1, y + 21, LEAD_W - 2, 74)
    hy = y + 96
    f_h = F(SERIF, 21)
    lines = wrap(d, headline, f_h, LEAD_W - 14)
    for ln in lines[:2]:
        d.text((x + 7, hy), ln, font=f_h, fill=INK)
        hy += 24
    f_s = F(SANS, 12)
    for s in subs:
        d.text((x + 7, hy), s, font=f_s, fill=(60, 58, 52))
        hy += 14
    d.text((x + LEAD_W - 7, y + LEAD_H - 2), source, font=F(SANS, 9),
           fill=GRAY, anchor="rs")


def lead1_image(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(203, 178, 128))
    # conference hall: rows of seats
    for r in range(3):
        yy = y + 10 + r * 20
        for c in range(9):
            xx = x + 14 + c * 34 + (r % 2) * 8
            d.ellipse([xx, yy, xx + 16, yy + 10], fill=(58, 44, 30))
            d.rectangle([xx + 2, yy + 10, xx + 14, yy + 14], fill=(58, 44, 30))
    # red FAILURE banner across the hall
    d.rectangle([x + 40, y + 26, x + w - 40, y + 48], fill=RED)
    d.text((x + w // 2, y + 29), "FAILURE", font=F(SANSB, 15), fill=WHITE, anchor="ma")
    # draft box
    d.rectangle([x + 8, y + h - 26, x + 108, y + h - 4], fill=WHITE, outline=INK)
    d.text((x + 58, y + h - 25), "144 \u2192 80", font=F(SANSB, 12), fill=RED, anchor="ma")
    d.text((x + 58, y + h - 12), "0 fossil mentions", font=F(SANS, 8), fill=INK, anchor="ma")


def lead2_image(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_DK)
    # y scale: $54,000 bottom, $61,000 top
    def py(price):
        return y + h - 8 - (price - 54000) / 7000.0 * (h - 16)

    # dashed $60,000 line
    yy = py(60000)
    for xx in range(x + 4, x + w - 4, 8):
        d.line([(xx, yy), (xx + 4, yy)], fill=(150, 160, 190), width=1)
    d.text((x + 6, y + 4), "$60,000", font=F(SANS, 9), fill=(170, 180, 205))
    d.text((x + 6, y + h - 13), "$55,000", font=F(SANS, 9), fill=(170, 180, 205))
    # falling line: open high, crash to the low, recover to the close
    pts = [(x + 6, py(59900)), (x + w * 0.30, py(58900)),
           (x + w * 0.52, py(57100)), (x + w * 0.68, py(55130)),
           (x + w * 0.86, py(56800)), (x + w - 8, py(57884))]
    d.line(pts, fill=(235, 70, 70), width=3, joint="curve")
    lx, ly = x + w * 0.68, py(55130)
    d.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], fill=(235, 70, 70), outline=WHITE)
    d.text((lx + 8, ly - 6), "LOW $55,130", font=F(SANSB, 10), fill=(255, 120, 120))
    ex, ey = x + w - 8, py(57884)
    d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=GOLD_LT, outline=WHITE)
    d.text((ex - 92, ey - 18), "CLOSE $57,884", font=F(SANSB, 10), fill=GOLD_LT)


def lead3_image(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 16, 34))
    for _ in range(26):
        sx = random.randint(x + 4, x + w - 4)
        sy = random.randint(y + 4, y + h - 4)
        r = random.choice([1, 1, 2])
        d.ellipse([sx, sy, sx + r, sy + r], fill=(220, 225, 240))
    # Mercury, big, right side
    mx, my, mr = x + w - 52, y + h // 2, 30
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(196, 178, 150))
    for (cx, cy, cr) in [(-12, -8, 7), (6, 10, 5), (12, -12, 4), (-4, 14, 3), (14, 2, 3)]:
        d.ellipse([mx + cx - cr, my + cy - cr, mx + cx + cr, my + cy + cr],
                  fill=(168, 148, 120))
    # spacecraft, left
    bx, by = x + 34, y + h // 2 + 2
    d.rectangle([bx - 16, by - 5, bx - 6, by + 5], fill=(90, 110, 160))
    d.rectangle([bx + 6, by - 5, bx + 16, by + 5], fill=(90, 110, 160))
    d.ellipse([bx - 7, by - 8, bx + 7, by + 8], fill=GOLD_LT, outline=WHITE)
    d.polygon([(bx - 22, by - 3), (bx - 32, by - 8), (bx - 32, by + 8)],
              fill=(255, 140, 40))
    d.text((x + 8, y + 5), "19:24 CET", font=F(SANSB, 16), fill=GOLD_LT)
    d.text((x + 8, y + 25), "BURN: 37 MIN \u00b7 ORBIT 590 \u00d7 11,640 KM",
           font=F(SANS, 9), fill=WHITE)
    st = stamp("IN ORBIT", 13)
    paste_stamp(img, st, x + w - 108, y + h - 34)


lead(0, "LEAD 1 \u00b7 CLIMATE \u00b7 ANTALYA", NAVY, lead1_image,
     "COP31: NO DEAL \u2014 TALKS INTO OVERTIME",
     ["Draft cut 144 \u2192 80 \u00b7 0 fossil mentions"], "AP \u00b7 REUTERS")
lead(1, "LEAD 2 \u00b7 MARKETS \u00b7 CRYPTO", RED_DK, lead2_image,
     "BITCOIN CRASHES BELOW $56,000",
     ["Low $55,130 \u2014 lowest since Sep 2024",
      "Closed Sat $57,884 \u00b7 Fear & Greed 12"], "FINNHUB \u00b7 REUTERS")
lead(2, "LEAD 3 \u00b7 SPACE \u00b7 MERCURY", NAVY, lead3_image,
     "BEPICOLOMBO ARRIVES AT MERCURY",
     ["8-year voyage ends in orbit",
      "Only the 2nd craft ever to orbit Mercury"], "ESA \u00b7 JAXA")

# ---------------------------------------------------------------- tiles
TILE_W = (CW - 24) // 4
TILE_X = [M, M + TILE_W + 8, M + 2 * (TILE_W + 8), M + 3 * (TILE_W + 8)]
TILE_Y = [284, 400, 516]
TILE_H = 108
IMG_H = 46


def tile(col, row, draw_image, headline, sub, source, kicker=None):
    x = TILE_X[col]
    y = TILE_Y[row]
    d.rectangle([x, y, x + TILE_W, y + TILE_H], outline=INK, width=1)
    draw_image(x + 1, y + 1, TILE_W - 2, IMG_H)
    if kicker:
        # small black label, top-left inside the picture strip
        f_k = F(SANSB, 10)
        tw = int(d.textlength(kicker, font=f_k)) + 10
        d.rectangle([x + 1, y + 1, x + 1 + tw, y + 15], fill=(15, 15, 15))
        d.text((x + 6, y + 3), kicker, font=f_k, fill=WHITE)
    hy = y + IMG_H + 5
    f_h = F(SERIF, 14)
    for ln in wrap(d, headline, f_h, TILE_W - 12)[:2]:
        d.text((x + 6, hy), ln, font=f_h, fill=INK)
        hy += 16
    d.text((x + 6, hy + 1), sub, font=F(SANS, 11), fill=(60, 58, 52))
    d.text((x + TILE_W - 6, y + TILE_H - 12), source, font=F(SANS, 8),
           fill=GRAY, anchor="ra")


def img_wallstreet(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_DK)
    pts = [(x + 4, y + 10), (x + w * 0.3, y + 14), (x + w * 0.55, y + 22),
           (x + w * 0.8, y + 34), (x + w - 5, y + 40)]
    d.line(pts, fill=(235, 70, 70), width=2, joint="curve")
    d.ellipse([x + w - 8, y + 37, x + w - 2, y + 43], fill=(235, 70, 70))
    d.text((x + w - 6, y + 3), "FRI 20 NOV CLOSE", font=F(SANSB, 9),
           fill=(255, 120, 120), anchor="ra")


def img_f1(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 24, 30))
    # kicker band: full literal kicker, gold on dark
    d.rectangle([x, y, x + w, y + 16], fill=(15, 15, 15))
    d.text((x + 6, y + 3), "LAS VEGAS \u00b7 WINNER: VERSTAPPEN",
           font=F(SANSB, 11), fill=GOLD_LT)
    # chequered flag, top-right below the band
    for r in range(2):
        for c in range(5):
            if (r + c) % 2 == 0:
                d.rectangle([x + w - 42 + c * 8, y + 19 + r * 7,
                             x + w - 34 + c * 8, y + 26 + r * 7], fill=WHITE)
    # red F1 car silhouette
    cy = y + 32
    d.rectangle([x + 30, cy - 3, x + 150, cy + 3], fill=RED)          # body
    d.polygon([(x + 150, cy - 3), (x + 185, cy - 1), (x + 185, cy + 3),
               (x + 150, cy + 3)], fill=RED)                          # nose
    d.rectangle([x + 22, cy - 10, x + 34, cy + 2], fill=RED)          # rear wing
    d.rectangle([x + 95, cy - 9, x + 115, cy - 3], fill=RED)          # cockpit
    for wx in (52, 168):
        d.ellipse([x + wx - 9, cy - 2, x + wx + 9, cy + 14], fill=(10, 10, 10),
                  outline=(120, 120, 120))
        d.ellipse([x + wx - 3, cy + 3, x + wx + 3, cy + 9], fill=(160, 160, 160))
    d.line([(x + 8, cy + 15), (x + w - 8, cy + 15)], fill=(90, 90, 90), width=2)


def img_cricket(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=GREEN)
    for sx in (14, 24, 34):
        d.rectangle([x + sx, y + 10, x + sx + 5, y + 34], fill=(226, 196, 110))
    d.text((x + 100, y + 4), "486/4", font=F(SERIF, 26), fill=WHITE)
    d.text((x + 100, y + 30), "LEAD BY 118", font=F(SANSB, 11), fill=GOLD_LT)
    d.ellipse([x + w - 16, y + 8, x + w - 6, y + 18], fill=(179, 39, 46),
              outline=WHITE)


def img_huawei(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(32, 34, 44))
    for cx in (30, 70, 110):
        d.rectangle([x + cx, y + 6, x + cx + 12, y + h - 6], fill=(150, 148, 140))
    d.rectangle([x + 8, y + 4, x + w - 8, y + 10], fill=(150, 148, 140))
    st = stamp("STILL OUT", 12)
    paste_stamp(img, st, x + w - 118, y + h - 30)


def img_rikers(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 40, 52))
    for bx in range(8, w, 18):
        d.rectangle([x + bx, y, x + bx + 7, y + h], fill=(120, 118, 112))
    d.rectangle([x, y + h // 2 - 3, x + w, y + h // 2 + 3], fill=(90, 88, 82))


def img_denmark(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(160, 36, 40))
    d.text((x + 10, y + 17), "EXPELLED", font=F(SANSB, 16), fill=WHITE)
    d.rectangle([x + 10, y + 32, x + 118, y + 43], fill=WHITE)
    d.text((x + 64, y + 34), "1 DIPLOMAT", font=F(SANSB, 10), fill=RED_DK,
           anchor="ma")


def img_zelensky(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 230, 215))
    d.rectangle([x + 10, y + 17, x + w // 2 - 4, y + h - 1], fill=WHITE,
                outline=NAVY)
    d.text((x + w // 4, y + 20), "\u201cFRIEND\u201d", font=F(SERIF, 14), fill=NAVY,
           anchor="ma")
    d.text((x + w // 4, y + 34), "\u2014 TRUMP", font=F(SANSB, 8), fill=NAVY,
           anchor="ma")
    d.rectangle([x + w // 2 + 4, y + 17, x + w - 10, y + h - 1], fill=RED)
    d.text((x + 3 * w // 4, y + 20), "\u201cKILLER\u201d", font=F(SERIF, 14),
           fill=WHITE, anchor="ma")
    d.text((x + 3 * w // 4, y + 34), "\u2014 ZELENSKY", font=F(SANSB, 8),
           fill=WHITE, anchor="ma")


def img_cyber(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # gold shield (small, left) — text well clear of it
    cx, cy = x + 30, y + h // 2
    d.polygon([(cx, cy - 14), (cx + 12, cy - 9), (cx + 10, cy + 7),
               (cx, cy + 15), (cx - 10, cy + 7), (cx - 12, cy - 9)],
              fill=GOLD, outline=GOLD_LT)
    d.text((cx, cy - 8), "\u2605", font=F(SANSB, 12), fill=NAVY, anchor="ma")
    d.text((x + 80, y + 18), "CYBER CHIEF", font=F(SANSB, 13), fill=GOLD_LT)
    d.text((x + 80, y + 32), "FIRED", font=F(SANSB, 13), fill=(255, 120, 120))


def img_anc(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=GREEN)
    d.rectangle([x + 10, y + 8, x + 40, y + 38], fill=(226, 196, 110),
                outline=INK)
    d.rectangle([x + 18, y + 4, x + 32, y + 9], fill=WHITE, outline=INK)
    d.text((x + 25, y + 14), "\u2713", font=F(SANSB, 16), fill=GREEN, anchor="ma")
    d.text((x + 48, y + 17), "KEY CITIES", font=F(SANSB, 13), fill=WHITE)
    d.text((x + 48, y + 31), "AT STAKE", font=F(SANSB, 13), fill=GOLD_LT)


def img_811m(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=BROWN)
    d.text((x + 8, y + 18), "$811M", font=F(SERIF, 22), fill=GOLD_LT)
    d.text((x + 118, y + 20), "FINED", font=F(SANSB, 14), fill=WHITE)
    d.text((x + 118, y + 35), "SCAM ROLLS ON", font=F(SANSB, 9), fill=WHITE)


def img_kharg(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 28, 50))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(40, 70, 110))
    for tx, tw in ((14, 66), (92, 58), (158, 62)):
        d.rectangle([x + tx, y + 18, x + tx + tw, y + 30], fill=(179, 39, 46))
        d.rectangle([x + tx + tw // 2 - 2, y + 8, x + tx + tw // 2 + 2, y + 18],
                    fill=(179, 39, 46))
    st = stamp("UNVERIFIED", 10)
    paste_stamp(img, st, x + w - 112, y + 2)


def img_roundup(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=OLIVE)
    for nx in (30, 70, 110, 150, 190):
        d.line([(x + nx, y + 8), (x + nx, y + 18)], fill=GOLD_LT, width=3)
        d.ellipse([x + nx - 3, y + 18, x + nx + 3, y + 24], fill=GOLD_LT)
    d.text((x + w // 2, y + 22), "$7.25BN", font=F(SERIF, 20), fill=WHITE,
           anchor="ma")


tile(0, 0, img_wallstreet, "WALL STREET ROUT",
     "S&P \u22123.7% into correction \u00b7 Nasdaq \u22125.3%", "INVESTOPEDIA",
     kicker="NEW YORK")
tile(1, 0, img_f1, "VERSTAPPEN WINS LAS VEGAS GP",
     "Norris 2nd +0.639 \u00b7 Piastri 3rd +1.529", "THE RACE")
tile(2, 0, img_cricket, "INDIA 486/4, LEAD BY 118",
     "Rahul 136 \u2014 first Test ton in New Zealand", "SPORTRADAR",
     kicker="WELLINGTON")
tile(3, 0, img_huawei, "HUAWEI JURY STILL OUT",
     "Day 3 of deliberations \u2014 no verdict yet", "REUTERS",
     kicker="BROOKLYN")
tile(0, 1, img_rikers, "RIKERS ISLAND TO CLOSE BY 2032",
     "Mayor Mamdani announces the plan", "BBC", kicker="NEW YORK")
tile(1, 1, img_denmark, "DENMARK: RUSSIA PLOTTED TO KILL RAPPER",
     "Russian diplomat expelled", "AL JAZEERA", kicker="COPENHAGEN")
tile(2, 1, img_zelensky, "ZELENSKY CALLS PUTIN A \u201cKILLER\u201d",
     "After Trump called him a friend", "BBC", kicker="KYIV")
tile(3, 1, img_cyber, "WHITE HOUSE FIRES CYBER CHIEF",
     "Sean Cairncross out after tech outages", "BBC", kicker="WASHINGTON")
tile(0, 2, img_anc, "ANC FIGHTS TO HOLD KEY CITIES",
     "After election setbacks", "BBC", kicker="SOUTH AFRICA")
tile(1, 2, img_811m, "FINED $811M FOR SCAMMING MIGRANTS",
     "But the scam did not stop", "BBC", kicker="USA")
tile(2, 2, img_kharg, "TANKERS MASS AT KHARG ISLAND",
     "Iranian-flagged tankers gather", "DAILY BRIEF", kicker="KHARG, IRAN")
tile(3, 2, img_roundup, "$7.25BN ROUNDUP DEAL APPROVED",
     "Judge approves cancer-claims settlement", "BBC", kicker="USA")

# ---------------------------------------------------------------- map band
MAP_Y, MAP_H = 640, 140
d.rectangle([M, MAP_Y, W - M, MAP_Y + MAP_H], fill=NAVY)
d.text((M + 8, MAP_Y + 6), "WHERE IT HAPPENED", font=F(SANSB, 14), fill=WHITE)
d.text((W - M - 8, MAP_Y + 8),
       "EUROPE 5 \u00b7 ASIA 2 \u00b7 N. AMERICA 3 \u00b7 OCEANIA 1 \u00b7 SPACE 1",
       font=F(SANSB, 10), fill=GOLD_LT, anchor="ra")

MAP_X0, MAP_X1 = M + 8, W - M - 8
MAP_TOP, MAP_BOT = MAP_Y + 28, MAP_Y + MAP_H - 6


def proj(lon, lat):
    x = MAP_X0 + (lon + 168) / 360.0 * (MAP_X1 - MAP_X0)
    y = MAP_TOP + (80 - lat) / 140.0 * (MAP_BOT - MAP_TOP)
    return (x, y)


def poly(points, fill=TAN):
    d.polygon([proj(lon, lat) for lon, lat in points], fill=fill)


# rough equirectangular continents
poly([(-168, 66), (-140, 70), (-125, 71), (-110, 73), (-95, 80), (-85, 70),
      (-80, 73), (-75, 72), (-65, 60), (-55, 47), (-60, 45), (-70, 42),
      (-75, 35), (-80, 32), (-85, 29), (-90, 21), (-95, 19), (-100, 17),
      (-105, 20), (-110, 23), (-115, 29), (-120, 34), (-125, 40),
      (-125, 49), (-130, 55), (-140, 60), (-155, 58), (-165, 60)])
poly([(-80, 10), (-75, 5), (-80, -5), (-80, -15), (-70, -18), (-60, -25),
      (-55, -35), (-65, -45), (-70, -52), (-72, -40), (-75, -30),
      (-80, -20), (-78, -10)])
poly([(-10, 36), (-5, 44), (0, 46), (5, 50), (8, 55), (10, 58), (18, 60),
      (25, 65), (30, 70), (35, 68), (40, 60), (35, 55), (30, 50), (28, 45),
      (25, 40), (20, 38), (15, 40), (10, 38), (5, 36), (0, 36)])
poly([(-10, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (40, 20),
      (45, 11), (50, 10), (48, 0), (40, -10), (35, -20), (30, -30),
      (20, -35), (15, -30), (12, -18), (10, -5), (5, 5), (-5, 5),
      (-10, 15), (-15, 25)])
poly([(40, 70), (60, 72), (80, 73), (100, 76), (120, 73), (140, 72),
      (160, 70), (170, 66), (160, 60), (150, 59), (140, 55), (135, 45),
      (130, 40), (127, 35), (122, 30), (120, 25), (115, 20), (110, 15),
      (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 15),
      (77, 8), (75, 12), (72, 20), (68, 25), (62, 25), (58, 26), (55, 26),
      (50, 29), (48, 30), (45, 25), (42, 20), (40, 15), (38, 12),
      (35, 15), (40, 30), (38, 35), (35, 40), (40, 45), (42, 55), (45, 65)])
poly([(113, -22), (114, -30), (120, -34), (130, -32), (137, -35),
      (142, -38), (148, -38), (150, -35), (153, -27), (150, -22),
      (146, -19), (142, -15), (137, -12), (132, -12), (130, -13),
      (126, -14), (122, -17), (118, -20)])
poly([(-4, 58), (-2, 58), (1, 57), (1, 52), (-3, 51), (-5, 53)])  # UK
poly([(130, 45), (132, 44), (135, 42), (138, 38), (140, 36), (141, 34),
      (140, 32), (138, 33), (134, 36), (131, 40), (129, 43)])  # Japan

PINS = [
    (1, 30.7, 36.9, 0, 0),      # Antalya
    (2, -74.0, 40.7, 0, 0),     # New York
    (3, -115.1, 36.2, 0, 0),    # Las Vegas
    (4, 174.8, -41.3, 0, 0),    # Wellington
    (5, -73.95, 40.65, 11, 9),  # Brooklyn (nudged off New York)
    (6, 12.57, 55.68, 0, -5),   # Copenhagen
    (7, 30.52, 50.45, 0, 0),    # Kyiv
    (8, -0.13, 51.5, 0, 6),     # London
    (9, 84.92, 19.26, 0, 0),    # Odisha
    (10, 50.32, 29.25, 0, 0),   # Kharg
    (11, 4.32, 52.07, 0, 11),   # The Hague
]
for num, lon, lat, dx, dy in PINS:
    px, py = proj(lon, lat)
    px += dx
    py += dy
    d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=WHITE, width=2)
    d.text((px, py - 1), str(num), font=F(SANSB, 9), fill=WHITE, anchor="mm")
# pin 12: Mercury, off the map at top-right
px12, py12 = MAP_X1 - 14, MAP_Y + 40
d.ellipse([px12 - 7, py12 - 7, px12 + 7, py12 + 7], fill=RED, outline=WHITE,
          width=2)
d.text((px12, py12 - 1), "12", font=F(SANSB, 9), fill=WHITE, anchor="mm")
d.text((px12 - 14, py12 - 2), "MERCURY", font=F(SANSB, 9), fill=GOLD_LT,
       anchor="rm")

d.text((W // 2, MAP_Y + MAP_H + 5),
       "1 ANTALYA \u00b7 2 NEW YORK \u00b7 3 LAS VEGAS \u00b7 4 WELLINGTON \u00b7 "
       "5 BROOKLYN \u00b7 6 COPENHAGEN \u00b7 7 KYIV \u00b7 8 LONDON \u00b7 "
       "9 ODISHA \u00b7 10 KHARG \u00b7 11 THE HAGUE \u00b7 12 MERCURY",
       font=F(SANS, 9), fill=INK, anchor="ma")

# ---------------------------------------------------------------- ALSO
ALSO_Y = 800
d.text((M, ALSO_Y), "ALSO", font=F(SANSB, 14), fill=INK)
d.line([(M + 52, ALSO_Y + 9), (W - M, ALSO_Y + 9)], fill=INK, width=1)

ALSO_L = [
    ("RUSSIA'S BIGGEST STRIKE ON UKRAINE", " \u2014 9 killed, 3 Kyiv bridges hit"),
    ("RUSSIA'S MISSILE LANDS IN POLAND", " \u2014 Tusk: \u201cdeliberate provocation\u201d"),
    ("TRUMP'S 90-MIN PRESSER", " \u2014 hails Asia trip, \u201cvery good talks\u201d with Putin"),
    ("GTA VI OFFICIAL: $3.79BN DAY ONE", " \u2014 32.5M copies, biggest launch ever"),
    ("UK\u2013EU DEAL AGREED", " \u2014 but tuition-fee row holds up implementation"),
    ("ANTHROPIC ANT DAY 2", " \u2014 closes $88.91, down 8.5%"),
    ("CYCLONE AKVAN LANDFALL DONE", " \u2014 zero deaths, 372,000 evacuated"),
    ("ICJ: MYANMAR GUILTY OF GENOCIDE, 9\u20136", " \u2014 first state ever found guilty"),
    ("IRAQI FORCES ENTER KATAIB HEZBOLLAH HQ", " \u2014 after 12 years"),
    ("US AI CHIP CURBS HIT CHINESE TECH", " \u2014 Z.AI \u221222%, MiniMax \u221234%"),
    ("UK SECRET CYBER OP SECURES TENS OF THOUSANDS OF FRIDGES", ""),
    ("PANCREATIC CANCER PILL", " \u2014 tumours gone in 1 of 12 patients"),
]
ALSO_R = [
    ("SYDNEY CAR-BOMB PLOT", " \u2014 3 arrested after 10 raids"),
    ("HIPPO FIONA DIES", " \u2014 swallowed a visitor's hat; zoo: removal \u201cimpossible\u201d"),
    ("CANADA COURTS AI DATA CENTRES", " \u2014 as US voters say no"),
    ("OIL CLOSES FRIDAY", " \u2014 Brent $92.57, WTI $83.98"),
    ("SAUDI\u2013HOUTHI ESCALATION", " \u2014 3 missiles intercepted over Riyadh"),
    ("TRUMP PARDONS PETE ROSE", " \u2014 posthumously, 4,256 career hits"),
    ("TRILATERAL PEACE DECLARATION", " \u2014 4 points, no Ukraine deal"),
    ("LAUREN PRICE UNDISPUTED WELTERWEIGHT CHAMPION", ""),
    ("NEPAL PM SHAH MEETS MODI", " \u2014 first foreign trip"),
    ("DEAD PETS MEANT FOR CREMATION FOUND ON LIVESTREAM", " \u2014 Philippines"),
    ("UK ANNOUNCES \u00a3260M DRONE PACKAGE FOR UKRAINE", " \u2014 1,000+ drones"),
]


def also_col(items, x0, y0):
    f_b = F(SANSB, 11)
    f_r = F(SANS, 11)
    y = y0
    for bold, rest in items:
        d.text((x0, y), "\u2022", font=f_r, fill=RED)
        d.text((x0 + 10, y), bold, font=f_b, fill=INK)
        bx = x0 + 10 + d.textlength(bold, font=f_b)
        d.text((bx, y), rest, font=f_r, fill=(60, 58, 52))
        y += 13
    return y


also_col(ALSO_L, M, ALSO_Y + 16)
also_col(ALSO_R, M + 512, ALSO_Y + 16)

# ---------------------------------------------------------------- footer
d.line([(M, 978), (W - M, 978)], fill=INK, width=1)
d.text((W // 2, 984),
       "SOURCES: BBC \u00b7 REUTERS \u00b7 CHANNEL NEWS ASIA \u00b7 BLOOMBERG \u00b7 "
       "MKT NEWS \u00b7 AP \u00b7 CNN \u00b7 FINNHUB \u00b7 USGS \u00b7 IMD \u00b7 "
       "ESA/JAXA \u00b7 REVOLUTION MEDICINES \u00b7 CINCINNATI ZOO \u00b7 GOV.UK",
       font=F(SANS, 9), fill=(90, 86, 76), anchor="ma")
d.text((W // 2, 997), "THE SATURDAY GAZETTE \u00b7 ALL FIGURES AS REPORTED 21 NOV 2026",
       font=F(SANSB, 9), fill=GRAY, anchor="ma")

img.save(BASE + "/entry.png", optimize=True)
print("saved", BASE + "/entry.png", img.size)
