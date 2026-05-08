"""
Generate a 1080x1080 Instagram announcement graphic for a schedule change.

Usage:  python make_schedule_change.py
Output: schedule_change.png
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# ── Brand colours ──────────────────────────────────────────
BG_COLOR   = (173, 88, 30)
BG_DARK    = (120, 55, 12)
GOLD       = (227, 189, 77)
GOLD_DIM   = (180, 148, 55)
CREAM      = (255, 248, 240)
DIM_CREAM  = (225, 215, 200)
RED_MUTED  = (220, 80, 70)
GREEN_MUTED = (90, 200, 90)

SIZE   = 1080
BORDER = 20
INNER  = 28


# ── Helpers (shared with make_show_schedule.py) ────────────

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
    vig = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cx, cy = SIZE // 2, SIZE // 2
    max_dist = math.hypot(cx, cy)
    pixels = vig.load()
    for py in range(SIZE):
        for px in range(SIZE):
            d = math.hypot(px - cx, py - cy) / max_dist
            frac = max(0.0, (d - 0.3) / 0.7) ** 1.8
            alpha = int(frac * 255 * strength)
            pixels[px, py] = (0, 0, 0, alpha)
    return Image.alpha_composite(canvas.convert("RGBA"), vig).convert("RGB")


def add_drop_shadow(canvas, sprite, pos, offset=(6, 6), blur=12, opacity=0.5):
    sx, sy = pos
    ox, oy = offset
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_sprite = Image.new("RGBA", sprite.size,
                              (0, 0, 0, int(255 * opacity)))
    shadow_sprite.putalpha(sprite.split()[3])
    shadow.paste(shadow_sprite, (sx + ox, sy + oy))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), shadow))
    canvas.paste(sprite, pos, sprite)


def draw_content_panel(img, x1, y1, x2, y2, radius=18, opacity=0.35):
    panel = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                         fill=(30, 15, 5, int(255 * opacity)))
    pd.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                         outline=(*GOLD_DIM, 180), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), panel))


def measure(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_diamond(draw, cx, cy, r=7):
    draw.polygon([(cx, cy - r), (cx + r, cy),
                  (cx, cy + r), (cx - r, cy)], fill=GOLD)


def draw_hline(draw, y, x1, x2, width=2):
    draw.line([(x1, y), (x2, y)], fill=GOLD, width=width)


def draw_corner_ornaments(draw, m, length=35, inset=5):
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


def draw_strikethrough_text(draw, pos, text, font, fill, strike_fill):
    """Draw text with a strikethrough line."""
    x, y = pos
    draw.text(pos, text, fill=fill, font=font)
    bb = draw.textbbox(pos, text, font=font)
    mid_y = (bb[1] + bb[3]) // 2
    draw.line([(bb[0] - 4, mid_y), (bb[2] + 4, mid_y)], fill=strike_fill, width=3)


def centered_text(draw, y, text, font, fill):
    """Draw text centred horizontally, return (width, height)."""
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = (SIZE - tw) // 2 - bb[0]
    draw.text((x, y - bb[1]), text, fill=fill, font=font)
    return tw, th


def centered_text_shadow(draw, y, text, font, fill, shadow=(40, 18, 0)):
    """Draw centred text with a shadow, return (width, height)."""
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = (SIZE - tw) // 2 - bb[0]
    draw.text((x + 2, y - bb[1] + 2), text, fill=shadow, font=font)
    draw.text((x, y - bb[1]), text, fill=fill, font=font)
    return tw, th


# ── Main ───────────────────────────────────────────────────

def main():
    img = Image.new("RGB", (SIZE, SIZE), BG_COLOR)
    tile_background(img, os.path.join(script_dir, "brand", "bg_tile.png"), opacity=0.08)
    img = add_vignette(img, strength=0.55)
    draw = ImageDraw.Draw(img)
    draw_corner_ornaments(draw, BORDER, length=65, inset=0)

    # ── Fonts ──────────────────────────────────────────────
    f_header = load_font("Cinzel-Bold.ttf", 52)
    f_header.set_variation_by_name("Black")

    f_sub = load_font("Cinzel-Bold.ttf", 36)
    f_sub.set_variation_by_name("Bold")

    f_date = load_font("Cinzel-Bold.ttf", 44)
    f_date.set_variation_by_name("Bold")

    f_show = load_font("Lato-Bold.ttf", 38)
    f_loc = load_font("Lato-Light.ttf", 28)
    f_body = load_font("Lato-Regular.ttf", 30)
    f_social = load_font("Lato-Regular.ttf", 24)

    cx = SIZE // 2
    MARGIN = 80

    # ── Logo centred at top ────────────────────────────────
    TOP_PAD = INNER + 20
    logo_path = os.path.join(script_dir, "brand", "logo.png")
    logo_bottom = TOP_PAD
    if os.path.isfile(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        max_logo = 240
        scale = min(max_logo / logo.width, max_logo / logo.height)
        lw = int(logo.width * scale)
        lh = int(logo.height * scale)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        logo_x = (SIZE - lw) // 2
        logo_y = TOP_PAD
        add_drop_shadow(img, logo, (logo_x, logo_y),
                        offset=(5, 5), blur=15, opacity=0.5)
        draw = ImageDraw.Draw(img)
        logo_bottom = logo_y + lh

    y = logo_bottom + 25

    # ── "SCHEDULE UPDATE" header ───────────────────────────
    _, hh = centered_text_shadow(draw, y, "SCHEDULE UPDATE", f_header, GOLD)
    y += hh + 20

    # Decorative divider
    draw_hline(draw, y, MARGIN + 20, SIZE - MARGIN - 20, width=2)
    draw_diamond(draw, cx, y, r=6)
    y += 30

    # ── Content panel ──────────────────────────────────────
    panel_top = y
    panel_bottom = SIZE - INNER - 80
    draw_content_panel(img, MARGIN - 10, panel_top - 10,
                       SIZE - MARGIN + 10, panel_bottom,
                       radius=16, opacity=0.40)
    draw = ImageDraw.Draw(img)

    y += 20

    # ── "No longer attending" section ──────────────────────
    _, sh = centered_text(draw, y, "NO LONGER ATTENDING", f_sub, RED_MUTED)
    y += sh + 18

    # Strikethrough old show
    old_date = "APRIL 25"
    old_show = "ATX Card Show"
    old_loc = "Hilton Austin"

    bb = draw.textbbox((0, 0), old_date, font=f_date)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    ox = (SIZE - tw) // 2 - bb[0]
    draw_strikethrough_text(draw, (ox, y - bb[1]), old_date, f_date,
                            fill=DIM_CREAM, strike_fill=RED_MUTED)
    y += th + 8

    bb2 = draw.textbbox((0, 0), old_show, font=f_show)
    tw2 = bb2[2] - bb2[0]
    ox2 = (SIZE - tw2) // 2 - bb2[0]
    draw_strikethrough_text(draw, (ox2, y - bb2[1]), old_show, f_show,
                            fill=DIM_CREAM, strike_fill=RED_MUTED)
    y += (bb2[3] - bb2[1]) + 6

    _, lh = centered_text(draw, y, old_loc, f_loc, DIM_CREAM)
    y += lh + 30

    # Divider
    draw_hline(draw, y, MARGIN + 50, SIZE - MARGIN - 50, width=1)
    y += 30

    # ── "Now attending" section ────────────────────────────
    _, sh2 = centered_text_shadow(draw, y, "NOW ATTENDING", f_sub, GREEN_MUTED)
    y += sh2 + 18

    # New show details
    new_date = "APRIL 24–26"
    new_show = "Texoma Trading Card Expo"
    new_loc = "Choctaw Durant Event Center"

    _, dh = centered_text_shadow(draw, y, new_date, f_date, GOLD)
    y += dh + 10

    _, nh = centered_text(draw, y, new_show, f_show, CREAM)
    y += nh + 8

    _, nlh = centered_text(draw, y, new_loc, f_loc, DIM_CREAM)
    y += nlh + 30
    y += nlh + 30

    # ── Excited message ────────────────────────────────────
    _, bh = centered_text(draw, y, "Come see us there!", f_body, CREAM)
    y += bh

    # ── Bottom social handle ───────────────────────────────
    social_y = panel_bottom + 20
    _, _ = centered_text(draw, social_y, "@duganslegendaryden  •  dugansden.com",
                         f_social, DIM_CREAM)

    # ── Save ───────────────────────────────────────────────
    out_path = os.path.join(script_dir, "brand", "schedule_change.png")
    img.save(out_path, "PNG", dpi=(300, 300))
    print(f"Saved: {out_path}")
    print(f"Size:  {SIZE}x{SIZE}px")


if __name__ == "__main__":
    main()
