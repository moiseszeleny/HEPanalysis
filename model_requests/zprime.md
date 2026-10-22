# Model request: `zprime` (a Z′ for a dilepton resonance search)

**Requested by**: HEPanalysis T10, a Z′ → ℓℓ bump hunt on ATLAS Open Data dileptons. The σ × BR
limit is turned into the (g′, M_Z′) plane. This is the course's first BSM search.

**Status**: open. Filed on 2026-10-22 at the user's request. It needs `model_requests/sm_qcd.md`
as its base, for the light quarks (Drell–Yan production) and e, μ. Nothing is built from here.

**Minimum level requested**: **L4**.

## Motivation

feynlag-models has no new gauge boson. feynlag already has the model in symbolic form:
`docs/tutorials/SM_U1X_Tutorial.ipynb` and `examples/sm_u1x.py` gauge a U(1)_X with
family-universal charges X = a Y + b (B − L), plus three ν_R, keeping a, b and the
symmetry-breaking singlet's charge q_S symbolic.

Two facts make this family the natural choice:
- With three ν_R, Y and B − L are the only family-universal anomaly-free abelian charges, so this
  is the most general consistent choice. Appelquist, Dobrescu, Hopper, Phys. Rev. D 68, 035012
  (2003), hep-ph/0212073; checked on INSPIRE 2026-10-22.
- It has the standard limits: a = 0 is pure B − L, and a ≠ 0, b = 0 is "hypercharge-like".

## Requested content

- Parent: the hadron-ready SM base (`model_requests/sm_qcd.md`), extended by U(1)_X with coupling
  g_X and a complex singlet S that breaks it (charge q_S). The Z′ gets its mass from ⟨S⟩.
- **The UFO must not need Majorana vertices**, because FG-3 is open. How ν_R is handled is the
  implementer's choice:
  - Dirac ν_R, by choosing q_S so that the ν_R Majorana term is forbidden; or
  - heavy ν_R left out of the exported scope (`ufo_scope.omitted`).
  Either way, record whether Z′ → ν_R ν̄_R enters Γ_Z′, because that changes BR(Z′ → ℓℓ) and
  therefore the limit T10 derives.
- Z–Z′ mass mixing (when a ≠ 0, through the Higgs's X charge) is kept and diagonalised. The
  mixing angle should be an exported internal parameter.
- Benchmark inputs in the physical basis: M_Z′, g_X, a, b. Γ_Z′ is computed, not a placeholder
  (with `DecayCalculator`; or as `Auto` after HG-1).
- The pure B − L benchmark (a = 0) should be one of the documented benchmark points.

## What calculation requires it

T10:
1. pp → Z′ → e⁺e⁻/μ⁺μ⁻ signal templates with MG5 → Pythia8 → Delphes;
2. a fit to the dilepton mass spectrum of the Open Data;
3. a 95% CL limit on σ × BR(ℓℓ) against M_Z′;
4. the translation to g_X against M_Z′ for the chosen (a, b).

Step 4 needs the model's own σ(g_X, M_Z′) and BR(ℓℓ).

## Checks requested

- **L2 (literature):** the Z′ fermion couplings g_X X_f, and the Z′ partial widths to massless
  fermions. One review to compare against is Langacker, Rev. Mod. Phys. 81, 1199 (2009),
  arXiv:0801.1345; the implementer chooses which equations and records their conventions.
- **L4:** σ(pp → Z′ → μ⁺μ⁻) at 13 TeV, compared with an independent implementation. Options
  are an analytic narrow-width σ from the model's own couplings plus a PDF luminosity, or a
  public B − L UFO; the implementer chooses and verifies.
