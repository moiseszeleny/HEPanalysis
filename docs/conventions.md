# Conventions

**Model quantities have one source of truth:** `feynlag-models/CONVENTIONS.md`. It fixes the
metric (+,−,−,−), the potential signs, the VEV normalisation, the mixing-matrix orientation, the
Feynman-rule definition, the names and the PDG codes. Any quantity a tutorial takes from a model
keeps that convention, or the conversion is written out where it is used (`../CLAUDE.md`).

The analysis conventions below are this repository's own.

## Units

- Energies, momenta and masses in **GeV**.
- Cross sections in **pb** (MadGraph's unit) unless a label says otherwise.
- Integrated luminosity in **fb⁻¹**, so an expected yield is
  $N = \sigma\,[\text{pb}] \times 10^3 \times L\,[\text{fb}^{-1}] \times \varepsilon$.

## Event weights

A sample is normalised with the sum of its own generator weights, $\Sigma w$:

$$w_i^{\text{norm}} = w_i \, \frac{\sigma\, L}{\Sigma w}.$$

This works whatever the generator's weight convention (for example MadGraph's `event_norm`), and
it stays correct for negative weights. Each tutorial says where σ comes from: `computed` (the
generator's own value) or `cited` (a higher-order value with its source).

## Kinematics

- $p_T$; pseudorapidity $\eta = -\ln\tan(\theta/2)$; azimuth $\phi \in (-\pi, \pi]$.
- Rapidity $y$ is used only where it differs from η and is named explicitly.
- $\Delta R = \sqrt{\Delta\eta^2 + \Delta\phi^2}$, with Δφ wrapped into $(-\pi, \pi]$.
- Particle ids are the PDG Monte Carlo numbers. BSM states use the codes in
  `feynlag-models/CONVENTIONS.md`.

## Statistics

- Limits are 95% CL with CLs. Discovery uses $q_0$; upper limits use $\tilde q_\mu$.
- The asymptotic formulae follow Cowan, Cranmer, Gross, Vitells, Eur. Phys. J. C 71, 1554
  (2011), arXiv:1007.1727.
- Each tutorial states its test statistic explicitly: the library has no default.

## Numbers and claims

- Every external number is a `hepanalysis.provenance.Cited`: a value, its uncertainty, unit,
  source and the date the source was read.
- A number with no source yet is a `TodoVerify`, and it refuses arithmetic.
- In prose, a statement is tagged **computed** or **cited**.
