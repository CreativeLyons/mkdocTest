#!/usr/bin/env python3
"""
Fix shared images that were erroneously duplicated across multiple pages.
Each of these images exists once in the Google Doc under a specific tool section,
but during conversion they were incorrectly placed on other pages too.

This script removes the wrong references and ensures the correct page has the image.
"""

import re
from pathlib import Path

DOCS_DIR = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/docs")

# Map: image file name pattern -> (correct page, [wrong pages to remove from])
# We match on the renamed image name as it appears in the markdown
FIXES = [
    # shared-filter-4.png = apEdgePush screenshot, wrongly on blur pages
    {
        "image_pattern": "shared-filter-4.png",
        "correct_page": "filter/edges/ap-edge-push.md",
        "wrong_pages": [
            "filter/blur/expon-blur-simple.md",
            "filter/blur/directional-blur.md",
            "filter/blur/fractal-blur.md",
            "filter/blur/iblur.md",
            "filter/blur/wavelet-blur.md",
        ],
    },
    # shared-filter-5.png = apEdgePush screenshot, wrongly on iblur
    {
        "image_pattern": "shared-filter-5.png",
        "correct_page": "filter/edges/ap-edge-push.md",
        "wrong_pages": [
            "filter/blur/iblur.md",
        ],
    },
    # shared-filter-7.png = EdgeDetectAlias screenshot, wrongly on 11 edge pages
    {
        "image_pattern": "shared-filter-7.png",
        "correct_page": "filter/edges/edge-detect-alias.md",
        "wrong_pages": [
            "filter/edges/anti-alias-filter.md",
            "filter/edges/colour-smear.md",
            "filter/edges/edge-detect-pro.md",
            "filter/edges/edge-expand.md",
            "filter/edges/edge-from-alpha.md",
            "filter/edges/edge.md",
            "filter/edges/erode-fine.md",
            "filter/edges/erode-smooth.md",
            "filter/edges/kill-outline.md",
            "filter/edges/vector-extend-edge.md",
            "filter/distort/x-distort.md",
        ],
    },
    # shared-filter-8.png = ExponGlow screenshot, wrongly on glow-exponential
    {
        "image_pattern": "shared-filter-8.png",
        "correct_page": "filter/glows/expon-glow.md",
        "wrong_pages": [
            "filter/glows/glow-exponential.md",
        ],
    },
    # shared-filter-6.png = bm_Lightwrap screenshot, wrongly on optical-glow
    {
        "image_pattern": "shared-filter-6.png",
        "correct_page": "filter/bm-lightwrap.md",
        "wrong_pages": [
            "filter/glows/optical-glow.md",
        ],
    },
    # shared-filter-2.png = BeautifulSkin screenshot, wrongly on x-tools pages
    {
        "image_pattern": "shared-filter-2.png",
        "correct_page": "filter/beautiful-skin.md",
        "wrong_pages": [
            "filter/x-tools/x-aton.md",
            "filter/x-tools/x-denoise.md",
        ],
    },
    # shared-filter-3.png = BeautifulSkin screenshot, wrongly on x-tools pages
    {
        "image_pattern": "shared-filter-3.png",
        "correct_page": "filter/beautiful-skin.md",
        "wrong_pages": [
            "filter/x-tools/x-aton.md",
            "filter/x-tools/x-denoise.md",
            "filter/x-tools/x-sharpen.md",
            "filter/x-tools/x-soften.md",
        ],
    },
    # shared-particles-1.jpg = ParticleLights screenshot, wrongly on rainmaker
    {
        "image_pattern": "shared-particles-1.jpg",
        "correct_page": "particles/particlelights.md",
        "wrong_pages": [
            "particles/rainmaker.md",
        ],
    },
    # shared-particles-2.jpg = ParticleLights screenshot, wrongly on rainmaker
    {
        "image_pattern": "shared-particles-2.jpg",
        "correct_page": "particles/particlelights.md",
        "wrong_pages": [
            "particles/rainmaker.md",
        ],
    },
    # contact-sheet-auto-2.jpg = EdgeDetectPRO AND Contact page (end)
    # It's in Google Doc under EdgeDetectPRO AND Contact
    # Currently: on contact-sheet-auto.md (wrong) and edge-detect-pro.md (correct as edge-detect-pro-2.jpg)
    # Remove from contact-sheet-auto.md
    {
        "image_pattern": "contact-sheet-auto-2.jpg",
        "correct_page": "filter/edges/edge-detect-pro.md",
        "wrong_pages": [
            "merge/contact-sheet-auto.md",
        ],
    },
]


def remove_image_line(content, image_pattern):
    """Remove markdown lines containing the image reference.
    Returns (new_content, lines_removed)."""
    lines = content.split('\n')
    new_lines = []
    removed = 0

    for line in lines:
        if image_pattern in line:
            removed += 1
            # Also skip if the next line would be empty (to avoid double blank lines)
            continue
        new_lines.append(line)

    # Clean up multiple consecutive blank lines
    result = '\n'.join(new_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result, removed


def main():
    total_removed = 0
    total_files = 0

    for fix in FIXES:
        img_pattern = fix["image_pattern"]
        correct = fix["correct_page"]
        wrong_pages = fix["wrong_pages"]

        print(f"\n{'='*70}")
        print(f"Image: {img_pattern}")
        print(f"Correct page: {correct}")
        print(f"Removing from: {len(wrong_pages)} wrong page(s)")

        # Verify the correct page has the image
        correct_path = DOCS_DIR / correct
        if correct_path.exists():
            correct_content = correct_path.read_text()
            if img_pattern in correct_content or img_pattern.replace('.jpg', '-2.jpg') in correct_content:
                print(f"  ✓ Correct page has the image")
            else:
                # For edge-detect-pro, the image was renamed to edge-detect-pro-2.jpg
                print(f"  ⚠ Correct page may not have image (could be renamed)")

        for wrong_page in wrong_pages:
            wrong_path = DOCS_DIR / wrong_page
            if not wrong_path.exists():
                print(f"  ✗ {wrong_page} - FILE NOT FOUND")
                continue

            content = wrong_path.read_text()
            if img_pattern not in content:
                print(f"  ✗ {wrong_page} - image not found in file (already removed?)")
                continue

            new_content, removed = remove_image_line(content, img_pattern)
            wrong_path.write_text(new_content)
            total_removed += removed
            total_files += 1
            print(f"  ✓ {wrong_page} - removed {removed} reference(s)")

    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Total files modified: {total_files}")
    print(f"Total references removed: {total_removed}")


if __name__ == "__main__":
    main()
