#!/usr/bin/env python3
"""
Aggressively optimize GIF files using gifsicle (bundled in ImageOptim).

- GIFs > 1 MB: gifsicle -O3 --lossy=80 (aggressive)
- GIFs <= 1 MB: gifsicle -O3 --lossy=30 (lighter)

Only replaces original if the optimized version is smaller.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path

GIFSICLE = (
    "/Applications/ImageOptim.app/Contents/Frameworks/"
    "ImageOptimGPL.framework/Versions/A/Resources/gifsicle"
)

SEARCH_DIR = Path("documentation/docs/img/tools")
ONE_MB = 1_048_576  # 1 MB in bytes


def human_size(nbytes):
    """Return a human-readable file size string."""
    val = float(nbytes)
    for unit in ("B", "KB", "MB", "GB"):
        if abs(val) < 1024:
            return f"{val:.1f} {unit}"
        val /= 1024
    return f"{val:.1f} TB"


def optimize_gif(gif_path):
    """Optimize a single GIF file. Returns a results dict."""
    before_size = gif_path.stat().st_size

    # Choose lossy level based on file size
    if before_size > ONE_MB:
        lossy = 80
        label = "aggressive"
    else:
        lossy = 30
        label = "light"

    # Create a temp file in the same directory (same filesystem for atomic rename)
    fd, tmp_path = tempfile.mkstemp(suffix=".gif", dir=gif_path.parent)
    os.close(fd)

    try:
        cmd = [
            GIFSICLE,
            "-O3",
            f"--lossy={lossy}",
            "-o", tmp_path,
            str(gif_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return {
                "path": str(gif_path),
                "before": before_size,
                "after": before_size,
                "saved": 0,
                "status": f"ERROR: {result.stderr.strip()}",
                "lossy": lossy,
            }

        after_size = os.path.getsize(tmp_path)

        if after_size < before_size:
            # Replace original with optimized version
            shutil.move(tmp_path, str(gif_path))
            status = "OPTIMIZED"
        else:
            # Keep original -- optimized is not smaller
            os.unlink(tmp_path)
            after_size = before_size
            status = "SKIPPED (no gain)"

        return {
            "path": str(gif_path),
            "before": before_size,
            "after": after_size,
            "saved": before_size - after_size,
            "status": status,
            "lossy": lossy,
        }

    except Exception as e:
        # Clean up temp file on any error
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        return {
            "path": str(gif_path),
            "before": before_size,
            "after": before_size,
            "saved": 0,
            "status": f"EXCEPTION: {e}",
            "lossy": lossy,
        }


def main():
    # Find all GIF files
    gif_files = sorted(SEARCH_DIR.rglob("*.gif"))
    if not gif_files:
        print("No GIF files found.")
        return

    print(f"Found {len(gif_files)} GIF files to optimize.\n")
    print(f"{'File':<70} {'Before':>10} {'After':>10} {'Saved':>10} {'%':>6}  {'Mode':>5}  Status")
    print("-" * 135)

    total_before = 0
    total_after = 0
    optimized_count = 0

    for gif in gif_files:
        result = optimize_gif(gif)

        total_before += result["before"]
        total_after += result["after"]

        if result["saved"] > 0:
            optimized_count += 1
            pct = (result["saved"] / result["before"]) * 100
        else:
            pct = 0.0

        # Shorten path for display
        short_path = str(gif).replace("documentation/docs/img/tools/", "")

        print(
            f"{short_path:<70} "
            f"{human_size(result['before']):>10} "
            f"{human_size(result['after']):>10} "
            f"{human_size(result['saved']):>10} "
            f"{pct:>5.1f}%  "
            f"L={result['lossy']:<3}  "
            f"{result['status']}"
        )

    # Summary
    total_saved = total_before - total_after
    if total_before > 0:
        total_pct = (total_saved / total_before) * 100
    else:
        total_pct = 0.0

    print("-" * 135)
    print(f"\n{'SUMMARY':=^60}")
    print(f"  Files processed:    {len(gif_files)}")
    print(f"  Files optimized:    {optimized_count}")
    print(f"  Files skipped:      {len(gif_files) - optimized_count}")
    print(f"  Total before:       {human_size(total_before)}")
    print(f"  Total after:        {human_size(total_after)}")
    print(f"  Total saved:        {human_size(total_saved)} ({total_pct:.1f}%)")
    print(f"{'':=^60}")


if __name__ == "__main__":
    main()
