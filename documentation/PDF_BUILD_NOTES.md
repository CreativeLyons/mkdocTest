# PDF Build Notes

## Preferred method: Playwright script

**`build_pdf_playwright.py`** is the preferred way to generate PDFs from this documentation.

- Uses the built MkDocs site (run `mkdocs build` first)
- Concatenates all pages in nav order — essentially placing all md content sequentially into PDF format
- Renders via Chromium/Playwright (full CSS support, good quality)
- Output: `NST_Documentation_Playwright.pdf`

This test confirmed that a high-quality PDF can be produced from the wiki.

---

## Future notes

*(Add notes here as needed.)*
