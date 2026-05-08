"""
Generate a 1080x1080 Instagram-ready show schedule graphic
matching Dugan's Legendary Den branding.

Quadrant layout:
  ┌──────────────┬──────────────┐
  │   LOGO       │  SHOWS 1-3   │
  │  + HEADER    │              │
  ├──────────────┼──────────────┤
  │  SHOWS 4-6   │  TAGLINE /   │
  │              │  SOCIALS     │
  └──────────────┴──────────────┘

Fonts: Cinzel (elegant serif) + Lato (clean sans-serif) — matches website.

Usage:  python make_show_schedule.py
Output: show_schedule.png (in the website/ folder)
"""

from PIL import Image, ImageDraw, ImageFont
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# ── Brand colours ──────────────────────────────────────────
BG_COLOR      = (173, 88, 30)      # #AD581E  Warm burnt orange (banner bg)
GOLD          = (227, 189, 77)     # #E3BD4D
CREAM         = (255, 248, 240)    # #FFF8F0
DIM_CREAM     = (235, 225, 210)    # Brighter for better contrast on orange

# ── Canvas ─────────────────────────────────────────────────
SIZE = 1080
HALF = SIZE // 2
BORDER = 22
INNER = 30

# ── Show data ──────────────────────────────────────────────
SHOWS = [
    ("APR 18–19", "NTX Fort Worth Card Show",     "Amon G. Carter Jr Exhibits Hall"),
    ("APR 25",    "ATX Card Show",                 "Hilton Austin"),
    ("MAY 2–3",   "NTX Card Show",                 "NTX Arena"),
    ("MAY 9–10",  "North ATX Card Show",           "Cadence Bank Center"),
    ("MAY 23–24", "CardsAndMore Pflugerville",     "Courtyard Marriott Pflugerville"),
    ("JUN 12–14", "Austin Card Show",              "Palmer Event Center"),
]


def load_font(name, size):
    for p in [
        os.path.join(script_dir, name),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts", name),
        os.path.join("C:/Windows/Fonts", name),
    ]:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def tile_background(canvas, tile_path, opacity=0.07):
    if not os.path.isfile(tile_path):
        return
    tile = Image.open(tile_path).convert("RGBA")
    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    tw, th = tile.size
    for y in range(0, SIZE, th):
        for x in range(0, SIZE, tw):
            overlay.paste(tile, (x, y))
    r, g, b, a = overlay.split()
    a = a.point(lambda p: int(p * opacity))
    overlay = Image.merge("RGBA", (r, g, b, a))
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), overlay))


def measure(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_hcentred(draw, x1, x2, y, text, font, fill):
    w, _ = measure(draw, text, font)
    draw.text(((x1 + x2 - w) // 2, y), text, fill=fill, font=font)
    return measure(draw, text, font)[1]


def draw_diamond(draw, cx, cy, r=7):
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=GOLD)


def draw_hline(draw, y, x1, x2, width=2):
    draw.line([(x1, y), (x2, y)], fill=GOLD, width=width)


def draw_show_block(draw, shows, x1, x2, y_start, y_end, fonts):
    """Draw show entries, evenly spaced and centred in region."""
    f_date, f_name, f_loc = fonts
    n = len(shows)

    # Measure total content height per entry
    sample_h = (measure(draw, "APR 18", f_date)[1] +
                measure(draw, "Test", f_name)[1] +
                measure(draw, "Test", f_loc)[1] + 26)
    slot_h = (y_end - y_start) // n

    for i, (date, name, location) in enumerate(shows):
        slot_top = y_start + i * slot_h
        # Vertically centre the 3-line block within each slot
        cy = slot_top + (slot_h - sample_h) // 2

        # Date
        h = draw_hcentred(draw, x1, x2, cy, date, f_date, GOLD)
        cy += h + 12
        # Name
        h = draw_hcentred(draw, x1, x2, cy, name, f_name, CREAM)
        cy += h + 10
        # Location
        draw_hcentred(draw, x1, x2, cy, location, f_loc, DIM_CREAM)

        # Wider separator between entries
        if i < n - 1:
            sep_y = slot_top + slot_h
            mid = (x1 + x2) // 2
            draw_hline(draw, sep_y, mid - 90, mid + 90, width=1)


def main():
    img = Image.new("RGB", (SIZE, SIZE), BG_COLOR)
    tile_background(img, os.path.join(script_dir, "brand", "bg_tile.png"), opacity=0.07)

    draw = ImageDraw.Draw(img)

    # ── Double border ──────────────────────────────────────
    draw.rectangle([BORDER, BORDER, SIZE - BORDER - 1, SIZE - BORDER - 1],
                   outline=GOLD, width=2)
    draw.rectangle([INNER, INNER, SIZE - INNER - 1, SIZE - INNER - 1],
                   outline=(200, 160, 60), width=1)

    # ── Cross dividers ─────────────────────────────────────
    draw_hline(draw, HALF, INNER + 8, SIZE - INNER - 8, width=2)
    draw.line([(HALF, INNER + 8), (HALF, SIZE - INNER - 8)], fill=GOLD, width=2)
    for cx, cy in [(HALF, INNER + 8), (HALF, SIZE - INNER - 8),
                   (INNER + 8, HALF), (SIZE - INNER - 8, HALF)]:
        draw_diamond(draw, cx, cy, r=6)
    draw_diamond(draw, HALF, HALF, r=8)

    # ── Fonts (Cinzel serif + Lato sans) ───────────────────
    # Cinzel-Bold.ttf is a variable font (wght 400-900); set named instance.
    f_header    = load_font("Cinzel-Bold.ttf", 48)
    f_header.set_variation_by_name("Black")
    f_date      = load_font("Cinzel-Bold.ttf", 40)
    f_date.set_variation_by_name("Bold")
    f_showname  = load_font("Lato-Bold.ttf", 30)
    f_location  = load_font("Lato-Light.ttf", 22)
    f_tagword   = load_font("Cinzel-Bold.ttf", 36)
    f_tagword.set_variation_by_name("Bold")
    f_handle    = load_font("Lato-Regular.ttf", 24)
    f_web       = load_font("Lato-Regular.ttf", 22)

    show_fonts = (f_date, f_showname, f_location)

    # Quadrant content bounds (tight to dividers for max space)
    L = INNER + 6
    R = SIZE - INNER - 6
    T = INNER + 6
    B = SIZE - INNER - 6

    # ══════════════════════════════════════════════════════
    # TOP-LEFT: Logo + "UPCOMING SHOWS" (vertically centred as one unit)
    # ══════════════════════════════════════════════════════
    tl_cx = (L + HALF) // 2
    tl_top = T + 8
    tl_bot = HALF - 8

    logo_path = os.path.join(script_dir, "brand", "logo.png")
    logo_h = 0
    if os.path.isfile(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        max_logo = min(HALF - L - 50, 320)
        scale = min(max_logo / logo.width, max_logo / logo.height)
        lw, lh = int(logo.width * scale), int(logo.height * scale)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        logo_h = lh

    # Measure header block height: line + gap + UPCOMING + gap + SHOWS + gap + line
    hdr_h1 = measure(draw, "UPCOMING", f_header)[1]
    hdr_h2 = measure(draw, "SHOWS", f_header)[1]
    header_block = 2 + 12 + hdr_h1 + 4 + hdr_h2 + 20 + 2  # lines + text + gaps
    total_tl = logo_h + 14 + header_block  # logo + gap + header

    # Vertically centre the whole unit
    start_y = tl_top + (tl_bot - tl_top - total_tl) // 2

    if os.path.isfile(logo_path):
        lx = tl_cx - lw // 2
        img.paste(logo, (lx, start_y), logo)
        below_logo = start_y + logo_h + 14
    else:
        below_logo = start_y

    # Header text
    draw_hline(draw, below_logo, L + 50, HALF - 50, width=1)
    draw_diamond(draw, tl_cx, below_logo, r=5)
    hy = below_logo + 12
    h = draw_hcentred(draw, L, HALF, hy, "UPCOMING", f_header, GOLD)
    hy += h + 4
    draw_hcentred(draw, L, HALF, hy, "SHOWS", f_header, GOLD)
    hy += measure(draw, "SHOWS", f_header)[1] + 20
    draw_hline(draw, hy, L + 50, HALF - 50, width=1)
    draw_diamond(draw, tl_cx, hy, r=5)

    # ══════════════════════════════════════════════════════
    # TOP-RIGHT: Shows 1-3
    # ══════════════════════════════════════════════════════
    draw_show_block(draw, SHOWS[:3], HALF + 12, R, T + 16, HALF - 16, show_fonts)

    # ══════════════════════════════════════════════════════
    # BOTTOM-LEFT: Shows 4-6
    # ══════════════════════════════════════════════════════
    draw_show_block(draw, SHOWS[3:], L, HALF - 12, HALF + 16, B - 16, show_fonts)

    # ══════════════════════════════════════════════════════
    # BOTTOM-RIGHT: Tagline + socials
    # ══════════════════════════════════════════════════════
    br_cx = (HALF + R) // 2
    br_top = HALF + 16
    br_bot = B - 16
    region_h = br_bot - br_top

    # Stack: CARDS / COLLECTIBLES / COMMUNITY / ---♦--- / @handle / website
    words = ["CARDS", "COLLECTIBLES", "COMMUNITY"]
    word_heights = [measure(draw, w, f_tagword)[1] for w in words]
    handle_h = measure(draw, "@duganslegendaryden", f_handle)[1]
    web_h = measure(draw, "dugansden.com", f_web)[1]

    gap_word = 10
    gap_section = 24
    total_h = (sum(word_heights) + gap_word * 2 +
               gap_section + 2 + gap_section +  # line + gaps
               handle_h + 14 + web_h)

    cy = br_top + (region_h - total_h) // 2

    for i, word in enumerate(words):
        h = draw_hcentred(draw, HALF + 8, R, cy, word, f_tagword, GOLD)
        cy += h + (gap_word if i < 2 else gap_section)

    draw_hline(draw, cy, HALF + 60, R - 60, width=1)
    draw_diamond(draw, br_cx, cy, r=5)
    cy += gap_section

    h = draw_hcentred(draw, HALF + 8, R, cy, "@duganslegendaryden", f_handle, CREAM)
    cy += h + 14
    draw_hcentred(draw, HALF + 8, R, cy, "dugansden.com", f_web, DIM_CREAM)

    # ── Save ───────────────────────────────────────────────
    out_path = os.path.join(script_dir, "brand", "show_schedule.png")
    img.save(out_path, "PNG", dpi=(300, 300))
    print(f"Saved: {out_path}")
    print(f"Size:  {SIZE}x{SIZE}px")


if __name__ == "__main__":
    main()
