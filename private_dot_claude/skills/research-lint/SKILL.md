---
name: research-lint
description: Health check of Kiyam's research wiki (~/Research) and its Zotero library — contradictions, stale claims, gaps, and Zotero organisation. Invoked only as /research-lint.
argument-hint: "[focus]"
disable-model-invocation: true
---

Read `~/Research/CLAUDE.md` first. Optional focus: $ARGUMENTS

1. Check Zotero is writable and pull, per the "Zotero conventions" and "Git sync" sections.
2. Run the `/research-lint-links` checks (same rules) and fold in the results.
3. **Wiki checks** (needs judgement):
   - Contradictions between pages not acknowledged anywhere.
   - Claims superseded by newer sources but not updated.
   - Methods/quantities mentioned on several pages without their own concept page.
   - Equation blocks missing a symbol in their table, provenance, or validity line.
   - Person pages linked from fewer than two sources (second-paper rule), and authors who
     now appear in two sources without a person page.
   - Pages filed under the wrong type: a dataset, simulation suite or index (e.g. a stock index)
     written as an entity belongs in `concepts/`; an `entity_type` that doesn't fit (a market
     index is not an `instrument`).
   - Gaps a search could fill (a later published version, an obvious follow-up paper).
4. **Zotero checks** (rules in the "Zotero conventions" section):
   - Regular items in no top-level topic collection.
   - `To Read` items (including subcollections) with no topic collection.
   - Items still in `Ingest`, and items with no `wiki/sources/` page.
   - Blocked work waiting for Kiyam: items tagged `needs-kiyam` (with their note) and digest
     lines marked `— blocked:`. List each with its reason and a suggested resolution.
   - Items missing the arXiv URL / DOI / bibcode **only when the paper has one**: check ADS or
     Crossref; a paper genuinely without an arXiv id or bibcode (e.g. outside ADS) is fine.
   - Preprints that ADS now shows as published (DOI/journal missing on the item).
   - Topic drift both ways: a top-level collection with no hub (`zotero_collection`), or a hub
     whose key doesn't exist or whose name differs from the collection's.
   - Possible duplicates (same arXiv id ignoring version, same DOI ignoring case, same bibcode).
5. Report everything grouped (structural, wiki, Zotero), each with a proposed fix, and suggest
   papers worth finding next. **Apply nothing until Kiyam confirms**; then apply the confirmed
   fixes, log a `lint` entry per the "Log format" section, and commit and push per the
   "Git sync" section.
