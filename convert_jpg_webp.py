#!/usr/bin/env python3
"""
Convert all JPG files to WebP (lossy q85) and update markdown references.
"""

import os
import re
from pathlib import Path
from PIL import Image

IMG_DIR = Path("documentation/docs/img/tools")
DOCS_DIR = Path("documentation/docs")
RENAME_MAP = Path("rename_map.txt")

def convert_jpgs():
    total_before = 0
    total_after = 0
    converted = 0
    errors = 0

    jpg_files = sorted(IMG_DIR.rglob("*.jpg"))
    print(f"Found {len(jpg_files)} JPG files to convert\n")

    for jpg in jpg_files:
        webp_path = jpg.with_suffix('.webp')
        before_size = jpg.stat().st_size
        total_before += before_size

        try:
            img = Image.open(jpg)
            img.save(webp_path, 'WEBP', quality=85, method=6)
            after_size = webp_path.stat().st_size
            total_after += after_size

            # Verify the webp is valid
            Image.open(webp_path).verify()

            # Delete original
            jpg.unlink()
            converted += 1

            savings = (1 - after_size / before_size) * 100
            print(f"  {jpg.relative_to(IMG_DIR)}: {before_size//1024}KB -> {after_size//1024}KB ({savings:.0f}% smaller)")

        except Exception as e:
            errors += 1
            print(f"  ERROR: {jpg.relative_to(IMG_DIR)}: {e}")
            # Clean up failed webp if it exists
            if webp_path.exists():
                webp_path.unlink()

    return converted, total_before, total_after, errors


def update_markdown():
    """Update all .jpg references to .webp in markdown files."""
    files_updated = 0
    refs_updated = 0

    for md in DOCS_DIR.rglob("*.md"):
        content = md.read_text(errors='replace')
        original = content

        # Replace .jpg in image paths and alt text
        # Matches: ![something.jpg](path/something.jpg) or data-thumbnail="path/something.jpg"
        new_content = re.sub(r'\.jpg(?=\)|\"|\'|\s)', '.webp', content)

        if new_content != original:
            md.write_text(new_content)
            count = content.count('.jpg') - new_content.count('.jpg')
            # More accurate count
            count = len(re.findall(r'\.jpg(?=\)|\"|\'|\s)', content))
            refs_updated += count
            files_updated += 1

    return files_updated, refs_updated


def update_rename_map():
    """Update .jpg -> .webp in rename_map.txt right-hand side."""
    if not RENAME_MAP.exists():
        return 0

    content = RENAME_MAP.read_text()
    lines = content.split('\n')
    updated = 0
    new_lines = []

    for line in lines:
        if ' -> ' in line and line.strip().endswith('.jpg'):
            line = line[:-4] + '.webp'
            updated += 1
        new_lines.append(line)

    RENAME_MAP.write_text('\n'.join(new_lines))
    return updated


def main():
    print("=" * 70)
    print("Converting all JPG files to WebP (lossy q85)")
    print("=" * 70)

    # 1. Convert files
    converted, before, after, errors = convert_jpgs()

    # 2. Update markdown
    print(f"\nUpdating markdown references...")
    md_files, md_refs = update_markdown()
    print(f"  Updated {md_refs} references in {md_files} markdown files")

    # 3. Update rename map
    print(f"\nUpdating rename_map.txt...")
    rmap_count = update_rename_map()
    print(f"  Updated {rmap_count} entries")

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Files converted: {converted}")
    print(f"  Errors: {errors}")
    print(f"  Size before: {before/1024/1024:.2f} MB")
    print(f"  Size after:  {after/1024/1024:.2f} MB")
    print(f"  Saved:       {(before-after)/1024/1024:.2f} MB ({(1-after/before)*100:.1f}%)")
    print(f"  Markdown files updated: {md_files}")
    print(f"  Rename map entries updated: {rmap_count}")


if __name__ == "__main__":
    main()
