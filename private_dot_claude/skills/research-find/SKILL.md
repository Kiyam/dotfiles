---
name: research-find
description: Find papers on NASA ADS / arXiv and add them to Kiyam's Zotero Ingest inbox — a specific paper by id/DOI/title, or discovery by topic or citation graph. Invoked only as /research-find.
argument-hint: "<arxiv-id | bibcode | DOI | title> | <free-text query> | <refs|cites|similar> <paper>"
disable-model-invocation: true
---

Read `~/Research/CLAUDE.md` first. Find: $ARGUMENTS

Check Zotero is writable per the "Zotero conventions" section before anything else.

## Specific paper

When the argument is an arXiv id, bibcode, DOI, or something that reads as one paper's title:

1. Identify it per the "Identifying a paper" section.
2. Dedupe per the "Zotero conventions" section. If it's already in Zotero, say so (with its
   collections and whether it has a `wiki/sources/` page) and stop.
3. Otherwise create the item with full metadata and identifiers per the "Zotero conventions"
   section, add it to `Ingest`, and attach the arXiv PDF if one exists (`fetch_pdf`).
4. Offer to ingest it now (`/research-ingest <key>`).

## Discovery

When the argument is a free-text query, or `refs` / `cites` / `similar` followed by a paper
(Zotero key, arXiv id, bibcode or DOI):

1. Search: `flexible_paper_search` for a query; `related_papers` with `mode` =
   `references` / `citations` / `similar` for the graph. ADS first; arXiv fallback happens
   automatically.
2. Read `wiki/index.md` and the topic hubs to know what Kiyam works on and already has.
3. Mark each candidate already in Zotero (dedupe rules) as **in library**.
4. Rank the rest by relevance to Kiyam's topics and show a numbered list: title, first author
   + year, venue/arXiv id, one line on why it matters *to these topics* (or "tangential").
   About 10 by default.
5. Wait for Kiyam to pick numbers. Add each pick as in "Specific paper" step 3.

No wiki pages are written here, and nothing is committed.
