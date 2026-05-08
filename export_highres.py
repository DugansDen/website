"""
Export popup_display.html as a high-resolution PNG for print.
Target: 7.5ft x 7.5ft (90in x 90in) at 150 DPI = 13,500 x 13,500 pixels.

Strategy: Render at 4x scale (3000px) to stay within Chrome's memory limits,
then upscale to 13,500px using Pillow with LANCZOS resampling.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

# Config
RENDER_SCALE = 4       # 750 * 4 = 3000px (safe for Chrome)
FINAL_SIZE = 13500     # 150 DPI at 90 inches
OUTPUT_RENDER = "brand/popup_display_render.png"
OUTPUT_FINAL = "brand/popup_display_highres.png"

# Get absolute path to the HTML file
script_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(script_dir, "popup_display.html")
html_url = "file:///" + html_path.replace("\\", "/")

print(f"Rendering: {html_path}")
print(f"Step 1: Render at {RENDER_SCALE}x (750px -> {750 * RENDER_SCALE}px)")
print(f"Step 2: Upscale to {FINAL_SIZE}x{FINAL_SIZE}px with LANCZOS")

# Set up Chrome in headless mode
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument(f"--force-device-scale-factor={RENDER_SCALE}")
options.add_argument("--hide-scrollbars")
# Window size is in screen pixels; with 4x scale, CSS viewport = window/4
# Need at least 750 CSS px wide, so window must be 750*4 = 3000+ screen px
options.add_argument(f"--window-size={750 * RENDER_SCALE + 100},{750 * RENDER_SCALE + 200}")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(html_url)
    time.sleep(3)  # Wait for fonts to load

    # Find the .display element and screenshot just that
    display_element = driver.find_element("css selector", ".display")

    # Save the intermediate render
    render_path = os.path.join(script_dir, OUTPUT_RENDER)
    display_element.screenshot(render_path)
    print(f"\nRender complete: {750 * RENDER_SCALE}px")

finally:
    driver.quit()

# Step 2: Upscale with Pillow
print("Upscaling with LANCZOS resampling...")
img = Image.open(render_path)
w, h = img.size
print(f"Source size: {w} x {h}")

# Element should be square (750x750 CSS); verify and upscale proportionally
if w == h:
    img_upscaled = img.resize((FINAL_SIZE, FINAL_SIZE), Image.LANCZOS)
    out_w, out_h = FINAL_SIZE, FINAL_SIZE
else:
    # Keep aspect ratio, scale based on the larger dimension
    scale = FINAL_SIZE / max(w, h)
    out_w = round(w * scale)
    out_h = round(h * scale)
    print(f"WARNING: Source is not square ({w}x{h}). Upscaling proportionally to {out_w}x{out_h}")
    img_upscaled = img.resize((out_w, out_h), Image.LANCZOS)

# Set DPI metadata to 150
final_path = os.path.join(script_dir, OUTPUT_FINAL)
img_upscaled.save(final_path, dpi=(150, 150))

# Clean up intermediate file
os.remove(render_path)

size_mb = os.path.getsize(final_path) / (1024 * 1024)
print(f"\nSuccess! Saved to: {final_path}")
print(f"File size: {size_mb:.1f} MB")
print(f"Resolution: {out_w} x {out_h} pixels")
print(f"DPI: 150 (embedded in file)")
print(f"Print size: 90 x 90 inches (7.5 x 7.5 feet)")
