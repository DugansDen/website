"""
Generate a 1080x1080 Instagram post announcing the live inventory browser
at dugansden.com.

Layout:
  - Flame + pokéball tile background (matching brand style)
  - Vignette + corner ornaments
  - Logo top-left, @handle top-right
  - Large headline "BROWSE OUR INVENTORY"
  - Sub-tagline "Singles  •  Slabs  •  Sealed Products"
  - Frosted QR panel centred with scan prompt
  - URL below QR

Usage:  python make_inventory_post.py
Output: inventory_post.png
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

script_dir = os.path.dirname(os.path.abspath(__file__))

# ── Brand colours (match show_schedule / popup banner) ───────────────────────
BG_COLOR   = (173, 88, 30)
BG_DARK    = (120, 55, 12)
GOLD       = (227, 189, 77)
GOLD_DIM   = (180, 148, 55)
CREAM      = (255, 248, 240)
DIM_CREAM  = (225, 215, 200)
PANEL_BG   = (100, 45, 10)

SIZE = 1080

# ── Helpers (copied from make_show_schedule.py) ───────────────────────────────

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
    shadow_sprite = Image.new("RGBA", sprite.size, (0, 0, 0, int(255 * opacity)))
    shadow_sprite.putalpha(sprite.split()[3])
    shadow.paste(shadow_sprite, (sx + ox, sy + oy))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), shadow))
    canvas.paste(sprite, pos, sprite)


def draw_rounded_panel(img, x1, y1, x2, y2, radius=20, opacity=0.40):
    panel = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                         fill=(30, 15, 5, int(255 * opacity)))
    pd.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                         outline=(*GOLD_DIM, 200), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), panel))


def draw_diamond(draw, cx, cy, r=7):
    draw.polygon([(cx, cy - r), (cx + r, cy),
                  (cx, cy + r), (cx - r, cy)], fill=GOLD)


def draw_hline(draw, y, x1, x2, width=2):
    draw.line([(x1, y), (x2, y)], fill=GOLD, width=width)


def draw_corner_ornaments(draw, m, length=65, inset=0):
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


def measure(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_centered_text(draw, y, text, font, fill, shadow=True, cx=SIZE // 2, stroke=0):
    w, h = measure(draw, text, font)
    x = cx - w // 2
    bb = draw.textbbox((0, 0), text, font=font)
    x -= bb[0]
    if shadow:
        draw.text((x + 3, y + 3), text, fill=(30, 12, 0), font=font,
                  stroke_width=stroke, stroke_fill=(30, 12, 0))
    draw.text((x, y), text, fill=fill, font=font,
              stroke_width=stroke, stroke_fill=fill)
    return h


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    img = Image.new("RGB", (SIZE, SIZE), BG_COLOR)
    tile_background(img, os.path.join(script_dir, "brand", "bg_tile.png"), opacity=0.09)
    img = add_vignette(img, strength=0.6)
    draw = ImageDraw.Draw(img)

    BORDER = 20
    draw_corner_ornaments(draw, BORDER, length=65, inset=0)

    # ── Fonts ──────────────────────────────────────────────
    f_headline   = load_font("Cinzel-Bold.ttf",   82)
    f_subhead    = load_font("Cinzel-Bold.ttf",   32)
    f_scan_label = load_font("Lato-Bold.ttf",     32)
    f_url        = load_font("Lato-Light.ttf",    28)
    f_social     = load_font("Lato-Regular.ttf",  26)
    f_handle     = load_font("Lato-Regular.ttf",  26)

    # ── Logo (top-left) ────────────────────────────────────
    MARGIN_L = 65
    MARGIN_R = 60
    TOP_PAD  = BORDER + 16
    logo_bottom = TOP_PAD + 10

    logo_path = os.path.join(script_dir, "brand", "logo.png")
    if os.path.isfile(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        max_logo = 280
        scale = min(max_logo / logo.width, max_logo / logo.height)
        lw, lh = int(logo.width * scale), int(logo.height * scale)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        logo_x = MARGIN_L + 30
        logo_y = TOP_PAD
        add_drop_shadow(img, logo, (logo_x, logo_y), offset=(5, 5), blur=15, opacity=0.5)
        draw = ImageDraw.Draw(img)
        logo_bottom = logo_y + lh

    # ── Social handle (top-right, vertically centred to logo) ─────────────────
    handle_text = "@duganslegendaryden"
    web_text    = "dugansden.com"
    handle_w, handle_h = measure(draw, handle_text, f_handle)
    web_w,    web_h    = measure(draw, web_text,    f_social)

    social_right = SIZE - MARGIN_R - 40
    logo_mid_y   = TOP_PAD + (logo_bottom - TOP_PAD) // 2
    block_h      = handle_h + 10 + web_h
    social_top   = logo_mid_y - block_h // 2

    line_left = social_right - max(handle_w, web_w)
    draw_hline(draw, social_top - 14, line_left, social_right, width=1)
    draw.text((social_right - handle_w, social_top), handle_text,
              fill=CREAM, font=f_handle)
    draw.text((social_right - web_w, social_top + handle_h + 10), web_text,
              fill=DIM_CREAM, font=f_social)
    draw_hline(draw, social_top + block_h + 14, line_left, social_right, width=1)

    # ── Decorative divider below header row ───────────────────────────────────
    div_y = logo_bottom + 18
    draw_hline(draw, div_y, BORDER + 30, SIZE - BORDER - 30, width=1)
    draw_diamond(draw, SIZE // 2, div_y, r=8)

    # ── Headline ──────────────────────────────────────────────────────────────
    y = div_y + 28
    h = draw_centered_text(draw, y, "BROWSE OUR", f_headline, GOLD, stroke=2)
    y += h + 6
    h = draw_centered_text(draw, y, "INVENTORY", f_headline, GOLD, stroke=2)
    y += h + 36

    # ── Sub-tagline ───────────────────────────────────────────────────────────
    tagline = "Singles  \u2022  Slabs  \u2022  Sealed Products"
    h = draw_centered_text(draw, y, tagline, f_subhead, CREAM, shadow=False)
    y += h + 26

    # ── Frosted QR panel ──────────────────────────────────────────────────────
    QR_SIZE = 310
    panel_pad = 28
    panel_w = QR_SIZE + panel_pad * 2
    # Extra height for "Scan to browse" label above and URL below
    label_h = measure(draw, "Scan to browse", f_scan_label)[1]
    url_h   = measure(draw, "dugansden.com/inventory", f_url)[1]
    panel_inner_h = label_h + 18 + QR_SIZE + 20 + url_h
    panel_h = panel_inner_h + panel_pad * 2

    panel_x1 = (SIZE - panel_w) // 2
    panel_x2 = panel_x1 + panel_w
    panel_y1 = y
    panel_y2 = panel_y1 + panel_h

    draw_rounded_panel(img, panel_x1, panel_y1, panel_x2, panel_y2,
                       radius=24, opacity=0.42)
    draw = ImageDraw.Draw(img)

    # "Scan to browse" label
    inner_y = panel_y1 + panel_pad
    draw_centered_text(draw, inner_y, "Scan to browse", f_scan_label, GOLD)
    inner_y += label_h + 18

    # QR code (white padded background for scannability)
    qr_path = os.path.join(script_dir, "brand", "website_QRcode.png")
    if os.path.isfile(qr_path):
        qr = Image.open(qr_path).convert("RGBA")
        qr = qr.resize((QR_SIZE, QR_SIZE), Image.LANCZOS)

        # White backing so dark QR reads cleanly against any background
        qr_bg = Image.new("RGBA", (QR_SIZE + 16, QR_SIZE + 16), (255, 255, 255, 255))
        qr_bg.paste(qr, (8, 8), qr)

        qr_x = (SIZE - qr_bg.width) // 2
        qr_y = inner_y
        add_drop_shadow(img, qr_bg, (qr_x, qr_y), offset=(4, 4), blur=12, opacity=0.45)
        draw = ImageDraw.Draw(img)
        inner_y += qr_bg.height + 20

    # URL
    url_text = "dugansden.com/inventory"
    draw_centered_text(draw, inner_y, url_text, f_url, DIM_CREAM, shadow=False)

    # ── Bottom tagline (below panel, only if it fits) ─────────────────────────
    bottom_y = panel_y2 + 22
    bottom_text = "Browse anytime. Buy at the show."
    btw, bth = measure(draw, bottom_text, f_social)
    if bottom_y + bth < SIZE - BORDER - 20:
        draw_centered_text(draw, bottom_y, bottom_text, f_social, CREAM, shadow=False)

    # ── Save ──────────────────────────────────────────────────────────────────
    out_path = os.path.join(script_dir, "brand", "inventory_post.png")
    img.save(out_path, "PNG", optimize=True)
    print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
