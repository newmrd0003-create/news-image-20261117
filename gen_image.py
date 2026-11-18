#!/usr/bin/env python3
"""Draw the 17 Nov 2026 front page, 1024x1024 PNG, stdlib only.

Hand-made PNG encoder (zlib + CRC) and a hand-made 5x7 bitmap font.
Every pixel, glyph and icon in this file was written for this entry.
"""
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (176, 30, 30)
NAVY = (29, 78, 137)
WHITE = (255, 255, 255)
LIGHT = (232, 226, 214)
GREY = (90, 90, 90)
GOLD = (184, 134, 11)

# --- 5x7 bitmap font: each glyph is 7 rows of 5 bits, written as strings ---
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
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '%': ("10001", "10010", "00010", "00100", "01000", "01001", "10001"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r + 2 * r:
                        self.set(xx, yy, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, c):
        x = (self.w - text_width(s, scale)) // 2
        self.text(x, y, s, scale, c)

    def save_png(self, path):
        raw = b''.join(b'\x00' + bytes(self.px[y * W * 3:(y + 1) * W * 3])
                       for y in range(H))

        def chunk(kind, data):
            out = struct.pack('>I', len(data)) + kind + data
            return out + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

        ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
        png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
               + chunk(b'IDAT', zlib.compress(raw, 9))
               + chunk(b'IEND', b''))
        with open(path, 'wb') as f:
            f.write(png)
        return len(png)


# --- icons, each drawn inside a 96x96 box at (bx, by) ---
def icon_bridge(cv, bx, by):
    cv.rect(bx + 6, by + 58, 84, 6, NAVY)          # deck
    cv.rect(bx + 10, by + 64, 6, 26, NAVY)        # pillars
    cv.rect(bx + 80, by + 64, 6, 26, NAVY)
    cv.rect(bx + 45, by + 64, 6, 26, NAVY)
    cv.line(bx + 10, by + 58, bx + 48, by + 22, RED, 4)   # broken arch, left
    cv.line(bx + 48, by + 22, bx + 62, by + 40, RED, 4)
    cv.line(bx + 86, by + 58, bx + 62, by + 40, RED, 4)   # right span sagging
    cv.rect(bx + 56, by + 44, 12, 6, RED)         # fallen span piece
    cv.line(bx + 48, by + 22, bx + 48, by + 58, INK, 3)   # tower
    cv.rect(bx + 20, by + 78, 56, 4, (120, 160, 200))     # water


def icon_tanker(cv, bx, by):
    cv.rect(bx + 12, by + 52, 72, 20, INK)        # hull
    cv.rect(bx + 12, by + 52, 72, 6, RED)
    cv.rect(bx + 18, by + 34, 30, 18, NAVY)       # tanks
    cv.rect(bx + 52, by + 28, 14, 24, NAVY)
    cv.circle(bx + 30, by + 24, 8, RED, fill=True)  # flame over front tank
    cv.circle(bx + 30, by + 14, 5, GOLD, fill=True)
    cv.circle(bx + 44, by + 20, 5, RED, fill=True)   # second flame
    cv.line(bx + 66, by + 28, bx + 66, by + 12, GREY, 3)  # funnel
    cv.rect(bx + 8, by + 76, 80, 4, (120, 160, 200))     # sea


def icon_flags(cv, bx, by):
    # two separate flags on two poles, no overlap, gold bar below = summit table
    cv.vline(bx + 20, by + 14, 46, INK, 3)
    cv.vline(bx + 72, by + 14, 46, INK, 3)
    cv.rect(bx + 23, by + 14, 26, 20, RED)        # flag left: red/white/navy
    cv.rect(bx + 23, by + 21, 26, 7, WHITE)
    cv.rect(bx + 23, by + 28, 26, 6, NAVY)
    cv.rect(bx + 47, by + 14, 26, 20, NAVY)       # flag right: navy/red/white
    cv.rect(bx + 47, by + 21, 26, 7, RED)
    cv.rect(bx + 47, by + 28, 26, 6, WHITE)
    cv.rect(bx + 14, by + 62, 68, 10, GOLD)       # summit table
    cv.rect(bx + 14, by + 62, 68, 3, INK)
    cv.rect(bx + 20, by + 72, 6, 16, INK)         # table legs
    cv.rect(bx + 70, by + 72, 6, 16, INK)


def icon_bank(cv, bx, by):
    cv.rect(bx + 14, by + 18, 68, 8, NAVY)        # roof
    cv.rect(bx + 20, by + 30, 6, 40, INK)         # columns
    cv.rect(bx + 38, by + 30, 6, 40, INK)
    cv.rect(bx + 56, by + 30, 6, 40, INK)
    cv.rect(bx + 74, by + 30, 6, 40, INK)
    cv.rect(bx + 14, by + 72, 68, 6, NAVY)        # base
    cv.rect(bx + 62, by + 44, 24, 34, RED)        # phone overlay
    cv.rect(bx + 65, by + 48, 18, 22, WHITE)
    cv.line(bx + 66, by + 54, bx + 82, by + 54, RED, 2)
    cv.line(bx + 66, by + 60, bx + 82, by + 60, RED, 2)


def icon_pin(cv, bx, by):
    cv.circle(bx + 48, by + 38, 26, RED, fill=True)
    cv.line(bx + 48, by + 58, bx + 48, by + 88, RED, 8)
    cv.line(bx + 48, by + 88, bx + 30, by + 62, RED, 6)
    cv.line(bx + 48, by + 88, bx + 66, by + 62, RED, 6)
    cv.circle(bx + 48, by + 38, 11, WHITE, fill=True)
    cv.circle(bx + 48, by + 38, 5, NAVY, fill=True)
    cv.rect(bx + 12, by + 84, 72, 4, GREY)


def icon_chip(cv, bx, by):
    cv.rect(bx + 28, by + 28, 40, 40, NAVY)       # chip body
    cv.rect(bx + 36, by + 36, 24, 24, GOLD)
    cv.rect(bx + 42, by + 42, 12, 12, INK)
    for px in (32, 44, 56):
        cv.vline(bx + px, by + 12, 16, INK, 4)
        cv.vline(bx + px, by + 68, 16, INK, 4)
        cv.hline(bx + 12, by + px, 16, INK, 4)
        cv.hline(bx + 68, by + px, 16, INK, 4)


ICONS = [icon_bridge, icon_tanker, icon_flags, icon_bank, icon_pin, icon_chip]

PANELS = [
    {"tag": "LEAD - UKRAINE WAR",
     "head": ["KERCH BRIDGE HIT", "AGAIN - ROAD SPAN", "COLLAPSES"],
     "sub": ["SECOND UKRAINIAN STRIKE", "IN UNDER 24 HOURS; TRAFFIC HALTED"],
     "src": "BBC - AL JAZEERA - THE WAR ZONE"},
    {"tag": "GULF - ENERGY",
     "head": ["TANKERS HIT MINES", "OFF HORMUZ"],
     "sub": ["IRAN SAYS TWO TANKERS STRUCK", "MINES AND CAUGHT FIRE"],
     "src": "AL JAZEERA - REUTERS - CLAIM UNVERIFIED"},
    {"tag": "ASIA - DIPLOMACY",
     "head": ["TRUMP LANDS IN", "MANILA - XI SUMMIT", "SET FOR THURSDAY"],
     "sub": ["THREE-WAY TALKS WITH XI AND", "PUTIN CONFIRMED IN SHENZHEN"],
     "src": "AP - CHINA FOREIGN MINISTRY"},
    {"tag": "MONEY - USA",
     "head": ["BANKS GO DOWN -", "CHASE BLAMES", "SOFTWARE BUG"],
     "sub": ["ONLINE BANKING AND ZELLE", "SLOWED; NOT A CYBERATTACK"],
     "src": "USA TODAY - ABC NEWS"},
    {"tag": "EUROPE - MIGRATION",
     "head": ["EUROPE PLANS", "RWANDA RETURN HUB"],
     "sub": ["FIVE STATES TO SEND REJECTED", "ASYLUM SEEKERS TO RWANDA"],
     "src": "DW - AP"},
    {"tag": "MARKETS - TECH",
     "head": ["NVIDIA REPORTS", "AFTER HUANG'S", "EXIT"],
     "sub": ["FIRST EARNINGS SINCE THE CHIEF", "EXECUTIVE RESIGNED"],
     "src": "BLOOMBERG - LEVEL HEADLINES"},
]


def draw():
    cv = Canvas(W, H, PAPER)
    # outer frame
    cv.rect(0, 0, W, 6, INK)
    cv.rect(0, H - 6, W, 6, INK)
    cv.rect(0, 0, 6, H, INK)
    cv.rect(W - 6, 0, 6, H, INK)
    # masthead
    cv.text_center(26, "THE WORLD IN ONE DAY", 5, INK)
    cv.hline(60, 72, W - 120, RED, 4)
    cv.text_center(92, "TUESDAY 17 NOVEMBER 2026", 3, RED)
    cv.text_center(124, "SIX STORIES FROM AROUND THE WORLD - IN ONE PAGE", 2, GREY)
    cv.hline(60, 154, W - 120, INK, 3)
    # panels: 2 cols x 3 rows
    px0, py0 = 24, 176
    pw, ph, gap = 480, 270, 16
    for i, p in enumerate(PANELS):
        col, row = i % 2, i // 2
        x = px0 + col * (pw + gap)
        y = py0 + row * (ph + gap)
        cv.rect(x, y, pw, ph, WHITE)
        cv.rect(x, y, pw, 4, INK)
        cv.rect(x, y + ph - 4, pw, 4, INK)
        cv.rect(x, y, 4, ph, INK)
        cv.rect(x + pw - 4, y, 4, ph, INK)
        cv.rect(x + 4, y + 4, pw - 8, 26, RED if i == 0 else NAVY)
        cv.text(x + 14, y + 11, p["tag"], 2, WHITE)
        # icon box
        ix, iy = x + 16, y + 46
        cv.rect(ix, iy, 96, 96, LIGHT)
        cv.rect(ix, iy, 96, 3, INK)
        cv.rect(ix, iy + 93, 96, 3, INK)
        cv.rect(ix, iy, 3, 96, INK)
        cv.rect(ix + 93, iy, 3, 96, INK)
        ICONS[i](cv, ix, iy)
        # headline, scale 3, at right of icon
        hx = x + 128
        hy = y + 48
        for ln in p["head"]:
            cv.text(hx, hy, ln, 3, INK)
            hy += 28
        # sub-label, scale 2, full width below
        sy = y + 158
        for ln in p["sub"]:
            cv.text(x + 16, sy, ln, 2, INK)
            sy += 20
        # divider + source line
        cv.hline(x + 16, y + 232, pw - 32, LIGHT, 2)
        cv.text(x + 16, y + 242, p["src"], 1, GREY)
    return cv


if __name__ == "__main__":
    cv = draw()
    n = cv.save_png("entry.png")
    print(f"wrote entry.png {n} bytes, {W}x{H}")
