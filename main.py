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
BROWN = (146, 90, 32)
PURPLE = (96, 62, 148)
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


def char_width(scale):
    """Advance, in pixels, for one glyph at this scale."""
    return 6 * scale


def text_width(text, scale):
    return len(text) * char_width(scale) - scale


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
        The font holds capitals only, so all text is set in capitals."""
        text = text.upper()
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, colour)
            cx += char_width(scale)
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
# was checked against reporting from that day: One Turn's 20 Nov day page
# (52 stories, sourced from BBC, Reuters, Al Jazeera, The Hindu and more),
# Just Security Early Edition 20 Nov, SCMP, HRW, NDTV and The Hindu.
# 38 stories in 7 regions: the lead plus one headline per story, each
# kept short enough to read at a glance.
# ---------------------------------------------------------------------------
LEAD = {
    "kicker": "DIPLOMACY  -  SHENZHEN",
    "headline": "TRUMP, XI AND PUTIN SIGN JOINT PEACE DECLARATION",
    "sub": "Four-point declaration on UN reform, energy, state immunity and nuclear risk after the first three-way summit.",
    "colour": NAVY,
}

REGIONS = [
    ("EUROPE", BLUE, [
        "KYIV STRIKES KILL 8; 28 HURT IN 9 REGIONS",
        "ALLIES IN BERLIN READY TO TALK TO RUSSIA",
        "CRIMEA BRIDGE HIT 3RD TIME IN 4 DAYS",
        "RUSSIA VIOLATES POLAND AIRSPACE",
        "ESTONIA TO SHUT RUSSIA BORDER 6 MONTHS",
        "EU-UK SUMMIT AGREES YOUTH MOBILITY DEAL",
    ]),
    ("ASIA-PACIFIC", TEAL, [
        "ICJ: MYANMAR COMMITTED GENOCIDE VS ROHINGYA",
        "CYCLONE AKVAN: 300,000 EVACUATED IN ODISHA",
        "TAKAICHI GETS COOL RECEPTION AT APEC",
        "S. KOREA ORDERS RETRIAL OF EX-PM HAN",
        "BANGLADESH VIOLENCE BEFORE HASINA RETURN",
        "PAKISTAN ARMY KILLS 22 MILITANTS IN RAIDS",
    ]),
    ("MIDDLE EAST", GOLD, [
        "HOUTHI MISSILE DAMAGES RIYADH PIF TOWER",
        "HORMUZ TANKER ATTACKS INTENSIFY",
        "TRUMP: NO IRAN DECISION UNTIL NEW YEAR",
        "ISRAELI TROOPS CROSS GAZA YELLOW LINE",
        "IRAQ ORDERS IRAN-BACKED MILITIA OUT",
    ]),
    ("AMERICAS", GREEN, [
        "SENATE BLOCKS BID TO END IRAN WAR 51-48",
        "HAITI FORCES KILL 34 SUSPECTED GANG MEMBERS",
        "BUKELE REGISTERS FOR THIRD TERM",
        "US, VENEZUELA SIGN MILITARY DEAL",
        "BRAZIL BANK SELLS $1BN AS REAL SLIDES 18%",
        "COLOMBIA PROTESTS TAX PLAN; STRIKE CALLED",
    ]),
    ("MARKETS & TECH", NAVY_LIGHT, [
        "ANTHROPIC SHARES UP 17% ON NASDAQ DEBUT",
        "US STOCKS FALL 5TH STRAIGHT DAY; S&P -2%",
        "NIKKEI -4.8%; SOFTBANK -16% IN AI ROUT",
        "GOLD -4.2% AS DOLLAR AND YIELDS WEIGH",
        "CALIFORNIA PROBES NVIDIA AFTER CEO QUITS",
        "GTA 6 LAUNCH TOPS $2.3BN IN SALES",
    ]),
    ("AFRICA", BROWN, [
        "KENYA: LAST EBOLA PATIENT DISCHARGED",
        "SUDAN DRONE STRIKE KILLS 10 AT GOLD MINE",
        "DOZENS MISSING AFTER BOAT SINKS OFF SENEGAL",
        "ETHIOPIA-ERITREA STRIKES RAISE WAR FEARS",
    ]),
    ("CLIMATE & WORLD", PURPLE, [
        "COP31 DRAFT DROPS FOSSIL-FUEL PHASE-OUT",
        "FIJI, TONGA DECLARE DISASTER IN DROUGHT",
        "VOYAGER 1 REACHES ONE LIGHT-DAY FROM EARTH",
        "UN CHIEF RACE STALLS AFTER EIGHT VOTES",
    ]),
]


def draw_icon(canvas, kind, cx, cy, colour):
    """A small pictogram for a story, drawn from shapes, not clip art."""
    if kind == "scales":
        canvas.line(cx, cy - 26, cx, cy + 26, colour, 4)
        canvas.line(cx - 24, cy - 14, cx + 24, cy - 14, colour, 4)
        canvas.line(cx - 24, cy - 14, cx - 30, cy + 8, colour, 3)
        canvas.line(cx - 24, cy - 14, cx - 18, cy + 8, colour, 3)
        canvas.line(cx - 30, cy + 8, cx - 18, cy + 8, colour, 3)
        canvas.line(cx + 24, cy - 14, cx + 30, cy + 8, colour, 3)
        canvas.line(cx + 24, cy - 14, cx + 18, cy + 8, colour, 3)
        canvas.line(cx + 30, cy + 8, cx + 18, cy + 8, colour, 3)
        canvas.rect(cx - 16, cy + 26, 32, 4, colour)
    elif kind == "blast":
        for dx, dy in ((0, -26), (18, -18), (26, 0), (18, 18), (0, 26),
                       (-18, 18), (-26, 0), (-18, -18)):
            canvas.line(cx, cy, cx + dx, cy + dy, colour, 5)
        canvas.circle(cx, cy, 10, colour)
    elif kind == "chart":
        canvas.line(cx - 28, cy + 20, cx - 10, cy + 2, colour, 4)
        canvas.line(cx - 10, cy + 2, cx + 4, cy + 12, colour, 4)
        canvas.line(cx + 4, cy + 12, cx + 28, cy - 20, colour, 4)
        canvas.line(cx + 28, cy - 20, cx + 14, cy - 20, colour, 4)
        canvas.line(cx + 28, cy - 20, cx + 28, cy - 6, colour, 4)
    elif kind == "tower":
        canvas.rect(cx - 14, cy - 26, 28, 52, colour)
        canvas.rect(cx - 20, cy + 26, 40, 4, colour)
        for wy in (-16, -4, 8):
            canvas.rect(cx - 8, cy + wy, 16, 6, WHITE)
    elif kind == "storm":
        for r in (26, 18, 10):
            canvas.circle(cx, cy, r, colour)
        canvas.circle(cx, cy, 4, PAPER)
        canvas.line(cx - 26, cy, cx - 8, cy, colour, 3)
    elif kind == "globe":
        canvas.circle(cx, cy, 26, colour)
        canvas.line(cx - 26, cy, cx + 26, cy, WHITE, 3)
        canvas.line(cx, cy - 26, cx, cy + 26, WHITE, 3)


def draw_lead(canvas, x, y, w, h):
    canvas.rect(x, y, w, h, WHITE)
    canvas.rect(x, y, 10, h, RED)
    canvas.rect(x, y, w, 4, NAVY)
    tx = x + 28
    canvas.text(tx, y + 14, LEAD["kicker"], 2, RED)
    y2 = canvas.paragraph(tx, y + 40, LEAD["headline"], 3, INK, w - 250, 6)
    canvas.paragraph(tx, y2 + 6, LEAD["sub"], 2, GREY, w - 250, 4)
    # Three small flag chips: United States, China, Russia.
    fx = x + w - 214
    fy = y + h // 2 - 18
    # United States: red and white stripes with a navy canton.
    for i in range(7):
        canvas.rect(fx, fy + i * 5, 52, 5, RED if i % 2 == 0 else WHITE)
    canvas.rect(fx, fy, 22, 20, NAVY)
    # China: red field with a gold star.
    canvas.rect(fx + 62, fy, 52, 36, RED)
    canvas.circle(fx + 78, fy + 14, 6, GOLD)
    # Russia: white, blue and red horizontal stripes.
    canvas.rect(fx + 124, fy, 52, 12, WHITE)
    canvas.rect(fx + 124, fy + 12, 52, 12, BLUE)
    canvas.rect(fx + 124, fy + 24, 52, 12, RED)


def draw_grid(canvas, x0, y0, col_w, gap_x):
    """Three columns of region blocks; one short headline per story.
    Returns the y just below the tallest column."""
    columns = [
        [REGIONS[0], REGIONS[3]],  # Europe + Americas
        [REGIONS[1], REGIONS[2]],  # Asia-Pacific + Middle East
        [REGIONS[4], REGIONS[5], REGIONS[6]],  # Markets + Africa + World
    ]
    bottom = y0
    for ci, column in enumerate(columns):
        x = x0 + ci * (col_w + gap_x)
        y = y0
        for name, colour, items in column:
            canvas.rect(x, y, col_w, 24, colour)
            canvas.text(x + 8, y + 5, name, 2, WHITE)
            y += 30
            for headline in items:
                for line in canvas.wrap(headline, 2, col_w - 8)[:2]:
                    canvas.text(x + 4, y, line, 2, INK)
                    y += 17
                y += 7
            y += 6
        bottom = max(bottom, y)
    return bottom


def draw_page():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)
    total = 1 + sum(len(items) for _, _, items in REGIONS)
    # Masthead.
    canvas.rect(0, 0, WIDTH, 92, NAVY)
    canvas.rect(0, 92, WIDTH, 4, GOLD)
    canvas.text_centred(WIDTH // 2, 18, "THE WORLD IN ONE DAY", 5, WHITE)
    canvas.text_centred(WIDTH // 2, 58, "FRIDAY 20 NOVEMBER 2026", 3, GOLD)
    # Lead story.
    draw_lead(canvas, 24, 104, WIDTH - 48, 124)
    # Section bar.
    canvas.rect(24, 238, WIDTH - 48, 26, NAVY)
    canvas.text(40, 244, "THE DAY IN %d STORIES  -  7 REGIONS" % total,
                2, WHITE)
    # Dense grid of the day's stories, on one white panel.
    canvas.rect(24, 274, WIDTH - 48, 690, WHITE)
    draw_grid(canvas, 24, 274, 312, 20)
    # Footer.
    canvas.text_centred(WIDTH // 2, 990,
                        "%d STORIES FROM FRIDAY 20 NOVEMBER 2026" % total,
                        2, GREY)
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
