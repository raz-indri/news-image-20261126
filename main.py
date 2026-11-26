#!/usr/bin/env python3
"""news-image-20261126: one front page summing up Thursday 26 November 2026.

Stdlib only. Draws a 1024x1024 newspaper front page with a hand-made 5x7
bitmap font and a hand-rolled PNG encoder (zlib + struct). No network, no
clock, no randomness: two runs write byte-identical files.
"""
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (15, 42, 74)
NAVY_DARK = (9, 28, 52)
SKY = (16, 48, 88)
RED = (176, 42, 42)
GOLD = (201, 162, 39)
TEAL = (31, 122, 110)
GREY = (110, 108, 100)
LIGHT = (233, 228, 216)
WHITE = (255, 255, 255)
BLUE = (52, 110, 180)
ORANGE = (214, 120, 40)
GREEN = (46, 125, 60)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = on. Only capitals, digits and
# punctuation are needed: all copy is upper-cased before drawing.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}

BLANK = ("00000",) * 7


def norm(text):
    """Upper-case and fold the few non-ASCII marks we use into ASCII."""
    return (text.replace("\u2019", "'").replace("\u2014", "-")
                .replace("\u2013", "-").replace("\u00b7", "-")
                .replace("\u20b9", "Rs ").upper())


def text_w(text, scale):
    return len(norm(text)) * 6 * scale


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines, each fitting max_w."""
    text = norm(text)
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))
        self.clip = (0, 0, w, h)

    def set(self, x, y, c):
        cx0, cy0, cx1, cy1 = self.clip
        if cx0 <= x < cx1 and cy0 <= y < cy1:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def frame(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def text(self, x, y, s, scale, c):
        s = norm(s)
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_c(self, y, s, scale, c, x0=0, x1=None):
        """Centred text on one line."""
        x1 = x1 if x1 is not None else self.w
        x = x0 + (x1 - x0 - text_w(s, scale)) // 2
        self.text(x, y, s, scale, c)

    def para(self, x, y, s, scale, c, max_w, lh=None):
        """Wrapped paragraph; returns y after the last line."""
        lh = lh if lh is not None else 7 * scale + 2
        for ln in wrap(s, scale, max_w):
            self.text(x, y, ln, scale, c)
            y += lh
        return y


def png_bytes(w, h, px):
    raw = b"".join(b"\x00" + bytes(px[y * w * 3:(y + 1) * w * 3])
                   for y in range(h))

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- content
HERO_KICKER = "SPACE - CHINA / PAKISTAN"
HERO_HEAD = "PAKISTAN'S FIRST ASTRONAUT REACHES TIANGONG"
HERO_DECK = ("Shenzhou-24 docks at Tiangong with Muhammad Zeeshan Ali aboard - "
             "the first Pakistani and first foreign astronaut on the "
             "station. Docked 11:56 Beijing time.")

THANKS_HEAD = "THANKSGIVING DAY"
THANKS_BODY = ("America gathers for Thanksgiving. NYSE and Nasdaq are "
               "closed today; markets reopen Friday for a 1pm ET early "
               "close.")

MARKETS = [
    "US CONSUMER CONFIDENCE JUMPS",
    "NEAR A 2-YEAR HIGH - CONF. BOARD",
    "S&P 500: 7,201.09, -0.50%",
    "NVIDIA -5.86% TO $155.38",
    "US PLANS NEW TARIFFS ON 16 PARTNERS",
]

CARDS = [
    ("WAR IN UKRAINE",
     "LEAK PUTS RUSSIAN DEAD NEAR 500,000",
     "BBC analysis of leaked Rosstat records counts at least 490,334 "
     "Russian soldiers killed since 2022; the true toll may top 700,000."),
    ("COLOMBIA",
     "10 YEARS AFTER THE PEACE DEAL",
     "A decade on from the 2016 accord, the UN hails progress but warns "
     "commitments are unmet as violence continues."),
    ("VENEZUELA",
     "DEBT OF $237.5BN LAID BARE",
     "Caracas reveals public debt equal to 242% of GDP in its "
     "'Plan Venezuela Renace' restructuring pitch."),
    ("SPACE",
     "BEPICOLOMBO SAFE IN MERCURY ORBIT",
     "The ESA-JAXA probe settles into orbit after an 8-year trip, "
     "despite a shorter-than-planned thruster burn."),
    ("PACIFIC",
     "AUSTRALIA-SOLOMON ISLANDS PACT",
     "Canberra and Honiara sign a landmark security agreement, the "
     "first of its kind in the Pacific."),
    ("EGYPT",
     "SUEZ CANAL TAKINGS DOUBLE",
     "Revenue hits $593m as international shipping returns to the "
     "canal, the authority says."),
]

# 24 one-line briefs, three columns of eight.
BRIEFS = [
    "CANADA - Bank of Canada holds inflation line",
    "EL SALVADOR - $860m debt financing for year-end",
    "BARBADOS - Caribbean AI rules due by February",
    "BRAZIL - Petrobras plans $122bn for 2027-2031",
    "ECUADOR - IMF approves $703m climate programme",
    "COLOMBIA - Police free 20 hostages, 1 gunman dead",
    "FRANCE - Strategic rare earths stockpile planned",
    "SPAIN - Bank tax extended; first strike in 14 years",
    "ITALY - Nears exit from EU deficit procedure",
    "PORTUGAL - 2027 budget approved; deficit warning",
    "UK - Inquiry into nuclear test veterans' health",
    "POLAND - Russian envoy summoned over airspace",
    "RUSSIA - Defence spending up 27% in 2027 budget",
    "UKRAINE - Zelensky meets Hungary PM on energy",
    "GERMANY - Q3 GDP revised down to 0.1%",
    "ISRAEL - Eisenkot wins first coalition deal",
    "IRAN - Rial hits record low after US sanctions",
    "SAUDI ARABIA - $371bn budget for 2027 approved",
    "ETHIOPIA - Africa health summit opens in Addis",
    "INDIA - Constitution Day; AI in war debated at UN",
    "INDIA - Rs 15,000 crore package for Nepal",
    "SOUTH KOREA - EV support as Chinese cars gain",
    "CRICKET - Sooryavanshi, 15, hits 204* off 53 balls",
    "CHESS - Gukesh v Sindarov draw in youngest final",
]

SOURCES = ("SOURCES: REUTERS - BBC - AP - XINHUA - DAWN - AVIATION WEEK - "
           "CONFERENCE BOARD - BANK OF CANADA - IMF - ESA - SUEZ CANAL "
           "AUTHORITY - UN")


# ---------------------------------------------------------------- drawing
def draw_stars(cv, x0, y0, x1, y1, n, seed):
    s = seed
    for _ in range(n):
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        x = x0 + s % (x1 - x0)
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        y = y0 + s % (y1 - y0)
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        r = 1 + s % 2
        cv.circle(x, y, r, WHITE if s % 5 else GOLD)


def draw_space_art(cv, x, y, w, h):
    """Hero artwork: night sky, Earth arc, station, rocket.

    Everything is clipped to the panel so the Earth arc cannot spill
    over the headline and story cards below it.
    """
    cv.clip = (x, y, x + w, y + h)
    cv.rect(x, y, w, h, SKY)
    draw_stars(cv, x, y, x + w, y + h, 90, 20261126)
    # Earth arc, bottom left (only the part inside the panel shows)
    cv.circle(x + 40, y + h + 150, 190, BLUE)
    for dx, dy, r in ((20, -25, 22), (90, -12, 18), (140, -30, 14)):
        cv.circle(x + dx, y + h + dy, r, TEAL)
    # Tiangong station, right side
    sx, sy = x + w - 250, y + 42
    cv.rect(sx - 110, sy + 12, 110, 10, (90, 140, 200))   # left panel
    cv.rect(sx + 60, sy + 12, 110, 10, (90, 140, 200))    # right panel
    for px in range(sx - 110, sx + 170, 14):
        cv.vline(px, sy + 12, 10, (60, 100, 160))
    cv.rect(sx - 50, sy, 110, 34, (200, 205, 210))         # core module
    cv.rect(sx - 50, sy, 110, 6, RED)
    cv.circle(sx - 58, sy + 17, 12, (220, 220, 220))       # node
    cv.rect(sx + 66, sy + 8, 26, 18, (180, 185, 190))      # docked craft
    # Rocket rising, left of station
    rx, ry = x + 130, y + 18
    cv.rect(rx, ry + 26, 22, 62, WHITE)                    # body
    cv.rect(rx, ry + 26, 22, 8, RED)                       # band
    for i in range(11):                                    # nose cone
        cv.hline(rx + i, ry + 15 + i, 22 - 2 * i, RED)
    cv.rect(rx - 10, ry + 78, 10, 14, RED)                 # fins
    cv.rect(rx + 22, ry + 78, 10, 14, RED)
    cv.circle(rx + 11, ry + 52, 6, SKY)                    # window
    cv.circle(rx + 11, ry + 52, 3, WHITE)
    for i in range(5):                                     # flame
        cv.rect(rx + 3 + i * 2, ry + 92 + i * 3, 16 - i * 2, 3, GOLD)
    cv.text(x + w - 268, y + h - 22, "SHENZHOU-24 - TIANGONG, 25 NOV 2026",
            1, GOLD)
    cv.clip = (0, 0, cv.w, cv.h)


def draw_pumpkin(cv, x, y, r):
    """Small Thanksgiving pumpkin for the rail box corner."""
    cv.circle(x, y, r, ORANGE)
    for dx in (-r // 2, 0, r // 2):
        cv.vline(x + dx, y - r + 2, 2 * r - 4, (180, 90, 20))
    cv.rect(x - 2, y - r - 6, 4, 8, GREEN)
    cv.circle(x - 3, y - 3, 2, (200, 140, 60))
    cv.circle(x + 4, y + 2, 2, (200, 140, 60))


def draw_bars(cv, x, y, w, h, vals, c):
    bw = w // len(vals)
    for i, v in enumerate(vals):
        bh = int(h * v)
        cv.rect(x + i * bw + 2, y + h - bh, bw - 4, bh, c)


def build():
    cv = Canvas(W, H, PAPER)
    n_stories = 1 + 2 + len(CARDS) + len(BRIEFS)

    # ---- masthead
    cv.rect(0, 0, W, 116, NAVY)
    cv.text_c(12, "THE WORLD TODAY", 6, WHITE)
    cv.rect(212, 76, 600, 3, GOLD)
    cv.text_c(86, "THURSDAY, 26 NOVEMBER 2026", 3, GOLD)
    # ---- sub-bar
    cv.text(24, 126, "THE WORLD IN ONE PAGE", 2, INK)
    right = "%d STORIES - 7 REGIONS - AS REPORTED TODAY" % n_stories
    cv.text(W - 24 - text_w(right, 2), 126, right, 2, GREY)
    cv.hline(24, 146, W - 48, INK)

    # ---- hero (left) + right rail
    hx, hy, hw = 24, 156, 676
    cv.frame(hx, hy, hw, 242, INK, 2)
    draw_space_art(cv, hx + 2, hy + 2, hw - 4, 118)
    ty = hy + 126
    cv.text(hx + 14, ty, HERO_KICKER, 2, RED)
    ty += 18
    ty = cv.para(hx + 14, ty, HERO_HEAD, 3, INK, hw - 28, lh=24)
    ty += 4
    cv.para(hx + 14, ty, HERO_DECK, 2, INK, hw - 28, lh=15)

    rx, ry, rw = 712, 156, 288
    # Thanksgiving box
    cv.frame(rx, ry, rw, 112, INK, 2)
    cv.rect(rx + 2, ry + 2, rw - 4, 26, RED)
    cv.text(rx + 10, ry + 7, "USA - HOLIDAY", 2, WHITE)
    cv.text(rx + 10, ry + 36, THANKS_HEAD, 2, INK)
    cv.para(rx + 10, ry + 56, THANKS_BODY, 1, INK, rw - 84, lh=10)
    draw_pumpkin(cv, rx + rw - 34, ry + 66, 16)
    # Markets box
    my = ry + 124
    cv.frame(rx, my, rw, 118, INK, 2)
    cv.rect(rx + 2, my + 2, rw - 4, 26, TEAL)
    cv.text(rx + 10, my + 7, "MARKETS", 2, WHITE)
    yy = my + 34
    for i, ln in enumerate(MARKETS):
        col = RED if (i in (2, 3)) else INK
        cv.text(rx + 10, yy, ln, 1, col)
        yy += 11
    draw_bars(cv, rx + 10, my + 92, 120, 20, (0.5, 0.8, 0.4, 0.9, 0.65),
              TEAL)

    # ---- six story cards
    cw, chh, gap = 312, 106, 12
    for i, (kick, head, body) in enumerate(CARDS):
        cx = 24 + (i % 3) * (cw + gap)
        cy = 410 + (i // 3) * (chh + gap)
        cv.frame(cx, cy, cw, chh, INK, 1)
        cv.rect(cx + 1, cy + 1, cw - 2, 20, LIGHT)
        cv.text(cx + 8, cy + 4, kick, 2, RED)
        yy = cy + 26
        yy = cv.para(cx + 8, yy, head, 2, INK, cw - 16, lh=15)
        cv.para(cx + 8, yy + 2, body, 1, INK, cw - 16, lh=10)

    # ---- around the world
    ay = 646
    cv.rect(24, ay, W - 48, 26, NAVY)
    cv.text(34, ay + 5, "AROUND THE WORLD", 2, WHITE)
    cv.text(W - 34 - text_w("IN BRIEF", 2), ay + 5, "IN BRIEF", 2, GOLD)
    by = ay + 34
    for col in range(3):
        bx = 24 + col * (cw + gap)
        yy = by
        for brief in BRIEFS[col * 8:(col + 1) * 8]:
            yy = cv.para(bx, yy, brief, 2, INK, cw, lh=14)
            yy += 4
        cv.vline(bx + cw + 6, by, 252, LIGHT) if col < 2 else None
    cv.hline(24, 946, W - 48, INK)

    # ---- footer
    cv.text(24, 958, SOURCES, 1, GREY)
    cv.text(24, 972,
            "EVENTS OF 24-25 NOV ARE SHOWN AS REPORTED IN THE 26 NOV EDITIONS.",
            1, GREY)
    cv.text(24, 986,
            "ONE DAY - THURSDAY 26 NOVEMBER 2026 - %d STORIES" % n_stories,
            2, NAVY)
    cv.text(W - 24 - text_w("THE WORLD TODAY", 2), 986,
            "THE WORLD TODAY", 2, NAVY)
    return png_bytes(W, H, cv.px)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    data = build()
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
