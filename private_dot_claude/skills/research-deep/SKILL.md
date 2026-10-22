---
name: research-deep
description: Answer a research question from Kiyam's research wiki (~/Research) with every claim backed by a verbatim quote and exact locator from the original paper. Use when Kiyam needs to verify or cite what a paper actually says, or asks for quotes/page numbers; also invoked as /research-deep. For quick wiki-only answers use /research-query.
argument-hint: <question>
---

Read `~/Research/CLAUDE.md` first. Answer, with quotes: $ARGUMENTS

1. Pull per the "Git sync" section.
2. Read `wiki/index.md`, then the relevant topic/source/concept pages. Don't go to raw
   sources for anything the wiki doesn't point you to.
3. Draft the answer with `[[page]]` citations, then back **every substantive claim** with a
   numbered marker `[n]`:
   - **Reuse first:** search `wiki/quotes/` (`grep -l <source-slug>`) for a quote from the same
     source and locator supporting the same claim. If found, cite it.
   - **Otherwise extract:** use the locator recorded on the source page (section, equation,
     page offset) to go straight to the passage — `read_topic` / `read_paper` with `sections`
     for arXiv sources, else the PDF via Zotero (`zotero_get_attachment_path`,
     `zotero_read_pdf_pages`). Extract only the sentence(s) needed. Never modify a source.
   - **Cache it:** `wiki/quotes/<source-slug>-<claim-slug>.md` with quote frontmatter per the
     "Page types and frontmatter" section; body is the verbatim text as a blockquote. The
     locator is precise: page number when available, else section + paragraph, plus equation
     number if relevant. If the source page lacks a page-offset note, add one.
   - **Link both ways** per the "Linking" section: `## Quotes` on every page in `supports:`.
4. End the answer with a **Sources** block:

   ```
   ---
   **Sources**

   [1] [[quote-page]] — Author (year), §2.3, p. 7:
   > "verbatim text"
   ```

5. If the answer is substantial, offer `/research-save`.
6. If any quote pages were created or pages changed: log a `query` entry with `quotes
   created:` per the "Log format" section, then commit and push per the "Git sync" section.
   If every quote was already cached and nothing changed, don't log or commit.
