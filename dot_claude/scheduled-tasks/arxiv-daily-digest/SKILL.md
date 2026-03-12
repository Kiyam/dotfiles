---
name: arxiv-daily-digest
description: Daily arXiv digest: scrape new papers, rank relevance, summarise, write to Obsidian
---

You are running the daily arXiv digest for Kiyam Lin (cosmologist, UCL). Your job is to scrape today's new papers from several arXiv listing pages, filter them by relevance to Kiyam's research interests, fetch the full text of relevant papers, write short summaries, and save a markdown digest to the Obsidian vault.

## Kiyam's research interests
Kiyam works on:
- Simulation-based inference (SBI) for weak gravitational lensing and cosmic shear
- Bayesian model comparison (e.g. Savage-Dickey density ratio with normalizing flows)
- Neural density estimators (normalizing flows, diffusion models, flow matching)
- Scattering transforms and wavelet-based summary statistics for cosmological fields
- Spherical convolutional network methods to summarise spherical fields as a summary statistics
- Machine learning methods for high-dimensional Bayesian inference in cosmology
- KiDS, Euclid, and LSST cosmic shear data analysis
- Euclid galaxy clustering analysis
- Large-scale structure statistics: power spectra, higher-order statistics
- Neural posterior/likelihood/ratio estimation for cosmological parameter inference
- Continuous normalising flows, diffusion-based generative models for inference
- Python cosmology tools: JAX-COSMO, CAMB, healpy, swyft, lampe, numpyro

Kiyam's own papers (for context on depth/style of research):
- arXiv:2404.15402 — KiDS-SBI: Simulation-based inference analysis of KiDS-1000 cosmic shear
- arXiv:2410.11883 — SBI with scattering representations: scattering is all you need
- arXiv:2506.04339 — Savage-Dickey density ratio with normalizing flows for Bayesian model comparison
- arXiv:2212.04521 — A simulation-based inference pipeline for cosmic shear with the Kilo-Degree Survey
- arXiv:2410.10616 — Field-level cosmological model selection: field-level simulation-based inference for Stage IV cosmic shear can distinguish dynamical dark energy


## Step-by-step instructions

### Step 0 — Load Kiyam's paper cache
Read the file at `~/.claude/scheduled-tasks/arxiv-daily-digest/my_papers_cache.md` (expand `~` to the actual home directory, e.g. `/Users/kiyam/.claude/scheduled-tasks/arxiv-daily-digest/my_papers_cache.md`).

This file contains abstracts and key sections from Kiyam's own published papers. Use the content to calibrate your relevance scoring in Step 3: understand the specific methods, datasets, and problem framings Kiyam works with, and score new papers higher when they closely relate to those specific approaches (not just the broad topic area).

If the file does not exist, skip this step and proceed with the topic list above as the sole reference.

### Step 1 — Scrape arXiv listing pages
Use WebFetch to fetch each of these four listing pages. For each page, extract the arXiv IDs of **new submissions only** (not cross-lists or replacements):
- https://arxiv.org/list/astro-ph.CO/recent
- https://arxiv.org/list/astro-ph.GA/recent
- https://arxiv.org/list/cs.LG/recent
- https://arxiv.org/list/stat.ML/recent

From each page, collect the paper IDs (format like `2501.12345`). Deduplicate across all four lists. Aim for up to 100 unique IDs total, prioritising astro-ph.CO and astro-ph.GA.

### Step 2 — Fetch paper metadata
Use WebFetch to call the arXiv Atom API in batches of up to 20 IDs at a time:
`https://export.arxiv.org/api/query?id_list=ID1,ID2,...&max_results=20`

From each response, extract for each paper:
- arXiv ID
- Title
- Authors (first 4)
- Abstract
- Primary category
- Submission date

### Step 3 — Score relevance
Read each paper's title and abstract. Assign a relevance score from 0–10 based on how closely it matches Kiyam's interests above. Use the paper cache loaded in Step 0 for finer calibration: papers that use similar methods, datasets (KiDS, Euclid, LSST), or problem framings to Kiyam's own work should score higher. Be strict: only score ≥6 if the paper directly relates to SBI, weak lensing, normalizing flows, diffusion models, Bayesian model comparison, scattering transforms, wavelet methods, spherical CNNs, field level inference or ML methods for cosmological inference.

Keep only papers with score ≥ 6. Aim for at most 15 papers — if more score ≥6 pick the top 15 by score.

### Step 4 — Fetch full text and summarise
For each relevant paper, fetch the arXiv HTML endpoint:
`https://arxiv.org/html/ARXIV_ID`

From the HTML, extract the main body text (focus on abstract, introduction, and conclusion sections). If the HTML version is unavailable (404), fall back to the abstract.

Write a 3–5 sentence summary that covers:
1. What problem the paper addresses
2. What method or approach they use
3. Key result or finding

### Step 5 — Write markdown digest to Obsidian
Write the final digest as a markdown file to:
`/Users/kiyam/Library/Mobile Documents/iCloud~md~obsidian/Documents/Kiyam's Notes/ArXiv/digest_YYYY-MM-DD.md`

where `YYYY-MM-DD` is today's date.

The file should have this structure:

```markdown
# arXiv Digest — YYYY-MM-DD

**Sources:** `astro-ph.CO`, `astro-ph.GA`, `cs.LG`, `stat.ML`
**Papers scraped:** N  
**Papers selected:** M (relevance ≥ 6/10)

---

## Contents

1. [Paper Title](#anchor) — score **X.X**
2. ...

---

## 1. Paper Title

**arXiv:** [XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · [HTML](https://arxiv.org/html/XXXX.XXXXX)  
**Authors:** Author 1, Author 2, Author 3 +N more  
**Submitted:** YYYY-MM-DD  
**Categories:** category1, category2  
**Relevance:** X.X/10 — _one-sentence reason_

### Abstract

> First 600 characters of abstract…

### Summary

3–5 sentence summary written above.

---
```

Repeat the paper section for each relevant paper, ordered by relevance score (highest first).

If no papers score ≥6, write a short digest noting that no highly relevant papers were found today.

## Important notes
- Today's date can be obtained by running: `date +%Y-%m-%d` via Bash
- The Obsidian vault folder already exists; just write the file directly
- Do not download any PDFs
- Be concise in summaries — quality over quantity
- If fetching a page fails, skip it and continue with the rest