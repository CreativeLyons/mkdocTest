#!/usr/bin/env python3
"""Accurately parse HTML to map each tool to its correct images"""

import re
from pathlib import Path

HTML_FILE = "/Users/tonylyons/Downloads/NukeSurvivalToolkit_Documentation_v2.1.0/NukeSurvivalToolkit_Documentation_v2.1.0.html"

def parse_tool_sections(html):
    """Parse HTML into distinct tool sections"""
    
    # Find all H2 headings with IDs (these mark tool sections)
    # Pattern: <h2 ...id="h.xxx"...>CONTENT</h2>
    h2_pattern = r'<h2[^>]*id="(h\.[^"]+)"[^>]*>(.*?)</h2>'
    
    matches = list(re.finditer(h2_pattern, html, re.DOTALL))
    
    tool_sections = {}
    
    for i, match in enumerate(matches):
        heading_id = match.group(1)
        heading_content = match.group(2)
        
        # Clean heading text
        heading_text = re.sub(r'<[^>]+>', '', heading_content)
        heading_text = re.sub(r'&nbsp;', ' ', heading_text)
        heading_text = heading_text.strip()
        
        # Skip TOC and non-tool headings
        if not heading_text or heading_text.isdigit():
            continue
        if heading_text.startswith('Table of') or 'Menu' in heading_text:
            continue
        
        # Extract tool name (before author tag like TL, AG, MHD, etc.)
        tool_match = re.match(r'^([A-Za-z0-9_\-\s]+?)(?:\s+[A-Z]{2,4})?$', heading_text)
        if tool_match:
            tool_name = tool_match.group(1).strip()
        else:
            tool_name = heading_text.split()[0] if heading_text.split() else heading_text
        
        # Get section content (from this H2 to next H2)
        start_pos = match.end()
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(html)
        
        section_content = html[start_pos:end_pos]
        
        # Find images in this section only
        images = re.findall(r'<img[^>]+src="images/(image\d+\.\w+)"', section_content)
        
        if images:
            # Normalize tool name for matching
            normalized = tool_name.lower().replace(' ', '').replace('_', '').replace('-', '')
            tool_sections[heading_text] = {
                'normalized': normalized,
                'images': images[:5],  # Max 5 images per tool
                'full_heading': heading_text
            }
    
    return tool_sections

def main():
    with open(HTML_FILE, 'r') as f:
        html = f.read()
    
    sections = parse_tool_sections(html)
    
    print(f"Found {len(sections)} tool sections with images")
    print("\nSample mappings:")
    
    # Print a few examples
    for heading, data in list(sections.items())[:10]:
        print(f"  {heading}: {data['images'][:2]}")
    
    # Save to JSON
    import json
    output = {heading: data['images'] for heading, data in sections.items()}
    
    with open('/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/accurate-image-mapping.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved to accurate-image-mapping.json")

if __name__ == "__main__":
    main()
