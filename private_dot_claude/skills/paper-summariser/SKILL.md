---
name: paper-summariser
description: Summarise a research paper (arXiv preprint, journal article, PDF, or abstract) into a structured, skimmable note that appraises it rather than just paraphrasing. Use this whenever the task is "read this paper and summarize it", "make notes on this arXiv paper", "what's the gist of this", "is this worth reading", "TL;DR of this PDF", or distilling a paper into method + assumptions + contribution + relevance. Trigger it for any request to digest a technical paper, across any field, even when no output format is specified.
---

# Paper Summariser

Turn a paper into a note that captures what it *does*, what it *assumes*, and whether it's worth a deeper read — the things worth knowing six months later when you've forgotten why you saved it. Optimize for honest signal and skimmability, not faithful reproduction of the abstract. Works for any technical field; the abstract sells, the note appraises.

## Output template

Default to this markdown structure (it suits a personal knowledge base like Obsidian, but reads fine anywhere). Drop a section entirely if the paper has nothing for it — an empty "Code/data: none" is fine; padded filler is not.

```markdown
# [Short title] — [first author] et al. ([year])
**Source:** [arXiv id / DOI / venue]  ·  **Read:** [date]  ·  **Tags:** #[topic] #[method]

## TL;DR
One or two sentences: what they did and the single most important result. No fluff.

## Problem
The gap or question, and why it matters to the field — not the abstract's words.

## Method
The actual approach in plain terms: technique, model, data. If one key idea makes it work, isolate it.

## Key assumptions / limitations
The load-bearing assumptions — the ones that, if wrong, break the result. What regime it's valid in; what got swept under the rug. Be skeptical here; this is where the note earns its keep.

## What's genuinely new
Separate the real contribution from incremental repackaging. If it's a known idea on a new dataset, say so plainly.

## Relevance / why I'd cite it
Concrete: a method to borrow, a baseline to beat, a result to cite, or just context. Most papers are tangential — saying so is more useful than manufacturing a link.

## Numbers / results worth remembering
The headline quantitative results with their uncertainties. Only what you'd actually reuse.

## Code / data
Repo, dataset, reproducibility — link plus a one-line take on whether it's actually runnable.

## Follow-ups
Threads to pull: references to chase, an experiment it suggests, a weakness worth probing.
```

If the user asks for something lighter (just a TL;DR, or a paragraph), give that instead — don't force the full template when they want three sentences.

## How to read for the summary

- **Lead with limitations, not claims.** Find the assumption the result rests on and state it, especially where the authors didn't.
- **Separate contribution from context.** Papers wrap a small new idea in a lot of background — name the small idea.
- **Quantify.** Replace "improves performance" with the actual number and the baseline it beats. If the paper is vague about this, note that as a weakness.
- **Be honest about strength.** Flag overclaiming, cherry-picked baselines, missing ablations, or results that don't support the headline. A summary that surfaces these is worth far more than one that launders the abstract.
- **Method papers:** record what was assumed, how the central claim was validated, and whether the method is reproducible/reusable in practice (code quality, compute needs, dependencies).
- **Empirical/results papers:** record the dataset, the comparison set, the effect size with uncertainty, and the main confound.

## Length

A summary is not a review. Aim for something readable in under a minute — dense, not long. If a section runs past a few lines, you're transcribing, not distilling.

## Copyright

Paraphrase throughout; do not reproduce paragraphs from the paper. Short quoted phrases only where exact wording matters (a defined term, a precise claim), kept minimal and attributed.
