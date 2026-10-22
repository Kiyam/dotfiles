---
name: research-query
description: Answer a research question from Kiyam's research wiki (~/Research) — papers Kiyam has read, methods, results, equations, how papers relate. Use when Kiyam asks about a paper, method, result or equation that may be in the literature notes, from any project or machine; also invoked as /research-query. Wiki only, no raw sources — for quote-backed answers use /research-deep.
argument-hint: <question>
---

Read `~/Research/CLAUDE.md` first. Then answer: $ARGUMENTS

1. `git -C ~/Research pull --rebase --autostash` per the "Git sync" section (if it fails, carry on with the local copy and mention it).
2. Read `~/Research/wiki/index.md`, then the topic, source, concept and entity pages it points to, following `[[wikilinks]]` as needed.
3. Answer with `[[page]]` citations. When the question is about implementing something, give the relevant equation block(s) from the concept pages in full, symbol table included. No verbatim quotes, locators or quote pages — that's `/research-deep`.
4. If the wiki doesn't cover the question, say so plainly and suggest `/research-deep <question>` (which may open raw sources) or `/research-find` (to look for papers). Do not open PDFs or `.tex` here.
5. If the answer is substantial (a comparison across papers, a literature-review answer, a non-trivial connection), offer `/research-save` to file it. Don't offer for quick lookups.
