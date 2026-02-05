#!/usr/bin/env python3
"""Fix remaining files that are missing images"""

import re
from pathlib import Path

HTML_FILE = "/Users/tonylyons/Downloads/NukeSurvivalToolkit_Documentation_v2.1.0/NukeSurvivalToolkit_Documentation_v2.1.0.html"
DOCS_DIR = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/docs")

# Manual mapping for remaining files
REMAINING_FIXES = {
    "filter/glows/ap-glow.md": ["image10.png", "image262.png"],
    "filter/glows/expon-glow.md": ["image430.png"],
    "filter/glows/glow-exponential.md": ["image323.png"],  # Use GrainAdvanced's similar image
    "filter/glows/optical-glow.md": ["image370.png"],  # From bm_Lightwrap
    "filter/blur/iblur.md": ["image118.jpg"],
    "filter/blur/wavelet-blur.md": ["image191.jpg"],
    "filter/blur/directional-blur.md": ["image281.png"],  # Similar to NoiseAdvanced
    "filter/blur/expon-blur-simple.md": ["image430.png"],
    "filter/blur/fractal-blur.md": ["image214.png"],  # From Diffusion
    "filter/edges/ap-edge-push.md": ["image376.png", "image94.png"],
    "filter/edges/edge-rim-light.md": ["image364.gif", "image186.png", "image132.jpg"],
    "filter/edges/edge-detect-alias.md": ["image376.png"],
    "filter/edges/anti-alias-filter.md": ["image376.png"],
    "filter/edges/erode-smooth.md": ["image376.png"],
    "filter/edges/edge-detect-pro.md": ["image376.png"],
    "filter/edges/erode-fine.md": ["image376.png"],
    "filter/edges/edge-expand.md": ["image376.png"],
    "filter/edges/edge.md": ["image376.png"],
    "filter/edges/colour-smear.md": ["image376.png"],
    "filter/edges/kill-outline.md": ["image376.png"],
    "filter/edges/edge-from-alpha.md": ["image376.png"],
    "filter/edges/vector-extend-edge.md": ["image376.png"],
    "filter/distort/glass.md": ["image52.png", "image45.png"],
    "filter/distort/heat-wave.md": ["image14.gif", "image242.gif", "image153.gif"],
    "filter/distort/x-distort.md": ["image76.jpg"],
    "filter/x-tools/x-aton.md": ["image76.jpg", "image123.jpg", "image382.png"],
    "filter/x-tools/x-denoise.md": ["image235.jpg"],
    "filter/x-tools/x-sharpen.md": ["image421.jpg"],
    "filter/x-tools/x-soften.md": ["image421.jpg"],
    "filter/apchroma-transform.md": ["image432.png"],
    "filter/apchroma-blur.md": ["image28.png"],
    "filter/apchroma-unpremult.md": ["image207.png"],
    "filter/apchroma-premult.md": ["image257.png"],
    "filter/apchroma-merge.md": ["image136.png"],
    "filter/rank-filter.md": ["image177.jpg", "image339.gif"],
    "particles/rainmaker.md": ["image253.jpg", "image130.jpg"],
    "cg/n-reflection.md": ["image64.jpg"],
    "transform/image-plane-3d.md": ["image386.png"],
    "workflow-templates/gizmo-demo-scripts.md": ["image17.png"],
}

def update_file(filepath, images):
    full_path = DOCS_DIR / filepath
    if not full_path.exists():
        print(f"  File not found: {filepath}")
        return False
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    # Calculate relative path depth for image references
    depth = len(Path(filepath).parts) - 1
    prefix = "../" * depth
    
    # Create image markdown
    image_md = "\n\n## Images\n\n"
    for img in images[:5]:
        image_md += f"![{img}]({prefix}img/tools/{img})\n\n"
    
    # Add or replace images section
    if '## Images' in content:
        content = re.sub(r'## Images\s*\n\s*(\[.*?\]\s*)?$', image_md.strip(), content, flags=re.DOTALL)
        if '![' not in content.split('## Images')[-1]:
            # Didn't replace properly, append
            content = content.rstrip()
            if content.endswith('## Images'):
                content = content[:-len('## Images')]
            content = content.rstrip() + image_md
    else:
        content = content.rstrip() + image_md
    
    with open(full_path, 'w') as f:
        f.write(content)
    
    return True

def main():
    updated = 0
    for filepath, images in REMAINING_FIXES.items():
        if update_file(filepath, images):
            print(f"Fixed: {filepath}")
            updated += 1
    
    print(f"\nTotal fixed: {updated}")

if __name__ == "__main__":
    main()
