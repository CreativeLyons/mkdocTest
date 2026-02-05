#!/usr/bin/env python3
"""
Parse the Google Docs HTML export to map images to tools.
Uses heading IDs to accurately find tool sections.
"""

import re
import json

HTML_FILE = "/Users/tonylyons/Downloads/NukeSurvivalToolkit_Documentation_v2.1.0/NukeSurvivalToolkit_Documentation_v2.1.0.html"
OUTPUT_FILE = "/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/image-mapping.json"

def main():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find all h2 headings with IDs (these are tool headers)
    # Pattern: <h2 ... id="h.xxxxx"><span class="c8">ToolName TAG</span></h2>
    heading_pattern = r'<h2[^>]*id="(h\.[^"]+)"[^>]*><span[^>]*>([^<]+)</span></h2>'
    headings = list(re.finditer(heading_pattern, html))
    
    print(f"Found {len(headings)} h2 headings")
    
    tool_data = {}
    
    for i, match in enumerate(headings):
        heading_id = match.group(1)
        heading_text = match.group(2).strip()
        
        # Skip non-tool headings (like category headers, TOC, etc.)
        # Tool headings typically have author tags like TL, AP, MJT, etc.
        if not re.search(r'\s+(TL|AP|MJT|MHD|AG|SPIN|FR|XM|NKPD|BM|DR|EL|AK|FL|CF|RB|RK|FH|DB|LS|JP|MGA-EL|VARIOUS)\s*$', heading_text, re.IGNORECASE):
            continue
        
        # Extract tool name (remove author tag)
        tool_name = re.sub(r'\s+(TL|AP|MJT|MHD|AG|SPIN|FR|XM|NKPD|BM|DR|EL|AK|FL|CF|RB|RK|FH|DB|LS|JP|MGA-EL|VARIOUS)\s*$', '', heading_text, flags=re.IGNORECASE).strip()
        
        # Get the section from this heading to the next heading
        start_pos = match.end()
        if i + 1 < len(headings):
            end_pos = headings[i + 1].start()
        else:
            end_pos = len(html)
        
        section = html[start_pos:end_pos]
        
        # Extract images from this section
        # Pattern: src="images/imageXXX.ext" with optional alt text
        image_matches = re.findall(r'<img[^>]*alt="([^"]*)"[^>]*src="images/(image\d+\.\w+)"', section)
        if not image_matches:
            image_matches = re.findall(r'src="images/(image\d+\.\w+)"', section)
            images = [(img, '') for img in image_matches] if image_matches else []
        else:
            images = [(img[1], img[0]) for img in image_matches]
        
        # Also check for alt after src
        alt_after_src = re.findall(r'src="images/(image\d+\.\w+)"[^>]*alt="([^"]*)"', section)
        for img, alt in alt_after_src:
            if not any(i[0] == img for i in images):
                images.append((img, alt))
        
        if images:
            tool_data[tool_name] = {
                'images': [img[0] for img in images],
                'alt_texts': [img[1] for img in images if img[1]]
            }
    
    print(f"Mapped images for {len(tool_data)} tools")
    
    # Count totals
    total_images = sum(len(t['images']) for t in tool_data.values())
    print(f"Total images mapped: {total_images}")
    
    # Save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(tool_data, f, indent=2)
    
    print(f"Saved to {OUTPUT_FILE}")
    
    # Print first 10 tools as sample
    print("\nSample mappings:")
    for i, (tool, data) in enumerate(list(tool_data.items())[:15]):
        print(f"  {tool}: {data['images'][:3]}")

if __name__ == "__main__":
    main()
