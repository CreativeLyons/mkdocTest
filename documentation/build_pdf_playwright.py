#!/usr/bin/env python3
"""
Build a PDF from MkDocs site by concatenating all pages in nav order.
Uses the built HTML (mkdocs build) and Playwright/Chromium for PDF rendering.
This produces a simple sequential PDF: all content, one page after another.

Prerequisites:
  - mkdocs build (run first to generate documentation/site/)
  - playwright install chromium (if not already installed)

Usage:
  cd documentation && python build_pdf_playwright.py
"""

import os
import re
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

# Optional: playwright for PDF
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


def get_nav_md_paths(nav):
    """Recursively extract .md paths from mkdocs nav in order."""
    paths = []

    def walk(obj):
        if isinstance(obj, list):
            for item in obj:
                walk(item)
        elif isinstance(obj, dict):
            for key, val in obj.items():
                if isinstance(val, str) and val.endswith(".md"):
                    paths.append(val)
                else:
                    walk(val)

    walk(nav)
    return paths


def md_to_html_path(md_path):
    """Convert docs-relative .md path to site-relative .html path."""
    base, _ = os.path.splitext(md_path)
    return base + ".html"


def extract_article(html_path, site_dir):
    """Extract article content from a built MkDocs HTML page."""
    full_path = site_dir / html_path
    if not full_path.exists():
        return None, None

    html = full_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one("article.md-content__inner")
    if not article:
        return None, None

    # Depth of page (for fixing relative paths): draw/grad-magic.html -> 1
    dir_part = os.path.dirname(html_path)
    depth = len([p for p in dir_part.split(os.sep) if p]) if dir_part else 0

    # Rewrite relative URLs to be site-root-relative
    for tag in article.find_all(["img", "a"]):
        attr = "src" if tag.name == "img" else "href"
        if not tag.has_attr(attr):
            continue
        url = tag[attr]
        if not url or url.startswith(("#", "mailto:", "http://", "https://")):
            continue
        # Remove leading ../ to make path relative to site root
        parts = url.replace("\\", "/").split("/")
        up = 0
        for p in parts:
            if p == "..":
                up += 1
            else:
                break
        if up > 0:
            remaining = "/".join(parts[up:])
            tag[attr] = remaining

    return str(article), depth


def build_combined_html(site_dir, nav_paths, output_html):
    """Build a single HTML file with all content in nav order."""
    html_paths = [md_to_html_path(p) for p in nav_paths]

    parts = []
    for html_path in html_paths:
        content, _ = extract_article(html_path, site_dir)
        if content:
            parts.append(f'<div class="pdf-page">{content}</div>')

    combined = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Nuke Survival Toolkit Documentation</title>
  <link rel="stylesheet" href="assets/stylesheets/main.120efc48.min.css">
  <link rel="stylesheet" href="assets/stylesheets/palette.9647289d.min.css">
  <link rel="stylesheet" href="css/material-custom.css">
  <style>
    body {{ max-width: 800px; margin: 0 auto; padding: 2em; font-size: 11pt; }}
    .pdf-page {{ page-break-after: always; }}
    .pdf-page:last-child {{ page-break-after: auto; }}
    @media print {{ .pdf-page {{ page-break-after: always; }} }}
  </style>
</head>
<body class="md-typeset">
  <h1>Nuke Survival Toolkit Documentation</h1>
  <p><em>Release v2.1.0</em> — PDF export</p>
  <hr>
  {"".join(parts)}
</body>
</html>"""

    output_html.write_text(combined, encoding="utf-8")
    return output_html


def main():
    script_dir = Path(__file__).resolve().parent
    site_dir = script_dir / "site"
    mkdocs_yml = script_dir / "mkdocs.yml"

    if not site_dir.exists():
        print("Run 'mkdocs build' first to generate documentation/site/")
        sys.exit(1)

    with open(mkdocs_yml, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    nav = config.get("nav", [])
    md_paths = get_nav_md_paths(nav)
    print(f"Found {len(md_paths)} pages in nav")

    output_html = site_dir / "_pdf_combined.html"
    build_combined_html(site_dir, md_paths, output_html)
    print(f"Wrote combined HTML: {output_html}")

    if not sync_playwright:
        print("Install playwright: pip install playwright && playwright install chromium")
        print("Then run this script again to generate the PDF.")
        sys.exit(0)

    output_pdf = script_dir / "NST_Documentation_Playwright.pdf"
    html_url = output_html.as_uri()

    with sync_playwright() as p:
        # Prefer system Chrome if available (avoids playwright install)
        try:
            browser = p.chromium.launch(channel="chrome")
        except Exception:
            browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_url, wait_until="networkidle", timeout=60000)
        page.pdf(
            path=str(output_pdf),
            format="A4",
            margin={"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"},
            print_background=True,
        )
        browser.close()

    print(f"Wrote PDF: {output_pdf}")


if __name__ == "__main__":
    main()
