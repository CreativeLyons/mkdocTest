#!/usr/bin/env python3
"""Fix verified issues"""

import re
from pathlib import Path

DOCS_DIR = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/docs")

# Issues to fix - extracted from verification
FIXES = {
    # Missing videos - add video div after author line
    "3d/m-scatter-geo.md": {"video": ("_v-6UR_Mkj4", "youtube")},
    "3d/god-rays-projector.md": {"video": ("476747690", "vimeo")},
    "workflow-templates/advanced-keying-template.md": {"video": ("BKcKpPFVmCk", "youtube")},
    "merge/contact-sheet-auto.md": {"video": ("dqzzT169GAc", "youtube")},
    "cg/gluep.md": {"video": ("jakExzK9MMw", "youtube")},
    "color/blacks-match.md": {"video": ("Kw3bcsmkGuk", "youtube")},
    "color/gamma-plus.md": {"video": ("bhjwnHXHPxQ", "youtube")},
    "deep/deepboolean.md": {"video": ("354811205", "vimeo")},
    "time/frame-filler.md": {"video": ("VZSk7j1zOCU", "youtube")},
    "utilities/pyclopedia.md": {"video": ("icLr4uo6F-c", "youtube")},
    "filter/dehaze.md": {"video": ("GKLGd3dFSU4", "youtube")},
    "transform/cproject.md": {"video": ("N-_M2lJWpe4", "youtube")},
    "transform/roto-centroid.md": {"video": ("McDI_qb3ycE", "youtube")},
    "transform/rp-reformat.md": {"video": ("vGZ6kNnOcTs", "youtube")},
    "transform/tproject.md": {"video": ("N-_M2lJWpe4", "youtube")},
    "transform/card-to-track.md": {"video": ("N-_M2lJWpe4", "youtube")},
    "transform/iidistort.md": {"video": ("p3Lv7ThKbUk", "youtube")},
    "draw/noise-advanced.md": {"video": ("EsHDBGonwEs", "youtube")},
    "draw/hagbarth/silk.md": {"video": ("195532256", "vimeo")},
    
    # Hero image fixes
    "transform/morph-dissolve.md": {"hero_image": "image121.png"},
    "transform/vector-math-tools.md": {"hero_image": "image33.png"},
    
    # Missing images
    "workflow-templates/gizmo-demo-scripts.md": {"add_image": "image145.jpg"},
}

def add_video(content, video_id, video_type, depth):
    """Add video div after author line"""
    prefix = "../" * depth
    video_div = f'<div class="video-container" data-video-id="{video_id}" data-video-type="{video_type}" data-thumbnail="{prefix}img/video-placeholder.jpg">\n</div>'
    
    # Find author line
    lines = content.split('\n')
    new_lines = []
    video_added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        if line.startswith('**Author:**') and not video_added:
            new_lines.append('')
            new_lines.append(video_div)
            video_added = True
    
    return '\n'.join(new_lines)

def fix_hero_image(content, correct_image, depth):
    """Replace first image with correct one"""
    prefix = "../" * depth
    
    # Find first image and replace
    pattern = r'!\[[^\]]*\]\([^\)]+/image\d+\.\w+\)'
    replacement = f'![{correct_image}]({prefix}img/tools/{correct_image})'
    
    # Only replace first occurrence
    match = re.search(pattern, content)
    if match:
        content = content[:match.start()] + replacement + content[match.end():]
    
    return content

def add_image(content, image_file, depth):
    """Add image after author line"""
    prefix = "../" * depth
    image_md = f'![{image_file}]({prefix}img/tools/{image_file})'
    
    lines = content.split('\n')
    new_lines = []
    added = False
    
    for line in lines:
        new_lines.append(line)
        if line.startswith('**Author:**') and not added:
            new_lines.append('')
            new_lines.append(image_md)
            added = True
    
    return '\n'.join(new_lines)

def fix_file(filepath, fixes):
    """Apply fixes to a file"""
    full_path = DOCS_DIR / filepath
    if not full_path.exists():
        print(f"  Not found: {filepath}")
        return False
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    depth = len(Path(filepath).parts) - 1
    
    if 'video' in fixes:
        video_id, video_type = fixes['video']
        if video_id not in content:
            content = add_video(content, video_id, video_type, depth)
    
    if 'hero_image' in fixes:
        content = fix_hero_image(content, fixes['hero_image'], depth)
    
    if 'add_image' in fixes:
        if fixes['add_image'] not in content:
            content = add_image(content, fixes['add_image'], depth)
    
    # Clean up
    while '\n\n\n' in content:
        content = content.replace('\n\n\n', '\n\n')
    
    with open(full_path, 'w') as f:
        f.write(content.strip() + '\n')
    
    return True

def main():
    fixed = 0
    for filepath, fixes in FIXES.items():
        if fix_file(filepath, fixes):
            print(f"Fixed: {filepath}")
            fixed += 1
    
    print(f"\nTotal fixed: {fixed}")

if __name__ == "__main__":
    main()
