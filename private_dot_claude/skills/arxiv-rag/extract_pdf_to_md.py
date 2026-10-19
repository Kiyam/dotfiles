#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["pypdf", "pymupdf"]
# ///
"""Extract text from a PDF (pypdf for born-digital, tesseract OCR for scanned)
and write a Markdown file with an arxiv-rag-style header.

Usage:
    python3 extract_pdf_to_md.py <pdf> <output.md> \
        --citekey KEY --title "TITLE" [--authors "..."] [--year YYYY] \
        [--journal "..."] [--doi "..."] [--ocr]

Pass --ocr to force OCR. By default the script tries pypdf first; if it
extracts less than ~200 chars of text from the first 3 pages, it falls
back to OCR automatically.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


OCR_DPI = 300  # pretty good for 1990s journal scans; raise to 400 if needed


def text_via_pypdf(pdf_path: Path) -> str:
    import pypdf
    r = pypdf.PdfReader(str(pdf_path))
    parts = []
    for p in r.pages:
        try:
            parts.append(p.extract_text() or "")
        except Exception as e:
            parts.append(f"[extract error: {e}]")
    return "\n\n".join(parts)


def text_via_ocr(pdf_path: Path, dpi: int = OCR_DPI) -> str:
    import pymupdf  # noqa
    doc = pymupdf.open(str(pdf_path))
    print(f"  OCRing {len(doc)} pages at {dpi} dpi...", file=sys.stderr)
    parts: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        for i, page in enumerate(doc, 1):
            zoom = dpi / 72.0
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_path = td_path / f"page_{i:03d}.png"
            pix.save(str(img_path))
            res = subprocess.run(
                ["tesseract", str(img_path), "-", "-l", "eng",
                 "--psm", "1", "-c", "preserve_interword_spaces=1"],
                capture_output=True, timeout=180,
            )
            if res.returncode != 0:
                parts.append(f"[OCR error page {i}]")
            else:
                parts.append(res.stdout.decode("utf-8", errors="replace"))
            if i % 5 == 0 or i == len(doc):
                print(f"    page {i}/{len(doc)}", file=sys.stderr)
    return "\n\n".join(parts)


def clean_text(text: str) -> str:
    # Join hyphen-broken line wraps: "wave-\nform" -> "waveform"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_header(args) -> str:
    h = f"# {args.title}\n\n"
    h += f"- **citekey**: `{args.citekey}`\n"
    if args.doi:
        h += f"- **doi**: [{args.doi}](https://doi.org/{args.doi})\n"
    if args.authors:
        h += f"- **authors**: {args.authors}\n"
    if args.year:
        h += f"- **year**: {args.year}\n"
    if args.journal:
        h += f"- **journal**: {args.journal}\n"
    h += f"- **source**: extracted from local PDF ({args.method})\n\n---\n\n"
    return h


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--citekey", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--authors", default="")
    ap.add_argument("--year", default="")
    ap.add_argument("--journal", default="")
    ap.add_argument("--doi", default="")
    ap.add_argument("--ocr", action="store_true",
                    help="Force OCR even if pypdf returns text")
    ap.add_argument("--dpi", type=int, default=OCR_DPI)
    args = ap.parse_args(argv)

    method = "OCR via tesseract" if args.ocr else "pypdf"
    if not args.ocr:
        text = text_via_pypdf(args.pdf)
        # Heuristic: very little text -> almost certainly a scanned PDF
        if len(text.strip()) < 200:
            print(f"  pypdf yielded only {len(text)} chars; falling back to OCR",
                  file=sys.stderr)
            text = text_via_ocr(args.pdf, dpi=args.dpi)
            method = "OCR via tesseract (auto)"
    else:
        text = text_via_ocr(args.pdf, dpi=args.dpi)

    text = clean_text(text)
    args.method = method
    header = build_header(args)
    args.output.write_text(header + text + "\n", encoding="utf-8")
    print(f"wrote {args.output}  ({len(text):,} chars, {method})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
