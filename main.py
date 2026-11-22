#!/usr/bin/env python3
"""THE SATURDAY GAZETTE — one broadsheet image summing up Saturday 21 November 2026.

Fresh build from RESEARCH.md (38 verified stories). Python 3.13, stdlib + PIL only.
Writes entry.png (1024x1024, <=1 MiB) to $MAKEFUN_OUTPUT_DIR (default /output).
Deterministic: no time, no randomness — two runs produce byte-identical output.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BASE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(BASE, "fonts")

# ---- palette: warm newsprint, one low golden-hour light from the top-left ----
PAPER = (246, 241, 229)
PAPER_DARK = (238, 231, 214)
INK = (25, 23, 19)
INK_SOFT = (74, 68, 58)
RED = (164, 31, 31)
RED_DARK = (122, 20, 20)
NAVY = (30, 58, 92)
NAVY_DEEP = (18, 38, 64)
GOLD = (185, 138, 47)
TEAL = (46, 107, 107)
GREEN = (74, 110, 62)
RULE = (25, 23, 19)
BAND_BG = (43, 54, 66)          # tile illustration band base
MAP_OCEAN = (24, 50, 74)
MAP_LAND = (216, 200, 163)
MAP_LAND_EDGE = (168, 148, 110)
CREAM = (250, 246, 236)
CHIP = (25, 23, 19)

_font_cache = {}


def font(size, bold=False, serif=False):
    key = (size, bold, serif)
    if key not in _font_cache:
        name = ("DejaVuSerif-Bold.ttf" if serif else
                "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
        _font_cache[key] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _font_cache[key]


def wrap(d, text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, f, fill, lh, align="left", max_w=None):
    for ln in lines:
        if align == "center":
            d.text((x + (max_w - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=fill)
        elif align == "right":
            d.text((x + max_w - d.textlength(ln, font=f), y), ln, font=f, fill=fill)
        else:
            d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def chip(d, x, y, text, f, fg=CREAM, bg=CHIP, pad_x=6, pad_y=2):
    w_ = int(d.textlength(text, font=f)) + 2 * pad_x
    h_ = f.size + 2 * pad_y
    d.rounded_rectangle([x, y, x + w_, y + h_], radius=3, fill=bg)
    d.text((x + pad_x, y + pad_y), text, font=f, fill=fg)
    return w_


def stamp(d, cx, cy, text, color=RED, angle=-8, size=15):
    """Rotated rubber-stamp label, pasted centred at (cx, cy)."""
    f = font(size, bold=True)
    tw = int(d.textlength(text, font=f))
    pad = 8
    tmp = Image.new("RGBA", (tw + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.rectangle([2, 2, tw + 2 * pad - 3, size + 2 * pad - 3], outline=color + (255,), width=2)
    td.text((pad, pad - 1), text, font=f, fill=color + (255,))
    tmp = tmp.rotate(angle, expand=True, resample=Image.BICUBIC)
    return tmp, (cx - tmp.width // 2, cy - tmp.height // 2)


def warm_light(img):
    """One uneven golden-hour wash: warm glow top-left fading out, plus a
    faint cool vignette at the far edges. Deterministic (fixed gradient)."""
    small = Image.new("L", (32, 32), 0)
    sd = ImageDraw.Draw(small)
    for i in range(32):
        for j in range(32):
            # distance from top-left corner, normalised
            dist = ((i / 31) ** 2 + (j / 31) ** 2) ** 0.5
            sd.point((i, j), fill=max(0, int(26 * (1 - dist / 1.35))))
    mask = small.resize((W, H), Image.BICUBIC)
    glow = Image.new("RGB", (W, H), (255, 196, 110))
    img.paste(Image.composite(glow, img, mask), (0, 0))
    return img

# ---------------------------------------------------------------- masthead
def draw_masthead(d):
    d.rectangle([0, 0, W, 82], fill=PAPER)
    d.text((W // 2, 4), "THE SATURDAY GAZETTE", font=font(54, serif=True),
           fill=INK, anchor="ma")
    d.rectangle([12, 80, W - 12, 82], fill=RULE)
    # date line: left date, right breadth claim
    d.text((12, 58), "SATURDAY 21 NOVEMBER 2026", font=font(17, bold=True), fill=INK)
    claim = "38 STORIES \u2022 5 CONTINENTS"
    d.text((W - 12 - d.textlength(claim, font=font(17, bold=True)), 58),
           claim, font=font(17, bold=True), fill=RED)


# ---------------------------------------------------------------- lead banners
def lead_frame(d, x, y, w, h, tag, tag_bg):
    d.rectangle([x, y, x + w, y + h], outline=RULE, width=2, fill=CREAM)
    chip(d, x + 8, y + 8, tag, font(11, bold=True), bg=tag_bg)
    return x, y, w, h


def lead_headline(d, x, y, w, headline, sub, source, accent=RED):
    f_h, f_s, f_r = font(23, bold=True), font(11), font(9)
    lines = wrap(d, headline, f_h, w - 16)
    yy = y
    for ln in lines[:2]:
        d.text((x + 8, yy), ln, font=f_h, fill=INK)
        yy += 26
    d.text((x + 8, yy + 4), sub, font=f_s, fill=INK_SOFT)
    d.text((x + w - 8, yy + 5), source, font=f_r, fill=INK_SOFT, anchor="ra")
    return yy


def draw_lead_cop31(d, x, y, w, h):
    lead_frame(d, x, y, w, h, "LEAD 1 \u00b7 CLIMATE \u00b7 ANTALYA", NAVY)
    # conference hall: warm wood rows + delegates + hanging FAILURE banner
    d.rectangle([x + 2, y + 30, x + w - 2, y + 106], fill=(214, 196, 158))
    for r in range(3):
        yy = y + 44 + r * 20
        d.rectangle([x + 14, yy, x + w - 14, yy + 12], fill=(146, 106, 62))
        for c in range(9):
            cx = x + 24 + c * 34
            d.ellipse([cx, yy - 7, cx + 12, yy + 2], fill=(52, 44, 34))
    # hanging banner
    d.rectangle([x + w // 2 - 52, y + 34, x + w // 2 + 52, y + 56], fill=RED)
    d.text((x + w // 2, y + 37), "FAILURE", font=font(15, bold=True),
           fill=CREAM, anchor="ma")
    d.line([x + w // 2 - 52, y + 30, x + w // 2 - 52, y + 34], fill=INK, width=2)
    d.line([x + w // 2 + 52, y + 30, x + w // 2 + 52, y + 34], fill=INK, width=2)
    # draft paper, bottom-left of the art
    d.rectangle([x + 14, y + 78, x + 118, y + 105], fill=CREAM, outline=INK)
    d.text((x + 20, y + 80), "144 \u2192 80", font=font(14, bold=True), fill=RED)
    d.text((x + 20, y + 94), "0 fossil mentions", font=font(9), fill=INK_SOFT)
    lead_headline(d, x, y + 110, w,
                  "COP31: NO DEAL \u2014 TALKS INTO OVERTIME",
                  "Draft cut 144 \u2192 80 \u00b7 0 fossil mentions", "AP \u00b7 REUTERS")


def draw_lead_bitcoin(d, x, y, w, h):
    lead_frame(d, x, y, w, h, "LEAD 2 \u00b7 MARKETS \u00b7 CRYPTO", RED_DARK)
    # chart: $63k top, $54k bottom; dashed $60k line; plunge to $55,555
    cx0, cy0, cw, ch = x + 40, y + 34, w - 56, 70
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], fill=(24, 28, 36))
    def py(p):
        return cy0 + ch - (p - 54000) / (63000 - 54000) * ch
    for p, lab in ((60000, "$60,000"), (55000, "$55,000")):
        d.line([cx0, py(p), cx0 + cw, py(p)], fill=(200, 200, 200), width=1)
        d.text((cx0 - 34, py(p) - 6), lab, font=font(8), fill=INK_SOFT)
    # dashed $60k threshold
    for xx in range(cx0, cx0 + cw, 10):
        d.line([xx, py(60000), xx + 5, py(60000)], fill=GOLD, width=2)
    pts = [(61674, 0.00), (61200, 0.18), (60400, 0.38), (58900, 0.55),
           (56800, 0.72), (55555, 0.86), (56002, 1.00)]
    xy = [(cx0 + f * cw, py(p)) for p, f in pts]
    d.line(xy, fill=(255, 92, 92), width=3, joint="curve")
    d.ellipse([xy[5][0] - 4, xy[5][1] - 4, xy[5][0] + 4, xy[5][1] + 4],
              fill=(255, 92, 92), outline=CREAM)
    d.text((xy[5][0] - 8, xy[5][1] - 6), "LOW $55,555", font=font(9, bold=True),
           fill=(255, 150, 150), anchor="ra")
    d.text((cx0 + cw - 2, py(56002) - 14), "$56,002", font=font(10, bold=True),
           fill=CREAM, anchor="ra")
    lead_headline(d, x, y + 110, w,
                  "BITCOIN CRASHES BELOW $56,000",
                  "\u22129.2% in a day \u00b7 Fear & Greed 12", "FINNHUB \u00b7 REUTERS")


def draw_lead_bepi(d, x, y, w, h):
    lead_frame(d, x, y, w, h, "LEAD 3 \u00b7 SPACE \u00b7 MERCURY", NAVY_DEEP)
    # night sky panel
    d.rectangle([x + 2, y + 30, x + w - 2, y + 106], fill=(10, 16, 30))
    for sx, sy in ((30, 12), (90, 26), (150, 10), (210, 22), (260, 14),
                   (60, 44), (180, 40), (300, 36)):
        d.ellipse([x + sx, y + 30 + sy, x + sx + 2, y + 32 + sy], fill=CREAM)
    # Mercury, cratered, lower right
    mx, my, mr = x + w - 74, y + 72, 30
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(176, 152, 128))
    for crx, cry, cr in ((-12, -7, 6), (5, -12, 4), (10, 7, 7), (-3, 10, 4),
                         (15, -3, 3)):
        d.ellipse([mx + crx - cr, my + cry - cr, mx + crx + cr, my + cry + cr],
                  outline=(120, 100, 82), width=2)
    # spacecraft, lower left, thrust flame toward Mercury
    sx, sy = x + 52, y + 80
    d.rectangle([sx - 26, sy - 6, sx + 26, sy + 6], fill=(200, 200, 200))
    d.rectangle([sx - 44, sy - 3, sx - 26, sy + 3], fill=(90, 110, 160))
    d.rectangle([sx + 26, sy - 3, sx + 44, sy + 3], fill=(90, 110, 160))
    d.polygon([(sx + 26, sy - 4), (sx + 52, sy), (sx + 26, sy + 4)], fill=GOLD)
    d.text((x + 14, y + 34), "19:24 CET", font=font(16, bold=True), fill=GOLD)
    d.text((x + 14, y + 54), "BURN: 37 MIN \u00b7 4 THRUSTERS", font=font(9),
           fill=CREAM)
    tmp, pos = stamp(d, x + 165, y + 94, "DUE TONIGHT", RED, angle=-6, size=12)
    d._image.paste(tmp, pos, tmp)
    lead_headline(d, x, y + 110, w,
                  "TONIGHT: 8-YEAR VOYAGE ENDS AT MERCURY",
                  "Only the 2nd craft ever to orbit Mercury", "ESA \u00b7 JAXA")

# ---------------------------------------------------------------- tiles
def tile_art_base(d, x, y, w, h, bg):
    d.rectangle([x, y, x + w, y + h], fill=bg)


def art_chart(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (24, 28, 36))
    pts = [(0.05, 0.30), (0.25, 0.38), (0.45, 0.34), (0.62, 0.55),
           (0.78, 0.72), (0.95, 0.86)]
    xy = [(x + f * w, y + v * h) for f, v in pts]
    d.line(xy, fill=(255, 92, 92), width=3, joint="curve")
    d.ellipse([xy[-1][0] - 4, xy[-1][1] - 4, xy[-1][0] + 4, xy[-1][1] + 4],
              fill=(255, 92, 92), outline=CREAM)


def art_f1(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (20, 24, 30))
    # checkered flag strip
    for i in range(12):
        for j in range(2):
            if (i + j) % 2 == 0:
                d.rectangle([x + 8 + i * 9, y + 6 + j * 9, x + 17 + i * 9, y + 15 + j * 9],
                            fill=CREAM)
    # simple open-wheel car silhouette
    d.rectangle([x + 130, y + 26, x + 210, y + 36], fill=RED)
    d.polygon([(x + 210, y + 26), (x + 228, y + 32), (x + 210, y + 36)], fill=RED)
    d.rectangle([x + 158, y + 18, x + 178, y + 26], fill=CREAM)
    d.ellipse([x + 138, y + 34, x + 152, y + 44], fill=INK)
    d.ellipse([x + 196, y + 34, x + 210, y + 44], fill=INK)
    d.text((x + 8, y + 28), "POLE: VERSTAPPEN", font=font(11, bold=True), fill=GOLD)


def art_cricket(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (74, 110, 62))
    # stumps
    for i in range(3):
        d.rectangle([x + 30 + i * 10, y + 12, x + 36 + i * 10, y + 38], fill=(232, 214, 170))
    d.rectangle([x + 30, y + 10, x + 56, y + 13], fill=(232, 214, 170))
    # red ball flying
    d.ellipse([x + 190, y + 8, x + 208, y + 26], fill=RED, outline=CREAM)
    d.arc([x + 190, y + 8, x + 208, y + 26], 200, 340, fill=CREAM, width=1)
    d.text((x + 70, y + 12), "486/4", font=font(20, bold=True), fill=CREAM)
    d.text((x + 70, y + 32), "LEAD BY 118", font=font(10, bold=True), fill=GOLD)


def art_court(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (58, 58, 66))
    d.rectangle([x + 8, y + 8, x + w - 8, y + 14], fill=(200, 190, 170))
    for i in range(4):
        cx = x + 26 + i * 56
        d.rectangle([cx, y + 14, cx + 8, y + 38], fill=(200, 190, 170))
    d.rectangle([x + 8, y + 38, x + w - 8, y + 44], fill=(200, 190, 170))


def art_prison(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (70, 76, 84))
    d.rectangle([x, y + 34, x + w, y + 46], fill=(46, 52, 60))
    for i in range(12):
        bx = x + 10 + i * 20
        d.rectangle([bx, y + 4, bx + 5, y + 42], fill=(180, 186, 194))


def art_flag_dk(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (164, 31, 31))
    d.rectangle([x + 30, y + 8, x + 44, y + 38], fill=CREAM)
    d.rectangle([x + 8, y + 18, x + 120, y + 28], fill=CREAM)
    d.text((x + 132, y + 12), "EXPELLED", font=font(13, bold=True), fill=CREAM)
    d.text((x + 132, y + 30), "1 DIPLOMAT", font=font(10), fill=(232, 200, 200))


def art_quotes(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (30, 58, 92))
    d.rounded_rectangle([x + 10, y + 10, x + 112, y + 40], radius=6, fill=CREAM)
    d.text((x + 16, y + 14), "\u201cFRIEND\u201d", font=font(13, bold=True), fill=NAVY)
    d.text((x + 16, y + 30), "\u2014 TRUMP", font=font(8), fill=INK_SOFT)
    d.rounded_rectangle([x + 126, y + 10, x + 234, y + 40], radius=6, fill=RED)
    d.text((x + 132, y + 14), "\u201cKILLER\u201d", font=font(13, bold=True), fill=CREAM)
    d.text((x + 132, y + 30), "\u2014 ZELENSKY", font=font(8), fill=(232, 200, 200))


def art_shield(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (30, 58, 92))
    cx, cy = x + 40, y + 23
    d.polygon([(cx, cy - 16), (cx + 16, cy - 10), (cx + 16, cy + 6),
               (cx, cy + 18), (cx - 16, cy + 6), (cx - 16, cy - 10)], fill=GOLD)
    d.line([(cx - 2, cy - 12), (cx + 4, cy - 2), (cx - 4, cy + 8), (cx + 6, cy + 14)],
           fill=RED_DARK, width=3)
    d.text((x + 102, y + 10), "CYBER CHIEF", font=font(13, bold=True), fill=CREAM)
    d.text((x + 102, y + 28), "FIRED", font=font(13, bold=True), fill=(255, 92, 92))


def art_ballot(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (74, 96, 54))
    d.rectangle([x + 24, y + 16, x + 84, y + 42], fill=(232, 214, 170))
    d.rectangle([x + 44, y + 10, x + 64, y + 16], fill=(232, 214, 170))
    d.line([(x + 30, y + 28), (x + 40, y + 38), (x + 56, y + 18)], fill=GREEN, width=3)
    d.text((x + 120, y + 12), "KEY CITIES", font=font(13, bold=True), fill=CREAM)
    d.text((x + 120, y + 30), "AT STAKE", font=font(10), fill=(210, 220, 200))


def art_fine(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (52, 44, 34))
    d.text((x + 52, y + 6), "$811M", font=font(24, bold=True), fill=GOLD)
    d.text((x + 142, y + 12), "FINED", font=font(14, bold=True), fill=CREAM)
    d.text((x + 142, y + 30), "SCAM ROLLS ON", font=font(9), fill=(232, 200, 200))


def art_tanker(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (24, 50, 74))
    d.rectangle([x, y + 34, x + w, y + 46], fill=(16, 38, 58))
    for i in range(3):
        hx = x + 20 + i * 74
        d.rectangle([hx, y + 18, hx + 58, y + 34], fill=(140, 40, 36))
        d.rectangle([hx + 40, y + 8, hx + 48, y + 18], fill=(200, 190, 170))


def art_wheat(d, x, y, w, h):
    tile_art_base(d, x, y, w, h, (120, 110, 52))
    for i in range(9):
        sx = x + 16 + i * 24
        d.line([(sx, y + 44), (sx, y + 14)], fill=(232, 214, 140), width=2)
        d.ellipse([sx - 4, y + 8, sx + 4, y + 18], fill=(232, 214, 140))
    d.text((x + w - 8, y + 6), "$7.25BN", font=font(15, bold=True), fill=CREAM, anchor="ra")


def draw_tile(d, x, y, w, h, art, place, headline, sub, source,
              stamp_text=None, stamp_color=RED, extra_chip=None):
    d.rectangle([x, y, x + w, y + h], outline=RULE, width=1, fill=CREAM)
    art(d, x + 1, y + 1, w - 2, 46)
    chip(d, x + 6, y + 6, place, font(9, bold=True), bg=CHIP)
    if extra_chip:
        chip(d, x + w - 6 - int(d.textlength(extra_chip, font=font(9, bold=True))) - 12,
             y + 6, extra_chip, font(9, bold=True), bg=RED)
    f_h, f_s = font(15, bold=True), font(10, bold=False)
    lines = wrap(d, headline, f_h, w - 12)
    yy = y + 52
    for ln in lines[:2]:
        d.text((x + 6, yy), ln, font=f_h, fill=INK)
        yy += 17
    sub_lines = wrap(d, sub, f_s, w - 12)
    max_sub = 2 if len(lines) == 1 else 1
    for ln in sub_lines[:max_sub]:
        d.text((x + 6, yy + 1), ln, font=f_s, fill=INK_SOFT)
        yy += 13
    d.text((x + w - 6, y + h - 13), source, font=font(8), fill=INK_SOFT, anchor="ra")
    if stamp_text:
        tmp, pos = stamp(d, x + w // 2 + 14, y + 26, stamp_text, stamp_color, angle=-8, size=13)
        d._image.paste(tmp, pos, tmp)


TILES = [
    (art_chart, "NEW YORK", "WALL STREET ROUT",
     "S&P \u22123.7% into correction \u00b7 Nasdaq \u22125.3%",
     "INVESTOPEDIA", None, "FRI 20 NOV CLOSE"),
    (art_f1, "LAS VEGAS", "ANTONELLI FASTEST, VERSTAPPEN ON POLE",
     "5-grid penalty hands pole to Verstappen", "THE RACE", None, None),
    (art_cricket, "WELLINGTON", "INDIA 486/4, LEAD BY 118",
     "Rahul 136 \u2014 first Test ton in New Zealand", "SPORTRADAR", None, None),
    (art_court, "BROOKLYN", "HUAWEI JURY STILL OUT",
     "Day 3 of deliberations \u2014 no verdict yet", "REUTERS", "STILL OUT", None),
    (art_prison, "NEW YORK", "RIKERS ISLAND TO CLOSE BY 2032",
     "Mayor Mamdani announces the plan", "BBC", None, None),
    (art_flag_dk, "COPENHAGEN", "DENMARK: RUSSIA PLOTTED TO KILL RAPPER",
     "Russian diplomat expelled", "AL JAZEERA", None, None),
    (art_quotes, "KYIV", "ZELENSKY CALLS PUTIN A \u201cKILLER\u201d",
     "After Trump called him a friend", "BBC", None, None),
    (art_shield, "WASHINGTON", "WHITE HOUSE FIRES CYBER CHIEF",
     "Sean Cairncross out after tech outages", "BBC", None, None),
    (art_ballot, "SOUTH AFRICA", "ANC FIGHTS TO HOLD KEY CITIES",
     "After election setbacks", "BBC", None, None),
    (art_fine, "USA", "FINED $811M FOR SCAMMING MIGRANTS",
     "But the scam did not stop", "BBC", None, None),
    (art_tanker, "KHARG, IRAN", "TANKERS MASS AT KHARG ISLAND",
     "Iranian-flagged tankers gather", "DAILY BRIEF", None, "UNVERIFIED"),
    (art_wheat, "USA", "$7.25BN ROUNDUP DEAL APPROVED",
     "Judge approves cancer-claims settlement", "BBC", None, None),
]

# ---------------------------------------------------------------- map band
CONTINENTS = {
    "N_AMERICA": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
                  (-85, 80), (-80, 73), (-75, 72), (-65, 60), (-55, 52),
                  (-60, 46), (-70, 42), (-75, 35), (-80, 32), (-85, 29),
                  (-90, 21), (-95, 19), (-100, 23), (-105, 20), (-110, 24),
                  (-115, 30), (-120, 34), (-125, 40), (-130, 48), (-140, 60),
                  (-155, 58), (-165, 60)],
    "S_AMERICA": [(-80, 10), (-75, 5), (-70, 0), (-65, -5), (-60, -10),
                  (-55, -15), (-50, -20), (-45, -25), (-40, -30), (-50, -33),
                  (-60, -38), (-65, -45), (-70, -52), (-73, -50), (-75, -40),
                  (-78, -30), (-80, -20), (-82, -10), (-80, 0)],
    "EUROPE": [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
               (10, 59), (18, 56), (21, 55), (24, 59), (28, 60), (30, 62),
               (25, 65), (20, 70), (15, 70), (10, 68), (5, 60), (0, 55),
               (-5, 50), (-10, 43), (-9, 37)],
    "AFRICA": [(-17, 15), (-15, 25), (-10, 30), (-5, 35), (0, 36), (10, 37),
               (20, 32), (30, 31), (35, 28), (40, 15), (45, 11), (50, 10),
               (48, 0), (42, -5), (40, -15), (35, -25), (30, -30), (25, -34),
               (20, -35), (15, -30), (12, -18), (10, -5), (8, 4), (0, 5),
               (-8, 5), (-15, 10)],
    "ASIA": [(30, 36), (35, 36), (40, 38), (45, 40), (50, 42), (55, 45),
             (60, 50), (65, 55), (70, 60), (75, 65), (80, 70), (90, 75),
             (100, 76), (110, 74), (120, 73), (130, 72), (140, 72),
             (150, 70), (160, 66), (170, 66), (178, 65), (170, 60),
             (162, 58), (158, 52), (150, 45), (142, 40), (135, 35),
             (130, 30), (127, 33), (122, 38), (120, 32), (115, 25),
             (110, 20), (105, 10), (100, 8), (98, 12), (95, 16), (92, 20),
             (90, 22), (85, 20), (80, 15), (78, 8), (75, 20), (72, 22),
             (68, 25), (65, 25), (60, 25), (57, 26), (54, 26), (52, 28),
             (50, 29), (48, 30), (44, 29), (40, 28), (38, 30), (36, 36)],
    "AUSTRALIA": [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
                  (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
                  (153, -32), (150, -27), (146, -20), (142, -15), (140, -12),
                  (137, -12), (135, -15), (132, -12), (130, -13), (126, -14),
                  (122, -17), (118, -20), (114, -22)],
}

# (number, lon, lat, circle_dx, circle_dy) — offsets de-clutter the Europe cluster
PINS = [
    (1, 30.7, 36.9, 0, 16),
    (2, -74.01, 40.71, 0, 0),
    (3, -115.14, 36.17, 0, 0),
    (4, 174.78, -41.29, -6, 0),
    (5, -73.95, 40.65, 24, 16),
    (6, 12.57, 55.68, 5, -16),
    (7, 30.52, 50.45, 17, -14),
    (8, -0.13, 51.51, -16, 14),
    (9, 84.92, 19.26, 0, 0),
    (10, 50.32, 29.25, 0, 0),
    (11, 4.32, 52.07, 6, 16),
]

MAP_X0, MAP_X1, MAP_Y0, MAP_Y1 = 12, 1012, 668, 776


def map_xy(lon, lat):
    x = MAP_X0 + (lon + 180) / 360 * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (90 - lat) / 180 * (MAP_Y1 - MAP_Y0)
    return x, y


def draw_map(d):
    d.rectangle([12, 646, 1012, 776], outline=RULE, width=1, fill=MAP_OCEAN)
    d.text((16, 650), "WHERE IT HAPPENED", font=font(14, bold=True), fill=CREAM)
    legend = "EUROPE 5 \u00b7 ASIA 2 \u00b7 N. AMERICA 3 \u00b7 OCEANIA 1 \u00b7 SPACE 1"
    d.text((1008, 652), legend, font=font(10, bold=True), fill=GOLD, anchor="ra")
    for pts in CONTINENTS.values():
        d.polygon([map_xy(lon, lat) for lon, lat in pts],
                  fill=MAP_LAND, outline=MAP_LAND_EDGE)
    # graticule hints
    for lon in (-120, -60, 0, 60, 120):
        x, _ = map_xy(lon, 0)
        d.line([x, MAP_Y0, x, MAP_Y1], fill=(255, 255, 255, 26), width=1)
    for n, lon, lat, dx, dy in PINS:
        tx, ty = map_xy(lon, lat)
        cx, cy = tx + dx, ty + dy
        d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=CREAM)
        if dx or dy:
            d.line([tx, ty, cx, cy], fill=CREAM, width=1)
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED, outline=CREAM, width=2)
        d.text((cx, cy - 1), str(n), font=font(10, bold=True), fill=CREAM, anchor="mm")
    # pin 12 — Mercury, out in space at the top-right of the band
    mx, my = 952, 684
    d.ellipse([mx - 11, my - 11, mx + 11, my + 11], fill=(176, 152, 128),
              outline=CREAM, width=1)
    for crx, cry, cr in ((-4, -3, 3), (4, 2, 2), (0, 6, 2)):
        d.ellipse([mx + crx - cr, my + cry - cr, mx + crx + cr, my + cry + cr],
                  outline=(120, 100, 82), width=1)
    d.text((938, 680), "MERCURY", font=font(9, bold=True), fill=CREAM, anchor="ra")
    d.ellipse([mx - 9, my + 14, mx + 9, my + 32], fill=RED, outline=CREAM, width=2)
    d.text((mx, my + 22), "12", font=font(10, bold=True), fill=CREAM, anchor="mm")
    key = ("1 ANTALYA \u00b7 2 NEW YORK \u00b7 3 LAS VEGAS \u00b7 4 WELLINGTON \u00b7 "
           "5 BROOKLYN \u00b7 6 COPENHAGEN \u00b7 7 KYIV \u00b7 8 LONDON \u00b7 "
           "9 ODISHA \u00b7 10 KHARG \u00b7 11 THE HAGUE \u00b7 12 MERCURY")
    d.text((512, 782), key, font=font(9), fill=INK_SOFT, anchor="ma")


# ---------------------------------------------------------------- ALSO + footer
ALSO_LEFT = [
    "RUSSIA'S BIGGEST STRIKE ON UKRAINE \u2014 9 killed, 3 Kyiv bridges hit",
    "RUSSIAN MISSILE LANDS IN POLAND \u2014 Tusk: \u201cdeliberate provocation\u201d",
    "TRUMP'S 90-MIN PRESSER \u2014 hails Asia trip, \u201cvery good talks\u201d with Putin",
    "GTA VI OFFICIAL: $3.79BN DAY ONE \u2014 32.5M copies, biggest launch ever",
    "UK\u2013EU DEAL AGREED \u2014 but tuition-fee row holds up implementation",
    "ANTHROPIC ANT DAY 2 \u2014 closes $88.91, down 8.5%",
    "CYCLONE AKVAN LANDFALL DONE \u2014 zero deaths, 372,000 evacuated",
    "ICJ: MYANMAR GUILTY OF GENOCIDE, 9\u20136 \u2014 first state ever found guilty",
    "IRAQI FORCES ENTER KATAIB HEZBOLLAH HQ \u2014 after 12 years",
    "US AI CHIP CURBS HIT CHINESE TECH \u2014 Z.AI \u221222%, MiniMax \u221234%",
    "UK SECRET CYBER OP SECURES TENS OF THOUSANDS OF FRIDGES",
    "PANCREATIC CANCER PILL \u2014 tumours gone in 1 of 12 patients",
]
ALSO_RIGHT = [
    "SYDNEY CAR-BOMB PLOT \u2014 3 arrested after 10 raids",
    "HIPPO FIONA DIES \u2014 swallowed a visitor's hat; zoo: removal \u201cimpossible\u201d",
    "CANADA COURTS AI DATA CENTRES \u2014 as US voters say no",
    "OIL CLOSES FRIDAY \u2014 Brent $92.57, WTI $83.98",
    "SAUDI\u2013HOUTHI ESCALATION \u2014 3 missiles intercepted over Riyadh",
    "TRUMP PARDONS PETE ROSE \u2014 posthumously, 4,256 career hits",
    "TRILATERAL PEACE DECLARATION \u2014 4 points, no Ukraine deal",
    "LAUREN PRICE UNDISPUTED WELTERWEIGHT CHAMPION",
    "NEPAL PM SHAH MEETS MODI \u2014 first foreign trip",
    "DEAD PETS MEANT FOR CREMATION FOUND ON LIVESTREAM \u2014 Philippines",
    "UK ANNOUNCES \u00a3260M DRONE PACKAGE FOR UKRAINE \u2014 1,000+ drones",
]


def draw_also(d):
    d.text((12, 804), "ALSO", font=font(15, bold=True), fill=INK)
    d.rectangle([64, 814, 1012, 815], fill=RULE)
    f = font(11)
    for col_x, items in ((12, ALSO_LEFT), (520, ALSO_RIGHT)):
        y = 824
        for it in items:
            # shrink only if a line would overflow the column
            size = 11
            while size > 9 and d.textlength("\u2022 " + it, font=font(size)) > 492:
                size -= 1
            d.text((col_x, y), "\u2022 " + it, font=font(size), fill=INK)
            y += 14
    d.rectangle([12, 992, 1012, 993], fill=RULE)
    foot = ("SOURCES: BBC \u00b7 REUTERS \u00b7 CHANNEL NEWS ASIA \u00b7 BLOOMBERG \u00b7 "
            "MKT NEWS \u00b7 AP \u00b7 CNN \u00b7 FINNHUB \u00b7 USGS \u00b7 IMD \u00b7 "
            "ESA/JAXA \u00b7 REVOLUTION MEDICINES \u00b7 CINCINNATI ZOO \u00b7 GOV.UK")
    d.text((512, 998), foot, font=font(9), fill=INK_SOFT, anchor="ma")
    d.text((512, 1012), "THE SATURDAY GAZETTE \u00b7 ALL FIGURES AS REPORTED 21 NOV 2026",
           font=font(8), fill=INK_SOFT, anchor="ma")


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    lx, lw, lh = 12, 328, 188
    draw_lead_cop31(d, lx, 86, lw, lh)
    draw_lead_bitcoin(d, lx + 336, 86, lw, lh)
    draw_lead_bepi(d, lx + 672, 86, lw, lh)
    tx, tw, th = 12, 244, 116
    for i, (art, place, head, sub, src, st, chip_) in enumerate(TILES):
        x = tx + (i % 4) * (tw + 8)
        y = 280 + (i // 4) * (th + 6)
        draw_tile(d, x, y, tw, th, art, place, head, sub, src,
                  stamp_text=st, extra_chip=chip_)
    draw_map(d)
    draw_also(d)
    warm_light(img)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
