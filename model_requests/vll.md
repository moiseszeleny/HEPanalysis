# Model request: `vll` (a vector-like lepton mixing with τ)

**Requested by**: HEPanalysis T12, a multilepton counting search with control regions
(simulation only). It teaches background estimation when there is no resonance peak to fit.

**Status**: open. Filed on 2026-10-22 at the user's request. Its base for LHC production is
`model_requests/sm_qcd.md`. Nothing is built from here.

**Minimum level requested**: **L4**.

## Motivation

feynlag-models has no vector-like fermion. feynlag already has one:
`docs/tutorials/SM_VLL_Tutorial.ipynb` and `examples/sm_vll.py` build an SM + vector-like lepton
doublet. That example covers:
- a bare mass M_Ψ;
- the Higgs-induced mixing with a right-handed SM lepton;
- the 2 × 2 mass matrix with two mixing angles (θ_L, θ_R);
- the induced flavour-changing Z, W and h couplings.

The example mixes with the electron. For the LHC the τ is the better-motivated case, and the
`sm` generation feynlag-models already has is the τ generation.

## Requested content

- A vector-like lepton doublet (or singlet; the implementer chooses and records it) mixing with
  the τ.
- Its mass eigenstates, the mixing angles as exported internal parameters, and the induced Z, W±
  and h couplings among τ, ν_τ and the heavy states.
- Benchmark inputs in the physical basis (heavy mass, mixing). The widths of the heavy states are
  computed, not placeholders.
- A UFO on the hadron-ready base, so that Drell–Yan pair production pp → Z\*/γ\*/W\* → L L̄ is
  available.

## What calculation requires it

T12: pair production, decays to Zτ, Wν and hτ, a multilepton selection, control regions for the
irreducible backgrounds, and an expected-limit estimate.

## Checks requested

- **L2:** the mass matrix, the mixing and the induced couplings, against Kumar & Martin,
  "Vectorlike leptons at the Large Hadron Collider", Phys. Rev. D 92, 115018 (2015),
  arXiv:1510.03456. The implementer verifies the equations and records the conventions.
- **L4:** σ(pp → L L̄) at 13 TeV against an independent route. For a pure gauge production
  process, the Drell–Yan cross section with the doublet's gauge couplings is a natural check.
