---
name: research-ingest
description: Ingest papers into Kiyam's research wiki (~/Research) and file them in Zotero. Invoked only as /research-ingest.
argument-hint: "<zotero-key | arxiv-id | DOI | pdf-path | inbox | backlog | daily> [--batch]"
disable-model-invocation: true
model: sonnet
---

Read `~/Research/CLAUDE.md` first. Ingest: $ARGUMENTS

## Arguments

- **Zotero item key** (8 chars), **arXiv id**, **DOI**, or **path to a PDF**: one paper.
- **`inbox`**: every item in the Zotero `Ingest` collection.
- **`backlog`**: every PDF under `~/Documents/Papers/` (recursive), plus every regular item in
  Zotero that has no `wiki/sources/` page yet (match on `zotero_key` in source frontmatter).
- **`daily`**: pending ticks in `~/Research/daily/*.md` (see below).
- **`--batch`**: don't stop to discuss takeaways. `inbox`, `backlog` and `daily` are always
  batch. In batch mode, process papers one at a time to completion and report at the end.

## Before anything

1. Check Zotero is writable per the "Zotero conventions" section. If not, stop now —
   nothing may be written.
2. Pull per the "Git sync" section.

## For each paper

1. **Resolve the Zotero item.**
   - Zotero key → fetch it.
   - arXiv id / DOI / PDF → identify per the "Identifying a paper" section, then dedupe per
     the "Zotero conventions" section. Existing item → use it. None → create it with
     `zotero_add_item` (correct type, authors, title, date, abstract, URL, DOI,
     journal, `Extra`). For a PDF, attach the original as a linked or imported file without
     moving or modifying it. For a PDF from a folder whose name contains `(unread)`, also add
     the item to `To Read`.
   - Enrich: make sure the item carries the arXiv URL, DOI/journal and the `Extra` lines
     `arXiv: <id>` / `ADS Bibcode: <bibcode>` — whichever exist. Use ADS to check whether an
     arXiv preprint has since been published; if so set the DOI, journal and type
     `journalArticle`.
2. **Read it** per the "Identifying a paper" section's full-text order: `.tex` first, then PDF,
   then OCR. Read section by section and look only at the key data figures (at most 4), as
   that section says. Also read the item's Zotero notes and PDF annotations
   (`zotero_get_notes`, `zotero_get_annotations`) — they are Kiyam's own reading notes and
   matter more than anything else on the page.
3. **Discuss** (unless batch): give Kiyam 3–5 key takeaways, the topic(s) you'd file it
   under, and any tension with existing wiki pages; wait for a reply before writing.
4. **Write pages.** Check `wiki/index.md` first.
   - **Topic(s)**: reuse an existing hub when it fits. A new topic means a new hub page *and*
     a new top-level Zotero collection with the same name; record its key in
     `zotero_collection`. In batch mode, prefer existing topics; propose new ones in the final
     report rather than creating them, unless nothing fits at all.
   - **Source page** `wiki/sources/<slug>.md` per the "Source page template" section. If a
     page with this `zotero_key` (or arXiv id / DOI) exists, update it — never create a second.
   - **Concept pages** for the methods, models and quantities it uses or introduces, with
     equation blocks per the "Equation blocks" section for the equations someone would need
     to implement. Update existing concept pages rather than duplicating; reconcile notation.
   - **Entity pages** for surveys/instruments and software/codes; for people, follow the
     second-paper rule in the "Page types and frontmatter" section (search existing
     sources' `authors:` for a match).
   - **Related papers**: typed links to sources already in the wiki, both ways.
   - **Topic hub(s)**: link every new/updated page; revise "Current picture" if this paper
     changes it.
   - `wiki/index.md` per the "Index format" section; a log entry per the "Log format"
     section.
   - Parse every touched page's frontmatter as YAML.
5. **Commit and push** per the "Git sync" section (one commit per paper:
   `ingest: <source slug>`). A failed push is reported but does not stop the next step — the
   commit exists locally.
6. **File in Zotero** — only after the commit exists: add the item to its topic
   collection(s), then remove it from `Ingest` if it was there.

A single paper typically touches 5–15 pages. That's expected.

## daily

Scan `~/Research/daily/*.md` for pending ticks per the "Daily digests" section. For each
paper section with a pending tick:

- **`ingest`** → run the per-paper steps above (batch) on the paper's arXiv id.
- **`to read`** → resolve and dedupe the Zotero item (step 1 only), add it to `To Read` and to
  the best-fitting topic collection; no wiki pages.
- Then rewrite that line as `- [x] ingest — done YYYY-MM-DD` / `- [x] to read — done
  YYYY-MM-DD` and include the digest file in that paper's commit.

## Resuming

Because items leave `Ingest` (and ticks get `— done`) only after their commit, re-running the
same command after an interruption picks up exactly what's left. A paper whose source page
already exists is updated, not duplicated.

## Report

List per paper: source page, pages created/updated, Zotero collections, whether it was pushed,
and any open questions, contradictions or proposed new topics.
