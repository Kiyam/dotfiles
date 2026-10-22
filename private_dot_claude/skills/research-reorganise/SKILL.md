---
name: research-reorganise
description: Propose and apply topic merges, splits and renames across Kiyam's research wiki (~/Research) and Zotero collections together. Invoked only as /research-reorganise.
argument-hint: "[what to reconsider]"
disable-model-invocation: true
---

Read `~/Research/CLAUDE.md` first. Reconsider: $ARGUMENTS (or the whole topic structure).

1. Check Zotero is writable and pull, per the "Zotero conventions" and "Git sync" sections.
2. Read every hub in `wiki/topics/`, the source pages' `topics:`, and each topic collection's
   item count. Read tags too.
3. Propose changes, each with a reason and the pages/items it moves: **merge** (A + B → C),
   **split** (A → A1 + A2, with which sources go where), **rename**, **new** topic, **retire**
   a topic, or tag clean-ups. Stop and wait for Kiyam to accept, edit or drop each one.
   Exception: if the arguments name one exact change (e.g. "rename X to Y"), that request is
   the approval — apply it directly. Anything you propose yourself always waits.
4. For each accepted change, apply both sides:
   - **Zotero**: rename with `zotero_update_collection` (keeps the key); create new
     collections; move items with `zotero_set_item_collections`. Delete a collection only when
     it is empty and Kiyam confirmed that deletion specifically — deletion can't be undone.
   - **Vault**: rename/create/merge hub files; update `zotero_collection`, `title`, and every
     page's `topics:`; rewrite every `[[old-slug]]` / `[[old-slug|…]]` link; update
     `wiki/index.md`.
5. Run the `/research-lint-links` checks; fix anything this change broke.
6. Log a `reorganise` entry per the "Log format" section; commit and push per the "Git sync"
   section. Report what changed on each side.
