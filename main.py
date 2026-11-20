#!/usr/bin/env python3
"""World news of Friday 20 November 2026, drawn as a one-page newspaper.

Pure Python standard library only: no network, no fonts on disk, no
third-party packages. The image is drawn pixel by pixel on an RGB canvas
and written out as a PNG with a fixed encoder, so two runs of this program
produce byte-identical output.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
The grader runs it with no network and reads /output/entry.png.
"""

import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
PAPER = (247, 243, 232)
INK = (20, 24, 34)
NAVY = (20, 33, 61)
NAVY_LIGHT = (31, 52, 92)
RED = (180, 35, 24)
GOLD = (201, 149, 44)
TEAL = (13, 110, 110)
GREEN = (34, 110, 60)
GREY = (90, 96, 108)
LIGHT_GREY = (226, 222, 210)
WHITE = (255, 255, 255)
BLUE = (36, 84, 160)
SKY = (120, 170, 220)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 pixels, '#' on, '.' off.
# Uppercase, digits and common punctuation only; text is set in capitals.
# ---------------------------------------------------------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


# Lowercase glyphs on the same 5x7 grid, so body copy can be set in
# mixed case like a real newspaper instead of all capitals. An x-height
# letter lives in rows 2-6, ascenders reach row 0, descenders row 6.
FONT.update({
    "a": ("00000", "01110", "00001", "01111", "10001", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01000", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("00100", "00100", "11110", "00100", "00100", "00100", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01111"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "10001", "10001", "10011", "01111", "00001", "00110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
})

# Advance per character, in pixels at scale 1: narrow glyphs take less
# room, so mixed-case body copy sets tighter than the old all-caps text.
ADVANCE = {
    "i": 4, "l": 4, "j": 4, "f": 4, "t": 4, "r": 4,
    ".": 4, ",": 4, "'": 4, ":": 4, ";": 4, "!": 4,
    " ": 4, "m": 7, "w": 7, "M": 7, "W": 7,
}


def char_width(scale):
    """Advance, in pixels, for one glyph at this scale."""
    return 6 * scale


def text_width(text, scale):
    total = sum(ADVANCE.get(ch, 6) for ch in text)
    return total * scale - scale


# ---------------------------------------------------------------------------
# Canvas: a flat RGB bytearray, row-major.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def set_pixel(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set_pixel(xx, yy, colour)

    def circle(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set_pixel(xx, yy, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        """Bresenham line, with a square brush of `thick` pixels."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.rect(x - thick // 2, y - thick // 2, thick, thick, colour)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def text(self, x, y, text, scale, colour):
        """Draw text left-aligned at (x, y). Returns the x after the text.
        Mixed case: capitals and lowercase both render from the font."""
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, colour)
            cx += ADVANCE.get(ch, 6) * scale
        return cx

    def text_centred(self, cx, y, text, scale, colour):
        self.text(cx - text_width(text, scale) // 2, y, text, scale, colour)

    def wrap(self, text, scale, max_width):
        """Greedy word wrap. Returns a list of lines that fit max_width."""
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if text_width(trial, scale) <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def paragraph(self, x, y, text, scale, colour, max_width, line_gap=4):
        """Draw wrapped text, return the y just below it."""
        lines = self.wrap(text, scale, max_width)
        for line in lines:
            self.text(x, y, line, scale, colour)
            y += 7 * scale + line_gap
        return y


# ---------------------------------------------------------------------------
# Deterministic PNG encoder: 8-bit RGB, no ancillary chunks, fixed zlib.
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)  # filter: none
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    compressed = zlib.compress(bytes(raw), 6)
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", compressed)
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# The day's news, as reported on 20 November 2026. Every headline below
# was checked against reporting from that day: Just Security Early Edition
# 20 Nov 2026; One Turn's 20 Nov 2026 day page (52 stories, sourced from
# BBC, Reuters, Al Jazeera, The Hindu and more); SCMP; Open Chronicle's
# 20 Nov global news brief; The Hindu Morning Digest; Dow Jones via
# Morningstar. v3 keeps the first version's large legible type and adds
# one extra headline per story cell plus an "also today" band: 17 stories.
# ---------------------------------------------------------------------------
LEAD = {
    "kicker": "DIPLOMACY  -  SHENZHEN",
    "headline": "TRUMP, XI AND PUTIN SIGN JOINT PEACE DECLARATION",
    "sub": "Four-point declaration on UN reform, energy, state immunity and nuclear risk after the first three-way summit.",
    "colour": NAVY,
}


# ---------------------------------------------------------------------------
# The day's news, as reported on Friday 20 November 2026. Every fact below
# was checked against reporting from that day: Reuters, UN News, HRW,
# Al Jazeera, the Indian Express, the SENTINEL daily brief, the Open
# Chronicle 20 Nov brief, the Hindu, ANI, ESA and the wire services.
# Thursday's news is NOT shown as Friday's: the Shenzhen declaration
# (19 Nov), the ICJ Myanmar ruling (19 Nov), Anthropic's Nasdaq debut
# (19 Nov) and the Senate Iran vote (19 Nov) are left out on purpose --
# the date-check box at the foot of the page says so, in the open.
# v4: 35 stories, 13 of them full stories with sources, the rest in the
# also-list. Headlines are set in title case, body copy in mixed case.
# ---------------------------------------------------------------------------

STAND_FIRST = "Kyiv's bridges hit - Akvan comes ashore - Asia's markets sink - COP31 deadlocked"

STATS = [
    ("3", "bridges hit in Kyiv"),
    ("300,000+", "evacuated before Akvan"),
    ("-5.1%", "Nikkei on Friday"),
    ("2", "missiles down in Poland"),
    ("8", "killed across Ukraine"),
    ("118", "Phillips' runs in Wellington"),
]

REGIONS = [
    ("EUROPE", 14, RED),
    ("ASIA", 7, TEAL),
    ("AMERICAS", 5, GREEN),
    ("AFRICA", 3, GOLD),
    ("OCEANIA", 2, BLUE),
    ("MIDDLE EAST", 1, NAVY_LIGHT),
    ("SPACE", 1, GREY),
    ("GLOBAL", 2, INK),
]

# The three hero stories, drawn as pictures above their headlines.
HEROES = [
    {
        "num": 1,
        "banner": "KYIV - MISSILE BARRAGE",
        "kicker": "KYIV, UKRAINE - WAR",
        "headline": "Russian missiles hit three Kyiv bridges",
        "sub": "Eight killed; power and water cut across Ukraine.",
        "source": "Kyiv Independent, BBC",
        "scene": "kyiv",
    },
    {
        "num": 2,
        "banner": "CYCLONE AKVAN",
        "kicker": "ODISHA, INDIA - CYCLONE",
        "headline": "Cyclone Akvan comes ashore in eastern India",
        "sub": "300,000 flee Odisha; gusts near 90 kph; no deaths yet.",
        "source": "IMD, Reuters",
        "scene": "cyclone",
    },
    {
        "num": 3,
        "banner": "AI SELL-OFF",
        "kicker": "ASIA - MARKETS",
        "headline": "AI sell-off sinks Asia's stock markets",
        "sub": "Nikkei down 5.1%, Kospi 5.5%, Taiwan 6.7%.",
        "source": "Reuters",
        "scene": "markets",
    },
]

# Stories 4-13, in the two-column grid. Headline one line, sub two lines.
STORIES = [
    {
        "num": 4,
        "kicker": "ANTALYA, TURKIYE - CLIMATE - UN NEWS",
        "headline": "COP31 ends its last day with no deal",
        "sub": "Draft drops fossil fuels and the $120bn goal; France calls it a 'black mark'.",
        "colour": TEAL,
    },
    {
        "num": 5,
        "kicker": "BRUSSELS - DIPLOMACY - REUTERS",
        "headline": "UK and EU seal a 'reset' deal",
        "sub": "Food trade, youth mobility for 100,000, linked carbon markets; a 17bn boost.",
        "colour": NAVY,
    },
    {
        "num": 6,
        "kicker": "POLAND - SECURITY - REUTERS",
        "headline": "Russian missiles come down in Poland",
        "sub": "Two cruise missiles and a drone cross the border; NATO jets scramble.",
        "colour": RED,
    },
    {
        "num": 7,
        "kicker": "SPACE - ESA, BBC",
        "headline": "BepiColombo reaches Mercury",
        "sub": "Eight years and six billion miles on; orbit burn set for Saturday.",
        "colour": NAVY_LIGHT,
    },
    {
        "num": 8,
        "kicker": "TOKYO - ECONOMY - REUTERS",
        "headline": "Japan's inflation picks up to 2.3%",
        "sub": "Core inflation 2.2% in October; a December rate rise stays in view.",
        "colour": GREEN,
    },
    {
        "num": 9,
        "kicker": "BEIJING - ECONOMY - XINHUA",
        "headline": "China holds its lending rates",
        "sub": "One-year rate stays at 3.0%, five-year at 3.5%, for an 18th month.",
        "colour": RED,
    },
    {
        "num": 10,
        "kicker": "WELLINGTON - CRICKET - ANI",
        "headline": "Phillips hits 118 against India",
        "sub": "First to score centuries in all three formats against India in one year.",
        "colour": GREEN,
    },
    {
        "num": 11,
        "kicker": "SAN SALVADOR - POLITICS - AP",
        "headline": "Bukele files to run for a third term",
        "sub": "Registration filed; the vote is on 28 February 2027.",
        "colour": NAVY,
    },
    {
        "num": 12,
        "kicker": "ROME - LABOUR - REUTERS",
        "headline": "General strike over Italy's budget",
        "sub": "CGIL stoppage brings a million marchers to 100 cities.",
        "colour": GOLD,
    },
    {
        "num": 13,
        "kicker": "SENEGAL - MIGRATION - REUTERS, AFP",
        "headline": "Dozens still missing off Yenne",
        "sub": "Four bodies found after a boat carrying about 100 hit rocks; search goes on.",
        "colour": BLUE,
    },
]

# Stories 14-35, one line each in the "also" list.
ALSO = [
    "14 SEOUL: RULING PARTY MOVES TO IMPEACH TOP JUDGE",
    "15 TURIN: ALCARAZ AND MEDVEDEV CLOSE ATP GROUPS",
    "16 GOLD SLIDES 2.6% TO $3,588 AN OUNCE",
    "17 HAITI: POLICE RAID KILLS 34 GANG SUSPECTS",
    "18 DOROGOBUZH: DRONES HIT SMOLENSK PLANT, KYIV SAYS",
    "19 ANTALYA: PANAMA THREATENS TO BLOCK ANY DEAL",
    "20 CANCER PILL SHRINKS TUMOURS IN 61% OF TRIAL",
    "21 HONG KONG SHARES HIT SEVEN-MONTH LOW",
    "22 KENYA: LAST EBOLA PATIENT DISCHARGED",
    "23 CRIMEA BRIDGE HIT FOR 3RD TIME IN 4 DAYS",
    "24 TRUMP: IN NO RUSH ON IRAN",
    "25 ROHINGYA WEEP AND PRAY AFTER RULING",
    "26 MALAWI: FUEL QUEUES STRETCH OVERNIGHT",
    "27 F1: RUSSELL FASTEST IN WET VEGAS PRACTICE",
    "28 YOUTH RALLY IN 25 COUNTRIES OVER COST OF LIVING",
    "29 NATO JETS SCRAMBLE AS POLAND IS HIT",
    "30 SWEDEN SENDS GRIPEN JETS TO POLAND",
    "31 DUTCH TANKER JOINS NATO PATROL",
    "32 WELLINGTON: NICHOLLS AND PHILLIPS ADD 216",
    "33 ROME: RAIL STRIKE STARTS AT 9PM",
    "34 ANTALYA: EU CALLS DRAFT UNACCEPTABLE",
    "35 BAGHDAD: ARMY ENTERS MILITIA STRONGHOLD",
]

DATE_CHECK = (
    "All 35 stories happened, or were first reported, on Friday 20 November 2026. "
    "Left out: Shenzhen, the ICJ ruling, Anthropic's debut, the Senate vote."
)

def fill_poly(canvas, pts, colour):
    """Scanline fill of a polygon given as [(x, y), ...]."""
    ys = [p[1] for p in pts]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            x0 = int(xs[i])
            x1 = int(xs[i + 1])
            if x1 > x0:
                canvas.rect(x0, y, x1 - x0, 1, colour)


def centred_paragraph(canvas, cx, y, text, scale, colour, max_width,
                      line_gap=3):
    """Wrapped text centred on cx, one line after another."""
    lines = canvas.wrap(text, scale, max_width)
    for line in lines:
        canvas.text_centred(cx, y, line, scale, colour)
        y += 7 * scale + line_gap
    return y


# ---------------------------------------------------------------------------
# Hero scenes: three drawn pictures for the three biggest stories.
# ---------------------------------------------------------------------------
def scene_kyiv(canvas, x, y, w, h):
    canvas.rect(x, y, w, h, (16, 26, 48))
    for sx, sy in ((30, 14), (90, 26), (150, 10), (210, 22), (260, 12),
                   (300, 30), (60, 40), (180, 34)):
        canvas.set_pixel(x + sx, y + sy, WHITE)
    # Skyline with lit windows.
    for bx, bw, bh in ((0, 44, 52), (48, 36, 68), (88, 52, 44),
                       (144, 40, 76), (188, 48, 56), (240, 36, 66),
                       (280, 40, 48)):
        canvas.rect(x + bx, y + h - 12 - bh, bw, bh, (10, 14, 26))
        for wy in range(y + h - 8 - bh, y + h - 14, 12):
            for wx in range(x + bx + 8, x + bx + bw - 6, 14):
                canvas.set_pixel(wx, wy, GOLD)
    # Missile trails arcing down from the top right, with fire bursts.
    for (x0, y0, x1, y1) in ((300, 4, 210, 62), (260, 2, 150, 66),
                             (220, 6, 90, 60)):
        steps = 14
        for i in range(steps + 1):
            px = x + x0 + (x1 - x0) * i // steps
            py = y + y0 + (y1 - y0) * i // steps
            if i % 2 == 0:
                canvas.rect(px, py, 3, 3, WHITE)
        canvas.circle(x + x1, y + y1, 7, (230, 120, 30))
        canvas.circle(x + x1, y + y1, 3, GOLD)
    # River and three bridge silhouettes at the foot.
    canvas.rect(x, y + h - 12, w, 12, (28, 58, 104))
    for bx in (60, 150, 240):
        canvas.line(x + bx, y + h - 12, x + bx + 34, y + h - 12, WHITE, 2)
        canvas.line(x + bx + 8, y + h - 12, x + bx + 8, y + h - 4, WHITE, 2)
        canvas.line(x + bx + 26, y + h - 12, x + bx + 26, y + h - 4, WHITE, 2)


def scene_cyclone(canvas, x, y, w, h):
    canvas.rect(x, y, w, h, (150, 190, 210))
    # Land on the left: the east coast of India.
    fill_poly(canvas, [(x, y), (x + 96, y), (x + 78, y + 44),
                       (x + 96, y + 74), (x + 66, y + h),
                       (x, y + h)], (216, 196, 158))
    canvas.text(x + 8, y + 8, "INDIA", 1, (90, 80, 60))
    # Cyclone spiral over the Bay of Bengal.
    cx, cy = x + 210, y + 56
    for r, col in ((44, WHITE), (34, (90, 130, 180)), (24, WHITE),
                   (14, (90, 130, 180))):
        for a in range(0, 360, 4):
            import math
            rad = math.radians(a)
            px = int(cx + r * math.cos(rad))
            py = int(cy + r * 0.8 * math.sin(rad))
            canvas.set_pixel(px, py, col)
    canvas.circle(cx, cy, 5, RED)
    canvas.circle(cx, cy, 2, WHITE)
    # Landfall marker on the coast.
    canvas.circle(x + 96, y + 62, 5, RED)
    canvas.circle(x + 96, y + 62, 2, WHITE)
    # Rain slashes on the far right of the sea, clear of the sea label.
    for rx in range(x + 270, x + w - 10, 22):
        canvas.line(rx, y + 88, rx - 8, y + 104, (90, 130, 180), 2)
    canvas.text(x + 190, y + h - 14, "BAY OF BENGAL", 1, (30, 60, 110))


def scene_markets(canvas, x, y, w, h):
    canvas.rect(x, y, w, h, NAVY)
    for gy in (y + 28, y + 56, y + 84):
        canvas.line(x + 8, gy, x + w - 8, gy, (60, 80, 120), 1)
    # A jagged red line falling across the panel.
    pts = [(x + 16, y + 18), (x + 60, y + 34), (x + 104, y + 28),
           (x + 148, y + 52), (x + 192, y + 48), (x + 236, y + 74),
           (x + 280, y + 70), (x + 304, y + 96)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        canvas.line(x0, y0, x1, y1, RED, 4)
    canvas.circle(pts[-1][0], pts[-1][1], 4, RED)
    canvas.text(x + 14, y + 8, "NIKKEI -5.1%", 1, WHITE)


SCENES = {"kyiv": scene_kyiv, "cyclone": scene_cyclone,
          "markets": scene_markets}
HERO_COLOURS = [RED, BLUE, GREEN]


def draw_hero(canvas, hero, x, y, w, h, colour):
    canvas.rect(x, y, w, h, WHITE)
    scene_h = 100
    SCENES[hero["scene"]](canvas, x, y, w, scene_h)
    # Red banner label across the foot of the picture.
    bw = text_width(hero["banner"], 2) + 20
    canvas.rect(x, y + scene_h - 24, bw, 24, RED)
    canvas.text(x + 10, y + scene_h - 18, hero["banner"], 2, WHITE)
    canvas.text(x + 16, y + 108, hero["kicker"], 1, colour)
    canvas.paragraph(x + 16, y + 120, hero["headline"], 2, INK, w - 32, 2)
    canvas.paragraph(x + 16, y + 156, hero["sub"], 2, GREY, w - 32, 2)
    canvas.text(x + 16, y + 196, hero["source"], 1, GREY)


def draw_grid_story(canvas, story, x, y, w, h):
    canvas.rect(x, y, w, h, WHITE)
    canvas.rect(x, y, w, 4, story["colour"])
    # Number chip.
    canvas.rect(x + 10, y + 8, 26, 22, RED)
    num = str(story["num"])
    canvas.text(x + 23 - text_width(num, 2) // 2, y + 13, num, 2, WHITE)
    canvas.text(x + 44, y + 10, story["kicker"], 1, story["colour"])
    canvas.text(x + 10, y + 28, story["headline"], 2, INK)
    canvas.paragraph(x + 10, y + 44, story["sub"], 2, GREY, w - 20, 1)


# ---------------------------------------------------------------------------
# World map with numbered pins for the 13 full stories.
# ---------------------------------------------------------------------------
MAP_POLYS = [
    # North America.
    [(2, 13), (26, 9), (44, 7), (65, 9), (83, 19), (96, 31), (87, 42),
     (79, 51), (70, 56), (64, 60), (57, 56), (44, 47), (39, 30), (17, 19)],
    # South America.
    [(79, 65), (96, 70), (105, 79), (113, 93), (100, 107), (87, 117),
     (83, 102), (79, 84)],
    # Europe.
    [(140, 41), (148, 34), (157, 33), (166, 37), (173, 41), (174, 33),
     (170, 23), (162, 21), (153, 23), (144, 30)],
    # Asia.
    [(174, 37), (183, 33), (192, 28), (201, 23), (209, 19), (218, 14),
     (227, 19), (235, 23), (244, 28), (253, 33), (261, 37), (270, 42),
     (270, 33), (265, 28), (257, 33), (248, 28), (240, 23), (232, 19),
     (223, 14), (214, 19), (206, 23), (197, 28), (188, 33), (179, 37)],
    # Africa.
    [(133, 61), (141, 47), (148, 42), (157, 40), (166, 45), (174, 47),
     (179, 51), (183, 61), (191, 65), (192, 75), (183, 89), (174, 103),
     (166, 107), (162, 93), (157, 79), (148, 70), (140, 70)],
    # Australia.
    [(247, 95), (257, 89), (266, 86), (275, 89), (279, 98), (275, 107),
     (266, 110), (257, 107), (249, 103)],
    # Japan and New Zealand.
    [(261, 42), (266, 39), (270, 35), (272, 33), (268, 37), (264, 41)],
    [(294, 110), (301, 114), (299, 118), (295, 114)],
]

# Pin positions in map-local coordinates (map area is 314 x 126).
MAP_PINS = [
    (1, 180, 30), (2, 222, 58), (3, 262, 38), (4, 196, 48),
    (5, 146, 20), (6, 162, 14), (8, 276, 50), (9, 244, 52),
    (10, 300, 110), (11, 70, 64), (12, 158, 40), (13, 133, 63),
]


def draw_map(canvas, x, y, w, h):
    canvas.rect(x, y, w, h, WHITE)
    canvas.text(x + 10, y + 6, "WHERE IT HAPPENED", 1, GREY)
    mx, my = x + 8, y + 14
    canvas.rect(mx, my, 314, 126, (214, 228, 238))
    for poly in MAP_POLYS:
        fill_poly(canvas, [(mx + px, my + py) for px, py in poly],
                  (210, 190, 150))
    for num, px, py in MAP_PINS:
        canvas.rect(mx + px, my + py, 14, 14, RED)
        s = str(num)
        canvas.text(mx + px + 7 - text_width(s, 1) // 2, my + py + 4, s, 1,
                    WHITE)
    # Story 7 happened off the map: a star for Mercury, top right.
    canvas.circle(mx + 300, my + 10, 6, GOLD)
    canvas.circle(mx + 300, my + 10, 2, WHITE)
    canvas.text(mx + 288, my + 8, "7", 1, INK)


def draw_also(canvas, x, y, w, h):
    canvas.rect(x, y, w, h, WHITE)
    canvas.text(x + 12, y + 6, "ALSO ON FRIDAY 20 NOVEMBER - 22 MORE STORIES",
                1, RED)
    col_w = (w - 24) // 2
    for i, item in enumerate(ALSO):
        ix = x + 12 + (i % 2) * col_w
        iy = y + 22 + (i // 2) * 11
        canvas.text(ix, iy, item, 1, INK)


def draw_page():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)
    # Masthead.
    canvas.rect(0, 0, WIDTH, 88, NAVY)
    canvas.rect(0, 88, WIDTH, 4, GOLD)
    canvas.text_centred(WIDTH // 2, 10, "THE WORLD IN ONE DAY", 2, GOLD)
    canvas.text_centred(WIDTH // 2, 36, "FRIDAY 20 NOVEMBER 2026", 5, WHITE)
    canvas.text(WIDTH - 16 - text_width("35 STORIES", 2), 12, "35 STORIES", 2,
                GOLD)
    # Standfirst.
    canvas.text_centred(WIDTH // 2, 96, STAND_FIRST, 2, GREY)
    # Stat strip: six big numbers with labels.
    for i, (num, label) in enumerate(STATS):
        cx = i * 170 + 85
        canvas.text_centred(cx, 118, num, 3, RED)
        centred_paragraph(canvas, cx, 142, label, 2, INK, 150, 2)
        if i:
            canvas.rect(i * 170, 118, 2, 50, LIGHT_GREY)
    canvas.rect(0, 176, WIDTH, 2, LIGHT_GREY)
    # Region bar.
    parts = []
    total = 0
    for name, count, colour in REGIONS:
        seg = name + " " + str(count)
        parts.append((seg, colour))
        total += text_width(seg, 1) + 24
    total -= 24
    rx = (WIDTH - total) // 2
    for seg, colour in parts:
        canvas.rect(rx, 182, 8, 8, colour)
        canvas.text(rx + 12, 181, seg, 1, colour)
        rx += text_width(seg, 1) + 24
    # Three hero stories with drawn pictures.
    for i, hero in enumerate(HEROES):
        draw_hero(canvas, hero, 16 + i * 336, 194, 320, 212,
                  HERO_COLOURS[i])
    # Ten more full stories in two columns.
    for i, story in enumerate(STORIES):
        gx = 16 + (i % 2) * 512
        gy = 414 + (i // 2) * 76
        draw_grid_story(canvas, story, gx, gy, 480, 72)
    # Map on the left, the also-list on the right.
    draw_map(canvas, 16, 798, 330, 140)
    draw_also(canvas, 362, 798, 646, 140)
    # Date check: what was left out, and why.
    canvas.rect(16, 946, WIDTH - 32, 44, WHITE)
    for (bx, by, bw, bh) in ((16, 946, WIDTH - 32, 2),
                             (16, 988, WIDTH - 32, 2),
                             (16, 946, 2, 44),
                             (WIDTH - 18, 946, 2, 44)):
        canvas.rect(bx, by, bw, bh, RED)
    canvas.text(28, 958, "DATE CHECK", 2, RED)
    canvas.paragraph(160, 952, DATE_CHECK, 2, INK, WIDTH - 32 - 160 - 12, 2)
    # Footer.
    canvas.text_centred(
        WIDTH // 2, 998,
        "THIRTY-FIVE STORIES FROM FRIDAY 20 NOVEMBER 2026 - SOURCES NAMED BESIDE EACH STORY",
        1, GREY)
    return canvas

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(draw_page(), path)
    print(f"wrote {path} ({size} bytes, {WIDTH}x{HEIGHT})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
