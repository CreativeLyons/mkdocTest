#!/usr/bin/env python3
"""Fix all tool pages with correct images from accurate mapping"""

import re
import os
import json
from pathlib import Path

DOCS_DIR = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/docs")

# Load accurate mapping
with open("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/accurate-image-mapping.json") as f:
    ACCURATE_MAP = json.load(f)

# Create normalized lookup
NORMALIZED_MAP = {}
for heading, images in ACCURATE_MAP.items():
    # Normalize: remove author tags, lowercase, remove special chars
    parts = heading.split()
    if parts:
        # Remove author tag (2-4 uppercase letters at end)
        if len(parts) > 1 and re.match(r'^[A-Z]{2,4}$', parts[-1]):
            name = ' '.join(parts[:-1])
        else:
            name = heading
        
        normalized = name.lower().replace(' ', '').replace('_', '').replace('-', '')
        NORMALIZED_MAP[normalized] = images

def normalize_filename(filename):
    """Normalize a markdown filename to match tool name"""
    # Remove .md, replace - with nothing, lowercase
    name = filename.replace('.md', '').replace('-', '').replace('_', '').lower()
    return name

def get_correct_images(filename, title):
    """Find correct images for a tool"""
    # Try filename first
    norm_file = normalize_filename(filename)
    if norm_file in NORMALIZED_MAP:
        return NORMALIZED_MAP[norm_file]
    
    # Try title (remove # and author tag)
    if title:
        title_clean = title.lstrip('# ').strip()
        parts = title_clean.split()
        if parts and len(parts) > 1 and re.match(r'^[A-Z]{2,4}$', parts[-1]):
            title_clean = ' '.join(parts[:-1])
        norm_title = title_clean.lower().replace(' ', '').replace('_', '').replace('-', '')
        if norm_title in NORMALIZED_MAP:
            return NORMALIZED_MAP[norm_title]
    
    return None

def fix_file(filepath):
    """Fix images in a single file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Get title
    title = ''
    for line in lines:
        if line.startswith('# '):
            title = line
            break
    
    # Get correct images
    correct_images = get_correct_images(filepath.name, title)
    if not correct_images:
        return None, "no mapping found"
    
    # Calculate image path prefix
    rel_path = filepath.relative_to(DOCS_DIR)
    depth = len(rel_path.parts) - 1
    prefix = "../" * depth
    
    # Remove old image references
    new_lines = []
    for line in lines:
        if not line.strip().startswith('!['):
            new_lines.append(line)
    
    # Find where to insert images (after author/website lines, before links/description)
    insert_pos = 0
    for i, line in enumerate(new_lines):
        if line.startswith('**Author:**') or line.startswith('**Website:**'):
            insert_pos = i + 1
        elif line.strip().startswith('- [http'):
            # Insert before links
            if insert_pos == 0:
                insert_pos = i
            break
    
    # Skip blank lines after author section
    while insert_pos < len(new_lines) and new_lines[insert_pos].strip() == '':
        insert_pos += 1
    
    # Create image markdown (max 2 hero images)
    hero_images = correct_images[:2]
    remaining_images = correct_images[2:]
    
    # Insert hero images
    image_lines = ['']
    for img in hero_images:
        image_lines.append(f'![{img}]({prefix}img/tools/{img})')
        image_lines.append('')
    
    new_lines = new_lines[:insert_pos] + image_lines + new_lines[insert_pos:]
    
    # Add remaining images at end if any
    if remaining_images:
        new_lines.append('')
        for img in remaining_images:
            new_lines.append(f'![{img}]({prefix}img/tools/{img})')
            new_lines.append('')
    
    # Clean up multiple blank lines
    result = '\n'.join(new_lines)
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')
    
    with open(filepath, 'w') as f:
        f.write(result.strip() + '\n')
    
    return correct_images, "fixed"

def main():
    fixed = 0
    not_found = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            if fname == 'index.md':
                continue
            if fname in ['about.md', 'installation.md', 'menus.md', 'techSpecs.md']:
                continue
            
            filepath = Path(root) / fname
            images, status = fix_file(filepath)
            
            if status == "fixed":
                fixed += 1
                print(f"Fixed: {filepath.name} -> {images[:2]}")
            else:
                not_found.append(filepath.name)
    
    print(f"\nTotal fixed: {fixed}")
    print(f"Not found: {len(not_found)}")
    if not_found:
        print("Files without mapping:")
        for f in not_found[:20]:
            print(f"  {f}")

if __name__ == "__main__":
    main()
