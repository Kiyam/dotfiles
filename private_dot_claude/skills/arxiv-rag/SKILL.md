---
name: arxiv-rag
description: >
  Use this skill when the user wants to build a RAG-ready corpus from arXiv
  papers referenced in a BibTeX file. It parses one or more .bib files,
  identifies entries with an arXiv eprint, downloads each paper's LaTeX
  source from arxiv.org/e-print, flattens \input/\include directives,
  converts to Markdown (pandoc if installed, light cleanup otherwise),
  and writes one .md per paper plus an index. Trigger on requests like
  "fetch the papers in this bib", "download tex sources for my references",
  "build a RAG corpus from these citations", "pull arxiv sources for
  every paper I cite", or for a single paper: "turn this arXiv paper into
  markdown", "get the tex source of 2401.12345 as md" (use --arxiv). Skip when the user only wants metadata, PDF
  downloads, or abstracts — this skill is specifically for full LaTeX
  source -> Markdown.
triggers:
  - "arxiv"
  - "bib"
  - "bibliography"
  - "rag"
  - "references"
  - "fetch papers"
  - "tex source"
  - "latex source"
  - "e-print"
---

# arxiv-rag

Pulls LaTeX sources for every arXiv-eprint entry in a `.bib` file and turns
them into one Markdown file per paper, suitable as RAG context.

## Quick start

```bash
python3 ~/.claude/skills/arxiv-rag/fetch_arxiv_papers.py \
    --bib path/to/bibliography.bib \
    --out path/to/output_dir
```

The output directory will look like:

```
output_dir/
  index.md                 # citekey -> title, arxiv id, file, status
  <citekey>.md             # one file per paper
  .cache/                  # downloaded .src archives + extracted work dirs
```

Pass `--bib` multiple times to merge several bibliographies (e.g. the
outline and detailed-application bibs). The script de-duplicates by
citekey.

## Common options

| Flag | Purpose |
|---|---|
| `--bib PATH` (repeatable) | BibTeX file(s) to parse |
| `--out DIR` | Output dir for `<citekey>.md` and `index.md` |
| `--cache DIR` | Cache for downloads (default: `<out>/.cache`) |
| `--only k1,k2` | Restrict to specific citekeys |
| `--limit N` | Stop after N new downloads (useful for smoke tests) |
| `--force` | Re-process entries whose `.md` already exists |
| `--no-pandoc` | Force light LaTeX→MD cleanup even if pandoc is installed |

## How it works

1. **Parse** each `.bib` with a small built-in parser (no `bibtexparser`
   dependency). Reads `eprint`, `archivePrefix`, `title`, `author`, `year`,
   `journal`, `doi`.
2. **Identify arXiv id** from the `eprint` field, accepting modern
   (`2210.02747`, `arXiv:2210.02747`, `2210.02747v2`) and legacy
   (`astro-ph/0503479`) forms.
3. **Download** `https://arxiv.org/e-print/<id>` with a polite ~3 s
   delay between fetches. Cached on disk so re-runs are free.
4. **Extract** the source archive. Handles `.tar.gz`, bare `.gz` of a
   single tex file, and raw `.tex`. Uses tarfile's `filter="data"` for
   safe extraction.
5. **Flatten** `\input{}`, `\include{}`, and `\subfile{}` recursively
   from the file containing `\documentclass`.
6. **Convert** flat tex to Markdown. If `pandoc` is on `$PATH`, uses
   `pandoc -f latex -t gfm --wrap=none --mathjax`; otherwise falls back
   to a regex-based cleaner (strips preamble/comments, maps sections to
   `##`, keeps math as LaTeX, drops `\cite/\ref/\label`).
7. **Write** `<citekey>.md` with a frontmatter-style header (title,
   citekey, arXiv link, authors, year, journal, doi), then the body.
8. **Index** all entries in `index.md` with status flags.

## Notes

- arXiv rate-limits e-print downloads; the script sleeps ~3 s after each
  successful fetch. For ~25 entries expect ~75 s on the first run; later
  runs are instant because tarballs are cached under `--cache`.
- Non-arXiv entries (e.g. `driscoll1994convolutions`,
  `romanowicz2023global`) are listed in `index.md` under "Skipped /
  failed" with reason `no-arxiv`.
- If pandoc isn't installed, install via `brew install pandoc` (macOS)
  for substantially cleaner Markdown.

## Examples

One paper, no `.bib` needed. Accepts `2401.12345`, `arXiv:2401.12345v2` or an
`arxiv.org/abs/...` / `/pdf/...` URL; title, authors and year come from the
arXiv API and the file is named `<firstauthor><year><firstword>.md`:

```bash
python3 ~/.claude/skills/arxiv-rag/fetch_arxiv_papers.py \
    --arxiv https://arxiv.org/abs/1706.03762 --out references/papers
```

`--arxiv` is repeatable and can be combined with `--bib`/`--refs`.

Build a RAG corpus from both bib files in this repo:

```bash
python3 ~/.claude/skills/arxiv-rag/fetch_arxiv_papers.py \
    --bib "outline_application/bibliography.bib" \
    --bib "detailed_application/detailed_research_description/bibliography.bib" \
    --out references/papers
```

Re-render just two papers after editing the converter:

```bash
python3 ~/.claude/skills/arxiv-rag/fetch_arxiv_papers.py \
    --bib outline_application/bibliography.bib \
    --out references/papers \
    --only mcewen2011sampling,price2024s2fft \
    --force
```

Smoke test with three new downloads:

```bash
python3 ~/.claude/skills/arxiv-rag/fetch_arxiv_papers.py \
    --bib outline_application/bibliography.bib \
    --out /tmp/arxiv-rag-test \
    --limit 3
```

## Papers without arXiv source (PDF only)

For a PDF (journal-only or scanned papers), `extract_pdf_to_md.py` writes the
same style of `.md`. Run it with `uv`, which installs `pypdf`/`pymupdf` from
the script's inline metadata. OCR of scanned PDFs also needs the `tesseract`
binary (`brew install tesseract` / `sudo apt install tesseract-ocr`).

```bash
uv run ~/.claude/skills/arxiv-rag/extract_pdf_to_md.py paper.pdf references/papers/key.md \
    --citekey key --title "Title" [--authors "..."] [--year YYYY] [--ocr]
```
