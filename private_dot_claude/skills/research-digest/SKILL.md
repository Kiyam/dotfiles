---
name: research-digest
description: Daily arXiv digest for Kiyam — scrape new papers, score relevance, summarise, and write a tickbox digest to ~/Research/daily/. Runs from cron on Prometheus; invoked only as /research-digest.
argument-hint: ""
disable-model-invocation: true
---

Read `~/Research/CLAUDE.md` first (the "Git sync" and "Daily digests" sections). Then build
today's arXiv digest. This often runs unattended from cron: never ask questions, never stop
for confirmation; if a step fails, skip it, note it in the digest, and carry on.

State lives in the vault: `~/Research/daily/seen_papers.txt` (one arXiv id per line, every
paper ever included) and `~/Research/daily/my_papers_cache.md` (excerpts of Kiyam's own
papers). The full-text cache is machine-local: `~/.cache/arxiv-digest/rag_corpus/`.

## Kiyam's research interests

- Simulation-based inference (SBI) for weak gravitational lensing, cosmic shear and galaxy
  clustering
- Bayesian model comparison (e.g. Savage–Dickey density ratio with normalizing flows)
- Neural density estimators (normalizing flows, diffusion models, flow matching)
- Scattering transforms and wavelet-based summary statistics for cosmological fields
- Spherical convolutional networks as summary statistics of spherical fields
- Machine learning for high-dimensional Bayesian inference in cosmology
- KiDS, DES, Euclid and LSST cosmic shear and galaxy clustering analyses
- Large-scale structure statistics: power spectra, higher-order statistics
- Neural posterior/likelihood/ratio estimation for cosmological parameters
- Continuous normalising flows, diffusion-based generative models for inference
- Tools: JAX-COSMO, CAMB, harmonic, healpy, swyft, lampe, numpyro, sbi

Kiyam's own papers: arXiv:2606.23346, 2404.15402, 2410.11883, 2506.04339, 2212.04521,
2410.10616.

Also read the topic hubs in `~/Research/wiki/topics/` — they show what Kiyam is actively
working on and should nudge scores.

## Steps

0. **Sync**: pull per the "Git sync" section. Get today's date with `date +%F`. If
   `daily/digest_<today>.md` already exists, stop — today is done.
1. **Load state**: `daily/my_papers_cache.md` for calibration; `daily/seen_papers.txt` as the
   seen set (empty if missing).
2. **Scrape** new submissions only (not cross-lists or replacements) from
   `https://arxiv.org/list/astro-ph.CO/recent`, `.../astro-ph.IM/recent` and
   `.../stat.ML/recent`. Dedupe; up to 100 ids, prioritising astro-ph.CO and astro-ph.IM.
3. **Metadata**: `https://export.arxiv.org/api/query?id_list=<ids>&max_results=20`, in batches
   of 20 — id, title, first 4 authors, abstract, primary category, submission date.
4. **Score**: drop ids in the seen set. Score the rest 0–10 against the interests, calibrated
   by the papers cache. Be strict: ≥6 only if the paper directly relates to SBI, weak lensing,
   normalizing flows, diffusion models, Bayesian model comparison, scattering transforms,
   wavelets, spherical CNNs, field-level inference, or ML for cosmological inference. Keep
   ≥6, at most 15, highest first.
5. **Full text**: write a BibTeX file of the selected papers (citekey from the id,
   `eprint = {<id>}`, `archivePrefix = {arXiv}`) to a temp file, then run
   `python3 ~/.claude/skills/arxiv-rag/fetch_arxiv_papers.py --bib <file> --out ~/.cache/arxiv-digest/rag_corpus`.
   Read `rag_corpus/<id>.md` for each; if its status isn't `ok`, use the abstract.
6. **Summarise** each in 3–5 sentences: the problem, the method, the key result.
7. **Write** `~/Research/daily/digest_<today>.md`:

   ```markdown
   # arXiv Digest — YYYY-MM-DD

   **Sources:** `astro-ph.CO`, `astro-ph.IM`, `stat.ML`
   **Papers scraped:** N
   **Papers selected:** M (relevance ≥ 6/10)

   ---

   ## Contents

   1. [Title](#anchor) — score **X.X**

   ---

   ## 1. Title

   **arXiv:** [ID](https://arxiv.org/abs/ID) · [HTML](https://arxiv.org/html/ID)
   **Authors:** A, B, C +N more
   **Submitted:** YYYY-MM-DD
   **Categories:** …
   **Relevance:** X.X/10 — _one-sentence reason_

   ### Abstract

   > first 600 characters…

   ### Summary

   …

   - [ ] ingest
   - [ ] to read

   ---
   ```

   Every paper section ends with exactly those two tickboxes. If nothing scored ≥6, write a
   short digest saying so (no tickboxes).
8. **Seen set**: append every included id to `daily/seen_papers.txt`.
9. **Commit and push** per the "Git sync" section (`digest: YYYY-MM-DD`), including the digest
   and `seen_papers.txt`. On a push rejection, `pull --rebase` once and push again.

Never write to Zotero here — Kiyam ticks boxes in Obsidian and runs
`/research-ingest daily`. Never download PDFs. Be concise.
