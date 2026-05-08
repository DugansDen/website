"""
Build a 150x150 tile PNG with alternating pokeball and fire energy symbols
on a checkerboard diagonal grid, for use as a CSS background-image.
Both source images are converted to black silhouettes on transparent background.
"""

from PIL import Image, ImageDraw
import os

TILE = 150  # tile size in px
ICON = 50   # icon size within each 75x75 cell
script_dir = os.path.dirname(os.path.abspath(__file__))


def to_silhouette(path, size):
    """Load an image and convert all non-transparent content to a black silhouette."""
    img = Image.open(path).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rp = result.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < 30:
                continue
            # Skip near-white background pixels (the pokeball has a light gray bg)
            brightness = (r + g + b) / 3
            if brightness > 230 and a > 200:
                continue
            # Everything else becomes black
            rp[x, y] = (0, 0, 0, a)

    # Crop to bounding box
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)

    # Resize to fit within target size, maintaining aspect ratio
    rw, rh = result.size
    scale = min(size / rw, size / rh)
    new_w = int(rw * scale)
    new_h = int(rh * scale)
    result = result.resize((new_w, new_h), Image.LANCZOS)

    # Center on a square canvas
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ox = (size - new_w) // 2
    oy = (size - new_h) // 2
    canvas.paste(result, (ox, oy), result)
    return canvas


def load_fire_silhouette(size):
    """Load fire energy image—extract just the dark flame (ignore the red circle)."""
    fire_path = os.path.join(script_dir, "brand", "Fire energy symbol.png")
    img = Image.open(fire_path).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rp = result.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < 128:
                continue
            # Dark pixels are the flame
            brightness = (r + g + b) / 3
            if brightness < 80:
                rp[x, y] = (0, 0, 0, 255)

    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)

    rw, rh = result.size
    scale = min(size / rw, size / rh)
    new_w = int(rw * scale)
    new_h = int(rh * scale)
    result = result.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ox = (size - new_w) // 2
    oy = (size - new_h) // 2
    canvas.paste(result, (ox, oy), result)
    return canvas


# Create the tile
tile = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))

# Load pokeball silhouette
pokeball_path = os.path.join(script_dir, "brand", "pokeball.png")
pokeball = to_silhouette(pokeball_path, ICON)

# Load fire energy silhouette
fire = load_fire_silhouette(ICON)

# Paste on checkerboard diagonals:
# Top-left & bottom-right = pokeball, top-right & bottom-left = fire
tile.paste(pokeball, (37 - ICON // 2, 37 - ICON // 2), pokeball)
tile.paste(pokeball, (112 - ICON // 2, 112 - ICON // 2), pokeball)
tile.paste(fire, (112 - ICON // 2, 37 - ICON // 2), fire)
tile.paste(fire, (37 - ICON // 2, 112 - ICON // 2), fire)

out_path = os.path.join(script_dir, "brand", "bg_tile.png")
tile.save(out_path)
print(f"Saved tile: {out_path} ({TILE}x{TILE}px)")
