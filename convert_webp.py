#!/usr/bin/env python3
"""Convert all PNG images to WebP, update markdown references, and update rename_map.txt."""

import os
import glob
import re
from pathlib import Path
from PIL import Image

WORKSPACE = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest")
IMG_DIR = WORKSPACE / "documentation" / "docs" / "img" / "tools"
DOCS_DIR = WORKSPACE / "documentation" / "docs"
RENAME_MAP = WORKSPACE / "rename_map.txt"


def convert_pngs():
    """Convert all PNGs to WebP, delete originals, return stats."""
    png_files = sorted(IMG_DIR.rglob("*.png"))
    total_before = 0
    total_after = 0
    converted = 0
    errors = []

    print(f"Found {len(png_files)} PNG files to convert.\n")

    for png_path in png_files:
        webp_path = png_path.with_suffix(".webp")
        png_size = png_path.stat().st_size

        try:
            img = Image.open(png_path)
            img.save(webp_path, "WEBP", lossless=True)

            # Verify the webp was created and is valid
            verify_img = Image.open(webp_path)
            verify_img.verify()

            webp_size = webp_path.stat().st_size
            total_before += png_size
            total_after += webp_size
            converted += 1

            rel = png_path.relative_to(WORKSPACE)
            savings_pct = (1 - webp_size / png_size) * 100 if png_size > 0 else 0
            print(f"  {rel}: {png_size:,} -> {webp_size:,} bytes ({savings_pct:+.1f}%)")

            # Delete the original PNG
            png_path.unlink()

        except Exception as e:
            errors.append((str(png_path), str(e)))
            print(f"  ERROR {png_path}: {e}")

    return converted, total_before, total_after, errors


def update_markdown_files():
    """Replace .png with .webp in all markdown files under docs/."""
    md_files = sorted(DOCS_DIR.rglob("*.md"))
    files_changed = 0
    refs_changed = 0

    for md_path in md_files:
        text = md_path.read_text(encoding="utf-8")
        # Replace .png with .webp in image paths and alt text
        new_text = text.replace(".png", ".webp")
        if new_text != text:
            count = text.count(".png")
            refs_changed += count
            files_changed += 1
            md_path.write_text(new_text, encoding="utf-8")
            rel = md_path.relative_to(WORKSPACE)
            print(f"  {rel}: {count} reference(s) updated")

    return files_changed, refs_changed


def update_rename_map():
    """Replace .png with .webp in the new-name column (right side of ' -> ')."""
    if not RENAME_MAP.exists():
        print("  rename_map.txt not found, skipping.")
        return 0

    lines = RENAME_MAP.read_text(encoding="utf-8").splitlines()
    new_lines = []
    changed = 0

    for line in lines:
        if " -> " in line:
            left, right = line.split(" -> ", 1)
            if right.endswith(".png"):
                right = right[:-4] + ".webp"
                changed += 1
            new_lines.append(f"{left} -> {right}")
        else:
            new_lines.append(line)

    RENAME_MAP.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return changed


def fmt_size(b):
    """Format bytes to human readable."""
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def main():
    print("=" * 60)
    print("STEP 1: Converting PNG -> WebP (lossless)")
    print("=" * 60)
    converted, total_before, total_after, errors = convert_pngs()

    print()
    print("=" * 60)
    print("STEP 2: Updating markdown references")
    print("=" * 60)
    files_changed, refs_changed = update_markdown_files()

    print()
    print("=" * 60)
    print("STEP 3: Updating rename_map.txt")
    print("=" * 60)
    map_changed = update_rename_map()
    print(f"  {map_changed} entries updated in rename_map.txt")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    savings = total_before - total_after
    pct = (savings / total_before * 100) if total_before > 0 else 0
    print(f"  Images converted:     {converted}")
    print(f"  Total size before:    {fmt_size(total_before)} ({total_before:,} bytes)")
    print(f"  Total size after:     {fmt_size(total_after)} ({total_after:,} bytes)")
    print(f"  Total savings:        {fmt_size(savings)} ({pct:.1f}%)")
    print(f"  Markdown files updated: {files_changed}")
    print(f"  Markdown refs changed:  {refs_changed}")
    print(f"  Rename map entries:     {map_changed}")
    if errors:
        print(f"  ERRORS:               {len(errors)}")
        for path, err in errors:
            print(f"    {path}: {err}")
    else:
        print(f"  Errors:               0")
    print("=" * 60)


if __name__ == "__main__":
    main()
