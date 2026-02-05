#!/usr/bin/env python3
"""Fix remaining tools with manual mapping based on source doc"""

import re
import os
from pathlib import Path

DOCS_DIR = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/docs")

# Manual mapping from source document analysis
MANUAL_MAP = {
    # Particles
    "particles/rainmaker.md": ["image190.jpg", "image161.jpg"],
    "particles/deep2vp.md": ["image67.png", "image299.png"],
    
    # Filter - apChroma tools share parent images
    "filter/apchroma.md": ["image193.png", "image206.jpg"],
    "filter/apchroma-blur.md": ["image432.png"],
    "filter/apchroma-merge.md": ["image432.png"],
    "filter/apchroma-premult.md": ["image432.png"],
    "filter/apchroma-unpremult.md": ["image432.png"],
    "filter/apchroma-transform.md": ["image432.png"],
    "filter/rank-filter.md": ["image77.gif", "image339.gif"],
    
    # X_Tools
    "filter/x-tools/x-aton.md": ["image381.png", "image150.png"],
    "filter/x-tools/x-denoise.md": ["image381.png", "image150.png"],
    "filter/x-tools/x-sharpen.md": ["image381.png"],
    "filter/x-tools/x-soften.md": ["image381.png"],
    
    # Blur tools - some share images from Blur section header
    "filter/blur/iblur.md": ["image376.png", "image94.png"],
    "filter/blur/wavelet-blur.md": ["image376.png"],
    "filter/blur/fractal-blur.md": ["image376.png"],
    "filter/blur/expon-blur-simple.md": ["image376.png"],
    "filter/blur/directional-blur.md": ["image376.png"],
    
    # Edges
    "filter/edges/edge.md": ["image188.png"],
    "filter/edges/edge-expand.md": ["image188.png"],
    "filter/edges/edge-detect-alias.md": ["image188.png"],
    "filter/edges/edge-detect-pro.md": ["image188.png"],
    "filter/edges/edge-from-alpha.md": ["image188.png"],
    "filter/edges/edge-rim-light.md": ["image364.gif", "image186.png"],
    "filter/edges/erode-fine.md": ["image188.png"],
    "filter/edges/erode-smooth.md": ["image188.png"],
    "filter/edges/anti-alias-filter.md": ["image188.png"],
    "filter/edges/colour-smear.md": ["image188.png"],
    "filter/edges/kill-outline.md": ["image188.png"],
    "filter/edges/vector-extend-edge.md": ["image188.png"],
    "filter/edges/ap-edge-push.md": ["image376.png", "image94.png"],
    
    # Distort
    "filter/distort/glass.md": ["image52.png", "image45.png"],
    "filter/distort/heat-wave.md": ["image14.gif", "image242.gif"],
    "filter/distort/x-distort.md": ["image188.png"],
    
    # Glows
    "filter/glows/ap-glow.md": ["image10.png", "image262.png"],
    "filter/glows/expon-glow.md": ["image430.png"],
    "filter/glows/glow-exponential.md": ["image430.png"],
    "filter/glows/optical-glow.md": ["image370.png"],
    
    # Others
    "time/frame-median.md": ["image77.gif"],
    "channel/binary-alpha.md": [],  # No images in source
    "cg/n-reflection.md": ["image64.jpg"],
    "transform/image-plane-3d.md": ["image178.png"],
    "workflow-templates/gizmo-demo-scripts.md": [],
}

def fix_file(filepath, images):
    """Update file with correct images"""
    full_path = DOCS_DIR / filepath
    if not full_path.exists():
        print(f"  Not found: {filepath}")
        return False
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    # Remove all existing image references
    lines = content.split('\n')
    new_lines = [line for line in lines if not line.strip().startswith('![')]
    
    if not images:
        # No images - just clean up
        result = '\n'.join(new_lines)
        while '\n\n\n' in result:
            result = result.replace('\n\n\n', '\n\n')
        with open(full_path, 'w') as f:
            f.write(result.strip() + '\n')
        return True
    
    # Calculate depth for image paths
    depth = len(Path(filepath).parts) - 1
    prefix = "../" * depth
    
    # Find insert position (after author/website, before links)
    insert_pos = 0
    for i, line in enumerate(new_lines):
        if line.startswith('**Author:**') or line.startswith('**Website:**'):
            insert_pos = i + 1
        elif line.strip().startswith('- [http'):
            if insert_pos == 0:
                insert_pos = i
            break
    
    # Skip blank lines
    while insert_pos < len(new_lines) and new_lines[insert_pos].strip() == '':
        insert_pos += 1
    
    # Insert images
    image_lines = ['']
    for img in images[:2]:  # Max 2 hero images
        image_lines.append(f'![{img}]({prefix}img/tools/{img})')
        image_lines.append('')
    
    new_lines = new_lines[:insert_pos] + image_lines + new_lines[insert_pos:]
    
    # Clean up
    result = '\n'.join(new_lines)
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')
    
    with open(full_path, 'w') as f:
        f.write(result.strip() + '\n')
    
    return True

def main():
    fixed = 0
    for filepath, images in MANUAL_MAP.items():
        if fix_file(filepath, images):
            print(f"Fixed: {filepath} -> {images[:2] if images else 'NO IMAGES'}")
            fixed += 1
    
    print(f"\nTotal fixed: {fixed}")

if __name__ == "__main__":
    main()
