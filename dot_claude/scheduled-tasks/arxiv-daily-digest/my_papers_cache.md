# Kiyam's Own Papers — Context Cache

These are excerpts from Kiyam Lin's own published arXiv papers.
Use them to understand the depth, style, and methods of Kiyam's research when scoring relevance of new papers.

---

## arXiv:2404.15402 — KiDS-SBI: Simulation-based inference analysis of KiDS-1000 cosmic shear
**URL:** https://arxiv.org/abs/2404.15402

### Abstract

We present a simulation-based inference (SBI) cosmological analysis of cosmic shear two-point statistics from the fourth weak gravitational lensing data release of the ESO Kilo-Degree Survey (KiDS-1000). KiDS-SBI efficiently performs non-Limber projection of the matter power spectrum via Levin ’s method and constructs log-normal random matter fields on the curved sky for arbitrary cosmologies, including effective prescriptions for intrinsic alignments and baryonic feedback. The forward model samples realistic galaxy positions and shapes, based on the observational characteristics of KiDS-1000. It incorporates shear measurement and redshift calibration uncertainties, as well as angular anisotropies due to variable survey depth and point spread function (PSF) variations. To enable direct comparisons with standard inference, we limited our analysis to pseudo-angular power spectra as summary statistics. Here, the SBI is based on neural density estimation of the likelihood with active learning to infer the posterior distribution of spatially flat Λ Λ \Lambda roman_Λ CDM cosmological parameters from 18,000 realisations. We inferred a mean marginal for the growth of the structure parameter of S 8 ≡ σ 8 ⁢ ( Ω m / 0.3 ) 0.5 = 0.731 ± 0.033 subscript 𝑆 8 subscript 𝜎 8 superscript subscript Ω m 0.3 0.5 plus-or-minus 0.731 0.033 S_{8}\equiv\sigma_{8}(\Omega_{\mathrm{m}}/0.3)^{0.5}=0.731\pm 0.033 italic_S start_POSTSUBSCRIPT 8 end_POSTSUBSCRIPT ≡ italic_σ start_POSTSUBSCRIPT 8 end_POSTSUB

---

## arXiv:2410.11883 — SBI with scattering representations: scattering is all you need
**URL:** https://arxiv.org/abs/2410.11883

### Abstract

Abstract We demonstrate the successful use of scattering representations without further compression for simulation-based inference (SBI) with images (i.e. field-level), illustrated with a cosmological case study. Scattering representations provide a highly effective representational space for subsequent learning tasks, although the higher dimensional compressed space introduces challenges. We overcome these through spatial averaging, coupled with more expressive density estimators. Compared to alternative methods, such an approach does not require additional simulations for either training or computing derivatives, is interpretable, and resilient to covariate shift. As expected, we show that a scattering only approach extracts more information than traditional second order summary statistics.

---

## arXiv:2506.04339 — Savage-Dickey density ratio with normalizing flows for Bayesian model comparison
**URL:** https://arxiv.org/abs/2506.04339

### Abstract

Abstract A core motivation of science is to evaluate which scientific model best explains observed data. Bayesian model comparison provides a principled statistical approach to comparing scientific models and has found widespread application within cosmology and astrophysics. Calculating the Bayesian evidence is computationally challenging, especially as we continue to explore increasingly more complex models. The Savage-Dickey density ratio (SDDR) provides a method to calculate the Bayes factor (evidence ratio) between two nested models using only posterior samples from the super model. The SDDR requires the calculation of a normalised marginal distribution over the extra parameters of the super model, which has typically been performed using classical density estimators, such as histograms. Classical density estimators, however, can struggle to scale to high-dimensional settings. We introduce a neural SDDR approach using normalizing flows that can scale to settings where the super model contains a large number of extra parameters. We demonstrate the effectiveness of this neural SDDR methodology applied to both toy and realistic cosmological examples. For a field-level inference setting, we show that Bayes factors computed for a Bayesian hierarchical model (BHM) and simulation-based inference (SBI) approach are consistent, providing further validation that SBI extracts as much cosmological information from the field as the BHM approach. The SDDR estimator with normalizing fl

---

## arXiv:2212.04521 — A simulation-based inference pipeline for cosmic shear with the Kilo-Degree Survey
**URL:** https://arxiv.org/abs/2212.04521

### Abstract

The standard approach to inference from cosmic large-scale structure data employs summary statistics that are compared to analytic models in a Gaussian likelihood with pre-computed covariance. To overcome the idealising assumptions about the form of the likelihood and the complexity of the data inherent to the standard approach, we investigate simulation-based inference (SBI), which learns the likelihood as a probability density parameterised by a neural network. We construct suites of simulated, exactly Gaussian-distributed data vectors for the most recent Kilo-Degree Survey (KiDS) weak gravitational lensing analysis and demonstrate that SBI recovers the full 12-dimensional KiDS posterior distribution with just under $10^4$ simulations. We optimise the simulation strategy by initially covering the parameter space by a hypercube, followed by batches of actively learnt additional points. The data compression in our SBI implementation is robust to suboptimal choices of fiducial parameter values and of data covariance. Together with a fast simulator, SBI is therefore a competitive and more versatile alternative to standard inference.

---

## arXiv:2410.10616 — Field-level cosmological model selection: field-level SBI for Stage IV cosmic shear
**URL:** https://arxiv.org/abs/2410.10616

### Abstract

Abstract We present a framework that for the first time allows Bayesian model comparison to be performed for field-level inference of cosmological models. We achieve this by taking a simulation-based inference (SBI) approach using neural likelihood estimation, which we couple with the learned harmonic mean estimator in order to compute the Bayesian evidence for model comparison. We apply our framework to mock Stage IV cosmic shear observations to assess its effectiveness at distinguishing between various models of dark energy. If the recent DESI results that provided exciting hints of dynamical dark energy were indeed the true underlying model, our analysis shows Stage IV cosmic shear surveys could definitively detect dynamical dark energy. We also perform traditional power spectrum likelihood-based inference for comparison, which we find is not able to distinguish between dark energy models, highlighting the enhanced constraining power for model comparison of our field-level SBI approach.

---
