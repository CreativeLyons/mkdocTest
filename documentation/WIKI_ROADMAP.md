# Wiki / Documentation Roadmap

Phased approach for the NST documentation wiki.

---

## Phase 1: Host images from Google Drive (first step)

- Upload `documentation/docs/img/` to Google Drive
- Make images "Anyone with the link can view"
- Update markdown to use Drive URLs: `https://drive.google.com/uc?export=view&id=FILE_ID`
- Keeps repo light; wiki works online
- **Tradeoff:** Images require internet; offline viewing breaks until Phase 2

---

## Phase 2: Compress images and add to repo

- Compress images (e.g. reduce resolution, optimize PNG/JPEG)
- Add compressed images back to repo
- Restore local paths in markdown
- Full offline support returns

---

## Phase 3: Lightweight download option in releases

- Build wiki (mkdocs build) as a zip/tarball
- Attach to GitHub Releases (not in repo)
- Users can download pre-built site for offline viewing
- Keeps main repo lean

---

## Phase 4: PDF for MAIN Tool repo

- Use `build_pdf_playwright.py` to generate PDF
- Add PDF to the main Nuke Survival Toolkit tool repo
- Link from main repo to this wiki: `https://creativelyons.github.io/mkdocTest/`

---

## Current status

- [ ] Phase 1: Google Drive images
- [ ] Phase 2: Compressed images in repo
- [ ] Phase 3: Release artifact (built wiki zip)
- [ ] Phase 4: PDF in main tool repo + link to wiki
