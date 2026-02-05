#!/usr/bin/env python3
"""
Resize oversized images. Max width = 1600px (2x retina for 800px content area).
For images displayed at <=400px in Google Doc, cap at 800px instead.
Only resizes PNGs and JPGs — GIFs are already small dimensions.
"""

import re
import os
from pathlib import Path
from PIL import Image

IMG_DIR = Path("documentation/docs/img/tools")
GDOC_HTML = Path("/Users/tonylyons/Downloads/NukeSurvivalToolkit_Documentation_v2.1.0/NukeSurvivalToolkit_Documentation_v2.1.0.html")
RENAME_MAP = Path("rename_map.txt")

MAX_WIDTH = 1600
SMALL_DISPLAY_THRESHOLD = 400  # If displayed <= this in GDoc, cap at 800px
SMALL_MAX_WIDTH = 800

def load_gdoc_display_sizes():
    """Parse Google Doc HTML to get display widths for each image."""
    html = GDOC_HTML.read_text(encoding="utf-8", errors="replace")
    sizes = {}
    for m in re.finditer(
        r'<img[^>]*src="images/(image\d+\.\w+)"[^>]*style="([^"]*)"',
        html
    ):
        img_name = m.group(1)
        style = m.group(2)
        w_match = re.search(r'width:\s*([\d.]+)px', style)
        if w_match:
            sizes[img_name] = float(w_match.group(1))
    return sizes

def load_rename_map():
    """old_name -> new_name"""
    rmap = {}
    if RENAME_MAP.exists():
        for line in RENAME_MAP.read_text().strip().split('\n'):
            if ' -> ' in line:
                old, new = line.split(' -> ', 1)
                rmap[old.strip()] = new.strip()
    return rmap

def get_max_width_for_image(img_path, gdoc_sizes, rmap_reverse):
    """Determine the max width for this image based on Google Doc display size."""
    # Find the original image name to look up in Google Doc
    current_name = img_path.name
    original_name = rmap_reverse.get(current_name)

    if original_name and original_name in gdoc_sizes:
        display_width = gdoc_sizes[original_name]
        if display_width <= SMALL_DISPLAY_THRESHOLD:
            return SMALL_MAX_WIDTH

    return MAX_WIDTH

def main():
    gdoc_sizes = load_gdoc_display_sizes()
    rmap = load_rename_map()
    rmap_reverse = {v: k for k, v in rmap.items()}

    resized = 0
    skipped = 0
    total_saved = 0

    print(f"{'='*70}")
    print(f"Image Resize Pass")
    print(f"Default max width: {MAX_WIDTH}px")
    print(f"Small-display max width: {SMALL_MAX_WIDTH}px (for images shown <= {SMALL_DISPLAY_THRESHOLD}px in GDoc)")
    print(f"{'='*70}\n")

    for img_path in sorted(IMG_DIR.rglob("*")):
        if img_path.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
            continue

        try:
            with Image.open(img_path) as img:
                w, h = img.size

                max_w = get_max_width_for_image(img_path, gdoc_sizes, rmap_reverse)

                if w <= max_w:
                    skipped += 1
                    continue

                # Calculate new dimensions maintaining aspect ratio
                ratio = max_w / w
                new_w = max_w
                new_h = int(h * ratio)

                before_size = img_path.stat().st_size

                # Resize
                resized_img = img.resize((new_w, new_h), Image.LANCZOS)

                # Save (strip metadata by not copying info/exif)
                if img_path.suffix.lower() == '.png':
                    resized_img.save(img_path, 'PNG', optimize=True)
                else:
                    resized_img.save(img_path, 'JPEG', quality=85, optimize=True)

                after_size = img_path.stat().st_size
                saved = before_size - after_size
                total_saved += saved
                resized += 1

                cap_label = f"(small-display cap {max_w}px)" if max_w == SMALL_MAX_WIDTH else ""
                print(f"  {img_path.relative_to(IMG_DIR)}: {w}x{h} -> {new_w}x{new_h} "
                      f"| {before_size//1024}KB -> {after_size//1024}KB "
                      f"(saved {saved//1024}KB) {cap_label}")

        except Exception as e:
            print(f"  ERROR: {img_path.relative_to(IMG_DIR)}: {e}")

    print(f"\n{'='*70}")
    print(f"RESIZE SUMMARY")
    print(f"{'='*70}")
    print(f"  Resized: {resized} files")
    print(f"  Skipped (already small): {skipped} files")
    print(f"  Total saved: {total_saved:,} bytes ({total_saved/1024/1024:.2f} MB)")

if __name__ == "__main__":
    main()
