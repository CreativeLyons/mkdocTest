#!/usr/bin/env python3
"""Restructure all tool pages to match source document order"""

import re
import os
from pathlib import Path
import json

DOCS_DIR = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/docs")

def parse_page(content):
    """Parse existing page into components"""
    result = {
        'title': '',
        'author_line': '',
        'website_line': '',
        'links': [],
        'video_div': '',
        'description': '',
        'images': []
    }
    
    lines = content.split('\n')
    current_section = None
    description_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Title (# Name)
        if stripped.startswith('# ') and not result['title']:
            result['title'] = stripped
            continue
        
        # Author line
        if stripped.startswith('**Author:**'):
            result['author_line'] = stripped
            continue
        
        # Website line
        if stripped.startswith('**Website:**'):
            result['website_line'] = stripped
            continue
        
        # Section headers
        if stripped == '## Links':
            current_section = 'links'
            continue
        elif stripped == '## Description':
            current_section = 'description'
            continue
        elif stripped == '## Demo' or stripped == '## Video':
            current_section = 'video'
            continue
        elif stripped == '## Images':
            current_section = 'images'
            continue
        elif stripped.startswith('## '):
            current_section = 'other'
            continue
        
        # Video div
        if '<div class="video-container"' in stripped or 'data-video-id' in stripped:
            result['video_div'] = stripped
            continue
        
        # Links section
        if current_section == 'links' and stripped.startswith('- ['):
            result['links'].append(stripped)
            continue
        
        # Description section
        if current_section == 'description' and stripped:
            description_lines.append(line)
            continue
        
        # Images section
        if current_section == 'images' and stripped.startswith('!['):
            result['images'].append(stripped)
            continue
    
    result['description'] = '\n'.join(description_lines).strip()
    
    return result

def build_page(components, depth=1):
    """Build restructured page from components"""
    lines = []
    prefix = "../" * depth
    
    # 1. Title (always first)
    lines.append(components['title'])
    lines.append('')
    
    # 2. Author info
    if components['author_line']:
        lines.append(components['author_line'])
    if components['website_line']:
        lines.append(components['website_line'])
    if components['author_line'] or components['website_line']:
        lines.append('')
    
    # 3. Hero section: Video OR 1-2 images
    if components['video_div']:
        lines.append('## Demo')
        lines.append('')
        lines.append(components['video_div'])
        lines.append('')
    elif components['images']:
        # Show max 2 images as hero
        hero_images = components['images'][:2]
        for img in hero_images:
            lines.append(img)
            lines.append('')
    
    # 4. Links section
    if components['links']:
        lines.append('## Links')
        lines.append('')
        for link in components['links']:
            lines.append(link)
        lines.append('')
    
    # 5. Description
    if components['description']:
        lines.append('## Description')
        lines.append('')
        lines.append(components['description'])
        lines.append('')
    
    # 6. Remaining images (after first 2 if no video, all if video)
    remaining_images = components['images'][2:] if not components['video_div'] else components['images']
    if remaining_images:
        lines.append('## Images')
        lines.append('')
        for img in remaining_images:
            lines.append(img)
            lines.append('')
    
    return '\n'.join(lines)

def process_file(filepath):
    """Process a single markdown file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    components = parse_page(content)
    
    # Skip if no title found (probably an index page)
    if not components['title']:
        return False
    
    # Calculate depth for image paths
    rel_path = filepath.relative_to(DOCS_DIR)
    depth = len(rel_path.parts) - 1
    
    new_content = build_page(components, depth)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

def main():
    updated = 0
    skipped = 0
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            if fname == 'index.md':
                skipped += 1
                continue
            if fname in ['about.md', 'installation.md', 'menus.md', 'techSpecs.md']:
                skipped += 1
                continue
            
            filepath = Path(root) / fname
            if process_file(filepath):
                updated += 1
                print(f"Updated: {filepath.relative_to(DOCS_DIR)}")
            else:
                skipped += 1
    
    print(f"\nTotal updated: {updated}")
    print(f"Total skipped: {skipped}")

if __name__ == "__main__":
    main()
