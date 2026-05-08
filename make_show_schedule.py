"""
Generate a 1080x1080 Instagram-ready show schedule graphic
matching Dugan's Legendary Den branding.

Polished vertical layout: vignette, drop shadows, frosted content panel,
filled month badges, corner ornaments, text glow.

Fonts: Cinzel (serif) + Lato (sans-serif) — matches dugansden.com.

Usage:  python make_show_schedule.py
Output: show_schedule.png
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# ── Brand colours ──────────────────────────────────────────
BG_COLOR   = (173, 88, 30)      # #AD581E  Warm burnt orange
BG_DARK    = (120, 55, 12)      # Darker shade for depth
GOLD       = (227, 189, 77)     # #E3BD4D
GOLD_DIM   = (180, 148, 55)     # Muted gold for secondary accents
CREAM      = (255, 248, 240)    # #FFF8F0
DIM_CREAM  = (225, 215, 200)
PANEL_BG   = (100, 45, 10)      # Dark panel behind content

# ── Canvas ─────────────────────────────────────────────────
SIZE   = 1080
BORDER = 20
INNER  = 28

# ── Show data (grouped by month) ──────────────────────────
SHOWS = [
    ("APRIL", [
        ("18–19", "NTX Fort Worth Card Show",    "Amon G. Carter Jr Exhibits Hall"),
        ("24–26", "Texoma Trading Card Expo",     "Choctaw Durant Event Center"),
    ]),
    ("MAY", [
        ("2–3",   "NTX Card Show",               "NTX Arena"),
        ("9–10",  "North ATX Card Show",          "Cadence Bank Center"),
        ("23–24", "CardsAndMore Pflugerville",    "Courtyard Marriott Pflugerville"),
    ]),
    ("JUNE", [
        ("12–14", "Austin Card Show",            "Palmer Event Center"),
    ]),
]


# ── Helpers ────────────────────────────────────────────────

def load_font(name, size):
    for p in [
        os.path.join(script_dir, name),
        os.path.join(os.environ.get("LOCALAPPDATA", ""),
                     "Microsoft", "Windows", "Fonts", name),
        os.path.join("C:/Windows/Fonts", name),
    ]:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def tile_background(canvas, tile_path, opacity=0.08):
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


def add_vignette(canvas, strength=0.55):
    """Darken edges with a radial gradient for depth."""
    vig = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cx, cy = SIZE // 2, SIZE // 2
    max_dist = math.hypot(cx, cy)
    pixels = vig.load()
    for py in range(SIZE):
        for px in range(SIZE):
            d = math.hypot(px - cx, py - cy) / max_dist
            # Ease-in — dark only at edges
            frac = max(0.0, (d - 0.3) / 0.7) ** 1.8
            alpha = int(frac * 255 * strength)
            pixels[px, py] = (0, 0, 0, alpha)
    return Image.alpha_composite(canvas.convert("RGBA"), vig).convert("RGB")


def add_drop_shadow(canvas, sprite, pos, offset=(6, 6), blur=12, opacity=0.5):
    """Paste sprite with a soft drop shadow."""
    sx, sy = pos
    ox, oy = offset
    # Shadow layer
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    # Use sprite alpha as shadow shape
    shadow_sprite = Image.new("RGBA", sprite.size,
                              (0, 0, 0, int(255 * opacity)))
    shadow_sprite.putalpha(sprite.split()[3])
    shadow.paste(shadow_sprite, (sx + ox, sy + oy))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), shadow))
    canvas.paste(sprite, pos, sprite)


def draw_content_panel(img, x1, y1, x2, y2, radius=18, opacity=0.35):
    """Draw a semi-transparent dark rounded panel."""
    panel = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                         fill=(30, 15, 5, int(255 * opacity)))
    # Gold border with slight transparency
    pd.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                         outline=(*GOLD_DIM, 180), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), panel))


def draw_filled_badge(img, draw, x1, y1, x2, y2, text, font, radius=12):
    """Draw a premium month badge with double border, inner glow, and diamond accents."""
    badge = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)

    # Outer border (dark, slightly larger)
    bd.rounded_rectangle([x1 - 3, y1 - 3, x2 + 3, y2 + 3], radius=radius + 2,
                         fill=(0, 0, 0, 0), outline=(40, 20, 5, 180), width=1)
    # Main fill
    bd.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                         fill=(50, 22, 3, 220), outline=GOLD, width=2)
    # Inner border (inset gold, subtler)
    bd.rounded_rectangle([x1 + 5, y1 + 5, x2 - 5, y2 - 5], radius=max(radius - 4, 2),
                         fill=(0, 0, 0, 0), outline=(*GOLD_DIM, 120), width=1)

    img.paste(Image.alpha_composite(img.convert("RGBA"), badge))
    draw = ImageDraw.Draw(img)

    # Diamond accents at top and bottom centre of badge
    bcx = (x1 + x2) // 2
    draw_diamond(draw, bcx, y1, r=5)
    draw_diamond(draw, bcx, y2, r=5)

    # Centred text (accounting for font bbox offset)
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    mcx = (x1 + x2) // 2
    mcy = (y1 + y2) // 2
    # Shadow
    draw.text((mcx - tw // 2 - bb[0] + 2, mcy - th // 2 - bb[1] + 2), text,
              fill=(30, 12, 0), font=font)
    draw.text((mcx - tw // 2 - bb[0], mcy - th // 2 - bb[1]), text,
              fill=GOLD, font=font)
    return draw


def draw_text_with_shadow(draw, pos, text, font, fill, shadow_fill=(0, 0, 0),
                          shadow_offset=(2, 2), shadow_opacity=0.4):
    """Draw text with a subtle shadow for depth."""
    sx, sy = pos
    ox, oy = shadow_offset
    sr, sg, sb = shadow_fill
    draw.text((sx + ox, sy + oy), text, fill=(*shadow_fill, int(255 * shadow_opacity)),
              font=font)
    draw.text(pos, text, fill=fill, font=font)


def measure(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_diamond(draw, cx, cy, r=7):
    draw.polygon([(cx, cy - r), (cx + r, cy),
                  (cx, cy + r), (cx - r, cy)], fill=GOLD)


def draw_hline(draw, y, x1, x2, width=2):
    draw.line([(x1, y), (x2, y)], fill=GOLD, width=width)


def draw_corner_ornaments(draw, m, length=35, inset=5):
    """Draw L-shaped gold corner ornaments."""
    corners = [
        (m + inset, m + inset, 1, 1),
        (SIZE - m - inset, m + inset, -1, 1),
        (m + inset, SIZE - m - inset, 1, -1),
        (SIZE - m - inset, SIZE - m - inset, -1, -1),
    ]
    for cx, cy, dx, dy in corners:
        draw.line([(cx, cy), (cx + length * dx, cy)], fill=GOLD, width=3)
        draw.line([(cx, cy), (cx, cy + length * dy)], fill=GOLD, width=3)
        draw_diamond(draw, cx, cy, r=7)


# ── Main ───────────────────────────────────────────────────

def main():
    img = Image.new("RGB", (SIZE, SIZE), BG_COLOR)
    tile_background(img, os.path.join(script_dir, "brand", "bg_tile.png"), opacity=0.08)

    # ── Vignette for depth ─────────────────────────────────
    img = add_vignette(img, strength=0.55)
    draw = ImageDraw.Draw(img)

    # ── Corner ornaments instead of plain border ───────────
    draw_corner_ornaments(draw, BORDER, length=65, inset=0)

    # ── Fonts ──────────────────────────────────────────────
    f_header = load_font("Cinzel-Bold.ttf", 56)
    f_header.set_variation_by_name("Black")

    f_month = load_font("Cinzel-Bold.ttf", 44)
    f_month.set_variation_by_name("Bold")

    f_date = load_font("Cinzel-Bold.ttf", 48)
    f_date.set_variation_by_name("Bold")

    f_name = load_font("Lato-Bold.ttf", 36)
    f_loc  = load_font("Lato-Light.ttf", 28)

    f_social = load_font("Lato-Regular.ttf", 26)
    f_web    = load_font("Lato-Light.ttf", 23)

    cx = SIZE // 2

    # ── Layout constants ───────────────────────────────────
    MARGIN_L = 65
    MARGIN_R = 50
    BADGE_W  = 190
    badge_cx = MARGIN_L + BADGE_W // 2

    DATE_X = MARGIN_L + BADGE_W + 24
    max_date_w = max(measure(draw, d, f_date)[0]
                     for _, shows in SHOWS for d, _, _ in shows)
    NAME_X = DATE_X + max_date_w + 18

    # ══════════════════════════════════════════════════════
    # TOP ROW: Logo (left) + Socials (right)
    # ══════════════════════════════════════════════════════
    TOP_PAD = INNER + 16
    logo_path = os.path.join(script_dir, "brand", "logo.png")
    logo_bottom = TOP_PAD
    if os.path.isfile(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        max_logo = 300
        scale = min(max_logo / logo.width, max_logo / logo.height)
        lw = int(logo.width * scale)
        lh = int(logo.height * scale)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        logo_x = MARGIN_L + 50
        logo_y = TOP_PAD
        add_drop_shadow(img, logo, (logo_x, logo_y),
                        offset=(5, 5), blur=15, opacity=0.5)
        draw = ImageDraw.Draw(img)
        logo_bottom = logo_y + lh

    # Socials — right-aligned, vertically centred to logo midpoint
    handle_text = "@duganslegendaryden"
    web_text = "dugansden.com"
    handle_w, handle_h = measure(draw, handle_text, f_social)
    web_w, web_h = measure(draw, web_text, f_web)
    social_block_h = handle_h + 8 + web_h
    social_right = SIZE - MARGIN_R - 60
    logo_mid_y = TOP_PAD + (logo_bottom - TOP_PAD) // 2
    social_top = logo_mid_y - social_block_h // 2

    # Small decorative line above socials
    line_left = social_right - max(handle_w, web_w)
    draw_hline(draw, social_top - 12, line_left, social_right, width=1)

    draw.text((social_right - handle_w, social_top),
              handle_text, fill=CREAM, font=f_social)
    draw.text((social_right - web_w, social_top + handle_h + 8),
              web_text, fill=DIM_CREAM, font=f_web)

    # Small decorative line below socials
    draw_hline(draw, social_top + social_block_h + 12, line_left, social_right, width=1)

    # ══════════════════════════════════════════════════════
    # HEADER: "UPCOMING SHOWS" — full width, no divider lines
    # ══════════════════════════════════════════════════════
    y = logo_bottom + 25

    hdr_w, hdr_h = measure(draw, "UPCOMING SHOWS", f_header)
    hx = (SIZE - hdr_w) // 2
    draw.text((hx + 3, y + 3), "UPCOMING SHOWS",
              fill=(40, 18, 0), font=f_header)
    draw.text((hx, y), "UPCOMING SHOWS", fill=GOLD, font=f_header)
    y += hdr_h + 28

    # ══════════════════════════════════════════════════════
    # SHOW LISTINGS — with content panel and side badges
    # ══════════════════════════════════════════════════════
    ENTRY_GAP = 26
    GROUP_GAP = 36

    # Measure total content height for panel
    panel_top = y
    temp_y = y
    for month, shows in SHOWS:
        entry_heights = []
        for date, name, loc in shows:
            dh = measure(draw, date, f_date)[1]
            nh = measure(draw, name, f_name)[1]
            lhh = measure(draw, loc, f_loc)[1]
            entry_heights.append(max(dh, nh) + 5 + lhh)
        group_h = sum(entry_heights) + ENTRY_GAP * (len(shows) - 1)
        badge_pad = 10
        badge_h = max(group_h, measure(draw, month, f_month)[1] + badge_pad * 2)
        temp_y += badge_h + GROUP_GAP
    # Extend panel to fill available space (down to near bottom edge)
    panel_bottom_content = temp_y - GROUP_GAP + 16
    panel_bottom = max(panel_bottom_content, SIZE - INNER - 20)

    # Draw frosted content panel — darker for better contrast
    draw_content_panel(img, MARGIN_L - 10, panel_top - 10,
                       SIZE - MARGIN_R + 10, panel_bottom,
                       radius=16, opacity=0.40)
    draw = ImageDraw.Draw(img)

    # Month groups with side badges
    for month, shows in SHOWS:
        entry_heights = []
        for date, name, loc in shows:
            dh = measure(draw, date, f_date)[1]
            nh = measure(draw, name, f_name)[1]
            lh = measure(draw, loc, f_loc)[1]
            entry_heights.append(max(dh, nh) + 5 + lh)
        group_h = sum(entry_heights) + ENTRY_GAP * (len(shows) - 1)

        badge_pad = 10
        badge_h = max(group_h, measure(draw, month, f_month)[1] + badge_pad * 2)
        bx = badge_cx - BADGE_W // 2

        # Premium badge
        draw = draw_filled_badge(img, draw,
                                 bx, y, bx + BADGE_W, y + badge_h,
                                 month, f_month, radius=10)

        # Show entries
        entries_y = y + (badge_h - group_h) // 2

        for si, (date, name, loc) in enumerate(shows):
            dw, dh = measure(draw, date, f_date)
            nw, nh = measure(draw, name, f_name)
            lh_val = measure(draw, loc, f_loc)[1]
            line1_h = max(dh, nh)
            row_h = line1_h + 5 + lh_val

            # Date with shadow
            draw.text((DATE_X + 2, entries_y + 2), date,
                      fill=(40, 18, 0), font=f_date)
            draw.text((DATE_X, entries_y), date, fill=GOLD, font=f_date)

            # Name
            name_y = entries_y + max(0, (dh - nh) // 2)
            draw.text((NAME_X, name_y), name, fill=CREAM, font=f_name)

            # Location
            draw.text((NAME_X, entries_y + line1_h + 5), loc,
                      fill=DIM_CREAM, font=f_loc)

            entries_y += row_h + ENTRY_GAP

        y += badge_h + GROUP_GAP

    # ── Save ───────────────────────────────────────────────
    out_path = os.path.join(script_dir, "brand", "show_schedule.png")
    img.save(out_path, "PNG", dpi=(300, 300))
    print(f"Saved: {out_path}")
    print(f"Size:  {SIZE}x{SIZE}px")


if __name__ == "__main__":
    main()
