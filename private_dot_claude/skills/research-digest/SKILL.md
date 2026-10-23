---
name: research-digest
description: Daily arXiv digest for Kiyam — scrape new papers, score relevance, summarise, and write a tickbox digest to ~/Research/daily/. Runs from a systemd user timer on Prometheus; invoked only as /research-digest.
argument-hint: ""
disable-model-invocation: true
---

Read `~/Research/CLAUDE.md` first (the "Git sync" and "Daily digests" sections). Then build
today's arXiv digest. This often runs unattended from a systemd timer: never ask questions, never stop
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
- Sequential SBI and simulation acquisition: SNLE/SNPE, active learning, Bayesian
  optimisation, BOLFI — inference with as few simulations as possible
- Multi-fidelity SBI and transfer learning: few expensive plus many cheap simulations,
  pre-training, emulators
- Data compression for inference: score/MOPED, Fisher-informed and neural compression
- Posterior calibration and validation: TARP, SBC, coverage tests, model misspecification
  in SBI
- Field-level inference with HMC/NUTS: differentiable (spherical) forward models, Bayesian
  hierarchical models, sampler performance on GPUs
- Differentiable large-scale-structure simulators: LPT, particle-mesh codes
- KiDS-Legacy systematics modelling: variable depth, pseudo-C_ℓ and mixing matrices,
  log-normal simulations, intrinsic alignments, n(z) uncertainty
- Tools: JAX-COSMO, CAMB, harmonic, healpy, swyft, lampe, numpyro, sbi, disco-DJ, GLASS,
  heracles, s2fft, zuko, nflows, blackjax

Kiyam's own papers: arXiv:2606.23346, 2404.15402, 2410.11883, 2506.04339, 2212.04521,
2410.10616.

Kiyam's active projects (the anchors for the top scores):
- `kids_sbi` — SBI for KiDS-Legacy cosmic shear: GLASS forward sims with variable depth,
  score/MOPED compression, NLE ensemble, TARP and misspecification tests; compared against
  an explicit-likelihood analysis (cosmosis + nautilus, scaling S8 covariance) and run on
  the real KiDS-Legacy data.
- `gc_sbi` — sequential NLE of (Ωm, σ8) from P(k) with disco-DJ: simulation acquisition,
  Fisher pre-training, next multi-fidelity / transfer learning.
- `spherical_inference` — field-level NUTS over a differentiable spherical weak-lensing
  forward model (s2fft, JAX) on GPUs: a Bayesian hierarchical model sampling cosmology and
  GLASS log-normal latent fields, with an analytic field metric (mass matrix) for mixing.

Also read `~/Research/wiki/index.md` and the topic hubs in `~/Research/wiki/topics/` — they
show what Kiyam is actively working on and should nudge scores.

## Steps

0. **Sync**: pull per the "Git sync" section. Get today's date with `date +%F`. If
   `daily/digest_<today>.md` already exists, stop — today is done.
1. **Load state**: `daily/seen_papers.txt` as the seen set (empty if missing). For
   calibration:
   - `daily/my_papers_cache.md` (Kiyam's own papers);
   - the `arxiv:` field of every `wiki/sources/*.md` — papers Kiyam chose to keep (positive
     examples; also the already-ingested set);
   - the tickboxes in `daily/digest_*.md` from the last 60 days (read only titles, relevance
     lines and tickboxes): a paper with `ingest` or `to read` ticked is a positive example;
     one left unticked in a digest older than 30 days is a weak negative. Note the score each
     got, to see where past scores were off.
2. **Scrape** the "New submissions" section only (not cross-lists or replacements) of
   `https://arxiv.org/list/astro-ph.CO/new`, `.../astro-ph.IM/new`, `.../stat.ML/new` and
   `.../stat.CO/new` — the latest mailing, one per weekday run. Dedupe; up to 100 ids,
   prioritising astro-ph.CO and astro-ph.IM. Count the ids found before capping.
3. **Metadata**: `https://export.arxiv.org/api/query?id_list=<ids>&max_results=20`, in batches
   of 20 — id, title, first 4 authors, abstract, primary category, submission date.
4. **Score**: drop ids in the seen set or already in `wiki/sources/`. Score the rest 0–10
   against the interests, the projects and the step-1 examples, using these anchors:
   - **9–10**: directly usable in `kids_sbi`, `gc_sbi` or `spherical_inference`;
   - **7–8**: a method that transfers to one of them;
   - **6**: same field, worth knowing;
   - **<6**: drop.

   The one-sentence reason names the project or topic hub it serves, or says "tangential".
   Be strict: ≥6 only if the paper directly relates to SBI, weak lensing,
   normalizing flows, diffusion models, Bayesian model comparison, scattering transforms,
   wavelets, spherical CNNs, field-level inference, sequential or multi-fidelity SBI, data
   compression, posterior calibration (TARP/SBC), differentiable LSS simulators, KiDS
   systematics modelling, or ML for cosmological inference. Keep
   ≥6, at most 15, highest first.
5. **Full text**: write a BibTeX file of the selected papers (citekey from the id,
   `eprint = {<id>}`, `archivePrefix = {arXiv}`) to a temp file, then run
   `python3 ~/.claude/skills/arxiv-rag/fetch_arxiv_papers.py --bib <file> --out ~/.cache/arxiv-digest/rag_corpus`.
   Read `rag_corpus/<id>.md` for each; if its status isn't `ok`, use the abstract.
6. **Summarise** each in 3–5 sentences: the problem, the method, the key result.
7. **Write** `~/Research/daily/digest_<today>.md`:

   ```markdown
   # arXiv Digest — YYYY-MM-DD

   **Sources:** `astro-ph.CO`, `astro-ph.IM`, `stat.ML`, `stat.CO`
   **Papers scraped:** N (cap reached: F found)
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

   Keep the "(cap reached: F found)" note only when more than 100 ids were found; otherwise
   write just `N`. Every paper section ends with exactly those two tickboxes. If nothing scored ≥6, write a
   short digest saying so (no tickboxes).
8. **Seen set**: append every included id to `daily/seen_papers.txt`.
9. **Commit and push** per the "Git sync" section (`digest: YYYY-MM-DD`), including the digest
   and `seen_papers.txt`. On a push rejection, `pull --rebase` once and push again.

Never write to Zotero here — Kiyam ticks boxes in Obsidian and runs
`/research-ingest daily`. Never download PDFs. Be concise.
