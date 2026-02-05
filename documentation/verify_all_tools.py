#!/usr/bin/env python3
"""Verify all tool pages against source document"""

import re
import os
from pathlib import Path

HTML_FILE = "/Users/tonylyons/Downloads/NukeSurvivalToolkit_Documentation_v2.1.0/NukeSurvivalToolkit_Documentation_v2.1.0.html"
DOCS_DIR = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/docs")

def parse_source_tools(html):
    """Parse all tools from source HTML"""
    tools = {}
    
    # Find all H2 headings with IDs
    h2s = list(re.finditer(r'<h2[^>]*id="(h\.[^"]+)"[^>]*>(.*?)</h2>', html, re.DOTALL))
    
    for i, h2 in enumerate(h2s):
        heading_text = re.sub(r'<[^>]+>', '', h2.group(2))
        heading_text = re.sub(r'&nbsp;', ' ', heading_text).strip()
        
        # Skip non-tool headings
        if not heading_text or 'Menu' in heading_text or heading_text.isdigit():
            continue
        if heading_text.startswith('Table of') or heading_text.startswith('1.') or heading_text.startswith('2.'):
            continue
        
        # Get section content
        start = h2.end()
        end = h2s[i+1].start() if i+1 < len(h2s) else len(html)
        section = html[start:end]
        
        # Extract data
        images = re.findall(r'images/(image\d+\.\w+)', section)
        
        # Get author
        author_match = re.search(r'Author:\s*([^<\n]+)', section)
        author = author_match.group(1).strip() if author_match else ""
        
        # Get nukepedia link
        nukepedia = re.search(r'nukepedia\.com/[^\s"<&]+', section, re.IGNORECASE)
        nukepedia_link = nukepedia.group(0) if nukepedia else ""
        
        # Get video
        vimeo = re.search(r'vimeo\.com/(\d+)', section)
        youtube = re.search(r'youtu\.?be[^\s"<]+', section)
        video_id = vimeo.group(1) if vimeo else (youtube.group(0) if youtube else "")
        
        # Normalize tool name for matching
        name_parts = heading_text.split()
        if len(name_parts) > 1 and re.match(r'^[A-Z]{2,4}$', name_parts[-1]):
            tool_name = ' '.join(name_parts[:-1])
        else:
            tool_name = heading_text
        
        normalized = tool_name.lower().replace(' ', '').replace('_', '').replace('-', '')
        
        tools[normalized] = {
            'heading': heading_text,
            'images': images[:5],
            'author': author,
            'nukepedia': nukepedia_link,
            'video': video_id
        }
    
    return tools

def check_markdown_file(filepath, source_tools):
    """Check a markdown file against source data"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    issues = []
    
    # Get tool name from filename
    fname = filepath.stem
    normalized = fname.lower().replace('-', '').replace('_', '')
    
    # Also try from title
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        name_parts = title.split()
        if len(name_parts) > 1 and re.match(r'^[A-Z]{2,4}$', name_parts[-1]):
            title_name = ' '.join(name_parts[:-1])
        else:
            title_name = title
        title_normalized = title_name.lower().replace(' ', '').replace('_', '').replace('-', '')
    else:
        title_normalized = normalized
    
    # Find matching source tool
    source = None
    for key in [normalized, title_normalized]:
        if key in source_tools:
            source = source_tools[key]
            break
    
    if not source:
        return None, "NO SOURCE MATCH"
    
    # Check images
    md_images = re.findall(r'!\[([^\]]*)\]\([^\)]+/(image\d+\.\w+)\)', content)
    md_image_files = [img[1] for img in md_images]
    
    source_images = source['images']
    
    # Check if first image matches (hero image)
    if source_images and md_image_files:
        if md_image_files[0] != source_images[0]:
            issues.append(f"Hero image mismatch: has {md_image_files[0]}, should be {source_images[0]}")
    elif source_images and not md_image_files:
        issues.append(f"Missing images, should have: {source_images[:2]}")
    
    # Check video
    if source['video']:
        if source['video'] not in content:
            issues.append(f"Missing video: {source['video']}")
    
    return source, issues if issues else "OK"

def main():
    with open(HTML_FILE, 'r') as f:
        html = f.read()
    
    print("Parsing source document...")
    source_tools = parse_source_tools(html)
    print(f"Found {len(source_tools)} tools in source\n")
    
    ok_count = 0
    issue_count = 0
    no_match = 0
    issues_list = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            if fname == 'index.md' or fname in ['about.md', 'installation.md', 'menus.md', 'techSpecs.md']:
                continue
            
            filepath = Path(root) / fname
            rel_path = filepath.relative_to(DOCS_DIR)
            
            source, result = check_markdown_file(filepath, source_tools)
            
            if result == "NO SOURCE MATCH":
                no_match += 1
            elif result == "OK":
                ok_count += 1
            else:
                issue_count += 1
                issues_list.append((str(rel_path), result))
    
    print(f"=== VERIFICATION RESULTS ===")
    print(f"✓ OK: {ok_count}")
    print(f"✗ Issues: {issue_count}")
    print(f"? No source match: {no_match}")
    print()
    
    if issues_list:
        print("=== ISSUES FOUND ===")
        for path, issues in issues_list[:30]:
            print(f"\n{path}:")
            for issue in issues:
                print(f"  - {issue}")
    else:
        print("All verified tools match source document!")

if __name__ == "__main__":
    main()
