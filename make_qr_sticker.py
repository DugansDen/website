"""Build a 3x3" circular black/white thermal-ready Arcanine QR sticker."""

from PIL import Image, ImageDraw, ImageFont
import math
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# 3x3 inches at 300 DPI
SIZE = 900
DPI = 300
INCLUDE_HANDLE = False


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


def main():
    # Load sources
    sticker_path = os.path.join(script_dir, "brand", "3x3_Circular_Sticker.png")
    qr_path = os.path.join(script_dir, "brand", "website_QRcode.png")

    sticker = Image.open(sticker_path).convert("RGBA")
    qr_raw = Image.open(qr_path).convert("RGBA")

    # Scale original sticker up to print resolution
    sticker = sticker.resize((SIZE, SIZE), Image.LANCZOS)

    # Work in RGBA for compositing, then convert to 1-bit B/W at end
    canvas = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 255))
    canvas.paste(sticker, (0, 0))
    draw = ImageDraw.Draw(canvas)

    # Preserve original art above this line, only rebuild lower section.
    clear_top = 548
    clear_bottom = 855

    # Only clear inside circle interior to preserve the outer ring.
    cx, cy = SIZE // 2, SIZE // 2
    circle_r = 414

    for py in range(clear_top, clear_bottom):
        dy = py - cy
        if abs(dy) >= circle_r:
            continue
        dx = int(math.sqrt(circle_r ** 2 - dy ** 2))
        x_left = max(cx - dx + 14, 0)
        x_right = min(cx + dx - 14, SIZE)
        draw.rectangle([x_left, py, x_right, py], fill=(255, 255, 255, 255))

    # Remove residual left-card edges without touching face/torso.
    draw.polygon(
        [(92, 500), (292, 500), (332, 604), (82, 604)],
        fill=(255, 255, 255, 255),
    )

    # Remove legacy lower banner arc remnants from original art.
    for py in range(756, 866):
        dy = py - cy
        if abs(dy) >= circle_r:
            continue
        dx = int(math.sqrt(circle_r ** 2 - dy ** 2))
        x_left = max(cx - dx + 18, 0)
        x_right = min(cx + dx - 18, SIZE)
        draw.rectangle([x_left, py, x_right, py], fill=(255, 255, 255, 255))

    # Lower, compact shipping box so Arcanine remains visually dominant.
    box_w, box_h = 360, 274
    box_x = (SIZE - box_w) // 2
    box_y = 534

    # Box body
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h],
                   fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=4)

    # Top flap and light perspective seams.
    flap_y = box_y + 54
    draw.line([box_x, flap_y, box_x + box_w, flap_y], fill=(0, 0, 0, 255), width=3)
    draw.line([box_x + 36, flap_y, box_x + 26, box_y + box_h - 26], fill=(0, 0, 0, 255), width=2)
    draw.line([box_x + box_w - 36, flap_y, box_x + box_w - 26, box_y + box_h - 26], fill=(0, 0, 0, 255), width=2)

    # Label panel for QR code.
    label_pad = 34
    label_x0 = box_x + label_pad
    label_y0 = flap_y + 20
    label_x1 = box_x + box_w - label_pad
    label_y1 = box_y + box_h - 24
    draw.rectangle([label_x0, label_y0, label_x1, label_y1],
                   fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)

    # QR sized to keep scanners happy on thermal prints.
    qr_size = min((label_x1 - label_x0) - 16, (label_y1 - label_y0) - 16)
    qr = qr_raw.resize((qr_size, qr_size), Image.NEAREST)

    qr_bw = qr.convert("L").point(lambda p: 255 if p > 170 else 0, mode="1").convert("RGBA")
    qr_bg = Image.new("RGBA", (qr_size, qr_size), (255, 255, 255, 255))
    qr_bg.paste(qr_bw, (0, 0))

    qr_x = label_x0 + ((label_x1 - label_x0 - qr_size) // 2)
    qr_y = label_y0 + ((label_y1 - label_y0 - qr_size) // 2)
    canvas.paste(qr_bg, (qr_x, qr_y))

    # Optional social handle in lower arc.
    if INCLUDE_HANDLE:
        font_handle = load_font("Lato-Bold.ttf", 34)
        handle = "@duganslegendaryden"
        bb = draw.textbbox((0, 0), handle, font=font_handle)
        tw = bb[2] - bb[0]
        th = bb[3] - bb[1]
        handle_x = (SIZE - tw) // 2 - bb[0]
        handle_y = 812

        # White backing for legibility in thermal print conversion
        draw.rectangle([handle_x - 5, handle_y - 2,
                        handle_x + tw + 5, handle_y + th + 2],
                       fill=(255, 255, 255, 255))
        draw.text((handle_x, handle_y - bb[1]), handle,
                  fill=(0, 0, 0, 255), font=font_handle)

        # Dots flanking handle (echoing the original stamp style)
        dot_y = handle_y + th // 2
        draw.ellipse([handle_x - 16, dot_y - 3, handle_x - 10, dot_y + 3],
                     fill=(0, 0, 0, 255))
        draw.ellipse([handle_x + tw + 10, dot_y - 3, handle_x + tw + 16, dot_y + 3],
                     fill=(0, 0, 0, 255))

    # Circular mask / crop
    mask = Image.new("L", (SIZE, SIZE), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([10, 10, SIZE - 10, SIZE - 10], fill=255)
    
    # White background, paste canvas through circular mask
    output = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 255))
    output.paste(canvas, (0, 0), mask)

    # Convert to 1-bit B&W for thermal printing
    output_bw = output.convert("L")
    output_1bit = output_bw.point(lambda p: 255 if p > 150 else 0, mode="1")

    # Save
    out_path = os.path.join(script_dir, "brand", "qr_sticker.png")
    output_1bit.save(out_path, "PNG", dpi=(DPI, DPI))
    print(f"Saved: {out_path}")
    print(f"Size:  {SIZE}x{SIZE}px  ({SIZE/DPI:.0f}x{SIZE/DPI:.0f}\" @ {DPI} DPI)")


if __name__ == "__main__":
    main()
