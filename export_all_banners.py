"""
Export all three banner HTML files as high-resolution PNGs for print at 150 DPI.

Banners:
  1. popup_display.html         — 7.5' × 7.5' (90in × 90in)  → 13,500 × 13,500 px
  2. popup_banner_3x6.html      — 3' × 6' (36in × 72in)      → 5,400 × 10,800 px
  3. popup_banner_120x200.html  — 120cm × 200cm (47.24in × 78.74in) → 7,087 × 11,811 px

Strategy: Render at 4x CSS scale via headless Chrome, then upscale to final
print size using Pillow LANCZOS resampling.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

RENDER_SCALE = 4
DPI = 150

# Each banner: (html_file, css_width, css_height, final_width, final_height, output_name, label)
BANNERS = [
    (
        "popup_display.html",
        750, 750,
        13500, 13500,
        "brand/popup_display_highres.png",
        "7.5' × 7.5' Pop-Up Display"
    ),
    (
        "popup_banner_3x6.html",
        450, 900,
        5400, 10800,
        "brand/popup_banner_3x6_highres.png",
        "3' × 6' Retractable Banner"
    ),
    (
        "popup_banner_120x200.html",
        450, 750,
        7087, 11811,
        "brand/popup_banner_120x200_highres.png",
        "120cm × 200cm Retractable Banner"
    ),
]

script_dir = os.path.dirname(os.path.abspath(__file__))

# Set up Chrome once, reuse for all banners
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument(f"--force-device-scale-factor={RENDER_SCALE}")
options.add_argument("--hide-scrollbars")
# Window big enough for the largest banner (750*4 = 3000)
options.add_argument(f"--window-size={750 * RENDER_SCALE + 100},{900 * RENDER_SCALE + 200}")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    for html_file, css_w, css_h, final_w, final_h, output_name, label in BANNERS:
        html_path = os.path.join(script_dir, html_file)
        html_url = "file:///" + html_path.replace("\\", "/")
        render_path = os.path.join(script_dir, f"_temp_render_{os.path.basename(output_name)}")
        final_path = os.path.join(script_dir, output_name)

        print(f"\n{'='*60}")
        print(f"Exporting: {label}")
        print(f"  HTML: {html_file}")
        print(f"  Step 1: Render at {RENDER_SCALE}x ({css_w}px → {css_w * RENDER_SCALE}px)")
        print(f"  Step 2: Upscale to {final_w} × {final_h} px (150 DPI)")

        driver.get(html_url)
        time.sleep(3)  # Wait for fonts to load

        display_element = driver.find_element("css selector", ".display")
        display_element.screenshot(render_path)

        w_rendered = css_w * RENDER_SCALE
        h_rendered = css_h * RENDER_SCALE
        print(f"  Render complete: {w_rendered} × {h_rendered} px")

        # Upscale with Pillow
        print(f"  Upscaling with LANCZOS resampling...")
        img = Image.open(render_path)
        img_upscaled = img.resize((final_w, final_h), Image.LANCZOS)
        img_upscaled.save(final_path, dpi=(DPI, DPI))

        # Clean up temp
        os.remove(render_path)

        size_mb = os.path.getsize(final_path) / (1024 * 1024)
        print(f"  Saved: {final_path}")
        print(f"  File size: {size_mb:.1f} MB")
        print(f"  Resolution: {final_w} × {final_h} px @ {DPI} DPI")

finally:
    driver.quit()

print(f"\n{'='*60}")
print("All banners exported successfully!")
