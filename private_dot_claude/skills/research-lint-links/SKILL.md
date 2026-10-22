---
name: research-lint-links
description: Structural link check of Kiyam's research wiki (~/Research) — orphan pages and missing cross-references. Invoked only as /research-lint-links (also called by /research-lint).
argument-hint: ""
disable-model-invocation: true
model: haiku
---

Read `~/Research/CLAUDE.md` first (the "Linking" section). Pull per the "Git sync" section,
then report — don't fix:

- **Orphans**: pages under `wiki/sources|concepts|entities|syntheses/` with no inbound
  `[[link]]` from `wiki/index.md` or any `wiki/topics/*.md`. Quote pages count as linked when
  a page in their `supports:` lists them under `## Quotes`.
- **Broken links**: `[[target]]` (ignore any `|alias` or `#heading`) with no
  `wiki/**/target.md`.
- **Missing cross-references**: a page's prose names something that has its own page (match
  page titles and slugs, case-insensitive, whole words) without linking it. Skip a page's own
  name and text inside code/math blocks.
- **Invalid frontmatter**: any page whose frontmatter doesn't parse as YAML.

Use `grep`/scripts for this, not reading every page. Output a flat list grouped by category,
each line `path — problem — suggested fix`. No claim-level judgement; that's `/research-lint`.
