#!/usr/bin/env python3
"""
Convert GIF files to animated WebP using gif2webp (libwebp).
Only converts files where WebP is smaller. Skips the 4 known losers.
Updates markdown references and rename_map.txt.
"""

import subprocess
import os
import re
import tempfile
from pathlib import Path

IMG_DIR = Path("documentation/docs/img/tools")
DOCS_DIR = Path("documentation/docs")
RENAME_MAP = Path("rename_map.txt")

# These GIFs are LARGER as WebP — skip them
SKIP_LIST = {
    "filter/deflicker-velocity-1.gif",
    "curves/wavemachine-6.gif",
    "curves/wavemachine-10.gif",
    "filter/mec-filler-3.gif",
}

GIF2WEBP = "gif2webp"


def main():
    converted = 0
    skipped_larger = 0
    skipped_known = 0
    total_before = 0
    total_after = 0
    errors = 0
    converted_files = []  # Track for markdown updates

    gif_files = sorted(IMG_DIR.rglob("*.gif"))
    print(f"Found {len(gif_files)} GIF files\n")

    for gif in gif_files:
        rel = str(gif.relative_to(IMG_DIR))
        gif_size = gif.stat().st_size

        # Skip known losers
        if rel in SKIP_LIST:
            skipped_known += 1
            print(f"  SKIP (known larger): {rel} ({gif_size//1024}KB)")
            continue

        webp_path = gif.with_suffix('.webp')

        try:
            # Use gif2webp with lossy compression, quality 80
            result = subprocess.run(
                [GIF2WEBP, "-lossy", "-q", "80", "-m", "4", str(gif), "-o", str(webp_path)],
                capture_output=True, text=True, timeout=120
            )

            if result.returncode != 0:
                print(f"  ERROR: {rel}: {result.stderr.strip()}")
                errors += 1
                if webp_path.exists():
                    webp_path.unlink()
                continue

            webp_size = webp_path.stat().st_size

            # Only keep if smaller
            if webp_size < gif_size:
                savings = (1 - webp_size / gif_size) * 100
                print(f"  {rel}: {gif_size//1024}KB -> {webp_size//1024}KB ({savings:.0f}% smaller)")
                gif.unlink()
                total_before += gif_size
                total_after += webp_size
                converted += 1
                converted_files.append(rel)
            else:
                print(f"  SKIP (WebP larger): {rel}: {gif_size//1024}KB -> {webp_size//1024}KB")
                webp_path.unlink()
                skipped_larger += 1

        except Exception as e:
            print(f"  ERROR: {rel}: {e}")
            errors += 1
            if webp_path.exists():
                webp_path.unlink()

    # Update markdown references for converted files
    print(f"\nUpdating markdown references...")
    md_files_updated = 0
    md_refs_updated = 0

    for md in DOCS_DIR.rglob("*.md"):
        content = md.read_text(errors='replace')
        original = content

        for gif_rel in converted_files:
            gif_name = Path(gif_rel).name
            webp_name = gif_name.replace('.gif', '.webp')
            content = content.replace(gif_name, webp_name)

        if content != original:
            md.write_text(content)
            md_files_updated += 1
            # Count changes
            for gif_rel in converted_files:
                gif_name = Path(gif_rel).name
                md_refs_updated += original.count(gif_name)

    print(f"  Updated {md_refs_updated} references in {md_files_updated} markdown files")

    # Update rename_map.txt
    print(f"\nUpdating rename_map.txt...")
    rmap_updated = 0
    if RENAME_MAP.exists():
        content = RENAME_MAP.read_text()
        for gif_rel in converted_files:
            gif_name = Path(gif_rel).name
            webp_name = gif_name.replace('.gif', '.webp')
            if gif_name in content:
                content = content.replace(f" -> {gif_name}", f" -> {webp_name}")
                rmap_updated += 1
        RENAME_MAP.write_text(content)
    print(f"  Updated {rmap_updated} entries")

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Converted to WebP: {converted}")
    print(f"  Skipped (known larger): {skipped_known}")
    print(f"  Skipped (measured larger): {skipped_larger}")
    print(f"  Errors: {errors}")
    if total_before > 0:
        print(f"  Size before: {total_before/1024/1024:.2f} MB")
        print(f"  Size after:  {total_after/1024/1024:.2f} MB")
        print(f"  Saved:       {(total_before-total_after)/1024/1024:.2f} MB ({(1-total_after/total_before)*100:.1f}%)")
    print(f"  Markdown files updated: {md_files_updated}")
    print(f"  Remaining GIF files: {skipped_known + skipped_larger}")


if __name__ == "__main__":
    main()
