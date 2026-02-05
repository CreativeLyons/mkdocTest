#!/usr/bin/env python3
"""Fix paragraph breaks in descriptions to match source document"""

import re
import os
from pathlib import Path

DOCS_DIR = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/docs")

def fix_paragraphs(content):
    """Add proper paragraph breaks in description sections"""
    lines = content.split('\n')
    new_lines = []
    in_description = False
    prev_was_text = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detect when we're past the links and into description
        if stripped.startswith('- [http'):
            in_description = False
            new_lines.append(line)
            prev_was_text = False
            continue
        
        # Start of description (after links, before images at end)
        if not in_description and prev_was_text == False and stripped and not stripped.startswith('#') and not stripped.startswith('**Author') and not stripped.startswith('![') and not stripped.startswith('<div') and not stripped.startswith('</div') and not stripped.startswith('- ['):
            in_description = True
        
        # In description area - add paragraph breaks
        if in_description and stripped:
            # Check if this line starts a new logical paragraph
            # (starts with capital, previous line ended with period)
            if prev_was_text and len(stripped) > 0:
                # Check if previous non-empty line ended with sentence-ending punctuation
                if new_lines:
                    prev_content = new_lines[-1].strip() if new_lines[-1].strip() else (new_lines[-2].strip() if len(new_lines) > 1 else "")
                    if prev_content and prev_content[-1] in '.!?' and stripped[0].isupper():
                        # This looks like a new paragraph
                        if new_lines[-1].strip():  # If previous line wasn't blank
                            new_lines.append('')  # Add blank line
        
        new_lines.append(line)
        
        # Track if current line has text
        if stripped and not stripped.startswith('#') and not stripped.startswith('![') and not stripped.startswith('<') and not stripped.startswith('- ['):
            prev_was_text = True
        elif stripped.startswith('![') or stripped == '':
            prev_was_text = False
            in_description = False
    
    return '\n'.join(new_lines)

def process_file(filepath):
    """Process a single file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    new_content = fix_paragraphs(content)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    return False

def main():
    updated = 0
    for root, dirs, files in os.walk(DOCS_DIR):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            if fname == 'index.md' or fname in ['about.md', 'installation.md', 'menus.md', 'techSpecs.md']:
                continue
            
            filepath = Path(root) / fname
            if process_file(filepath):
                updated += 1
    
    print(f"Updated {updated} files with paragraph breaks")

if __name__ == "__main__":
    main()
