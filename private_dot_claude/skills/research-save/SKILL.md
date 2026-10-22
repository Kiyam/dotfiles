---
name: research-save
description: File the previous answer as a synthesis page in Kiyam's research wiki (~/Research/wiki/syntheses/). Invoked only as /research-save.
argument-hint: "[slug]"
disable-model-invocation: true
model: haiku
---

Read `~/Research/CLAUDE.md` first. File the previous assistant answer as a synthesis page.

1. Pull per the "Git sync" section.
2. Slug: `$ARGUMENTS`, or a short kebab-case slug derived from the answer.
3. Write `~/Research/wiki/syntheses/<slug>.md` with synthesis frontmatter per the "Page types and frontmatter" section (`question:` = the question that prompted the answer; quote wikilinks in YAML lists; parse the frontmatter to check it). Keep the answer's `[[wikilinks]]` and any Sources block.
4. Link it from each relevant topic hub (`## Syntheses`) and from `wiki/index.md` per the "Index format" section.
5. Append a `query` entry with a `filed as:` line per the "Log format" section.
6. Commit and push per the "Git sync" section; report the page path and whether the push succeeded.
