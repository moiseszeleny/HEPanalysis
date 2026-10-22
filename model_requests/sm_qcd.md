# Model request: `sm_qcd` (a hadron-collider SM base)

**Requested by**: HEPanalysis, for every tutorial that simulates proton collisions with a
feynlag-models UFO (Track B: T08–T13). Track A uses MadGraph's stock `sm` until this exists.

**Status**: open. Filed on 2026-10-22 at the user's request ("Check the gaps … and do request to
fill these gaps"). Nothing is built from here: building happens in `feynlag-models`, under its
own rules.

**Minimum level requested**: **L4**, meaning a MadGraph cross-section check with `slow_evidence`.
The point of this model is to be the validated base that every LHC tutorial stands on.

## Motivation

No feynlag-models UFO can describe a proton collision today.

- **The BSM models have one generation and no gluon.** `sm_singlet_z2` and `thdm_type2` inherit
  the one-generation `sm`: t, b, τ and ν_τ. They have no u, d, s, c, no e, μ, and no gluon.
  - At import, MadGraph reports `impossible to set default multiparticles p because No particle
    g in model`.
  - `generate p p > h2` stops with `InvalidCmd : No particle p in model`.
  - Evidence: `docs/evidence/ufo_probe_2026-10-22.md` P1/P2.
- **`sm_ckm` has all three generations but still no gluon.** It defines `l+`, `l-`, `vl` and
  `vl~`, but not `p` or `j` (same file).
- **No vertex carries colour.** `ufo_check` finds no colour-charged vertex in any of the four
  UFOs. The quarks carry `Identity(1,2)` colour flow only.
- **This was already foreseen upstream.** `models/sm/NEXT_STEPS.md:34-36` says
  "hadron-collider use needs the gluon sector (feynlag supports it; not wired here)", and
  proposes the child `sm_qcd_ufo` (line 6).
- **The feynlag writer already supports colour.** It handles `T`, `f` and `d` colour tensors and
  assigns `QCD` coupling orders (`src/feynlag/export/ufo/writer.py:112-124`). feynlag's own
  MadGraph check of u ū → gg is in `scripts/madgraph_qcd.py`.

## Requested content

The id and the parent are the implementer's choice. The natural option is a child of `sm_ckm`
(it `extends` it).

- All three generations, as in `sm_ckm`. Electrons and muons are needed for Drell–Yan
  calibration and for Z′ → ee/μμ (`model_requests/zprime.md`).
- The SU(3)_c gauge sector, exported: the gluon (PDG 21), the q q̄ g vertices with `T` colour
  tensors, and the ggg and gggg self-couplings.
- The u, d, s, c quarks massless at the benchmark, or a 5-flavour option with a massless b. Then
  MadGraph's default `p`/`j` multiparticles are defined. The flavour scheme chosen should be
  recorded in `metadata.yaml`.
- The strong coupling exported so that MadGraph runs it. This depends on HG-1 in
  `docs/upstream_gaps.md`: today MadGraph replaces it with a dummy `AS = 0.138` (probe P3). If
  HG-1 is not fixed first, the request is still useful at fixed αs, but `ufo_scope.omitted`
  should say so.

## What calculation requires it

T02 and T03 compare the feynlag UFO with MadGraph's stock `sm` for Drell–Yan, tt̄ and WW. After
that, every Track B model is re-based on this base (`model_requests/lhc_scalars.md`,
`zprime.md`, `vll.md`).

## L4 checks requested

These are cross sections at √s = 13 TeV, comparing the feynlag UFO with the stock MadGraph `sm`
using the same PDF set, scales, cuts and MadGraph version. They should agree within Monte Carlo
uncertainty.
- σ(pp → Z → ℓ⁺ℓ⁻) with a dilepton mass window;
- σ(pp → tt̄);
- σ(pp → W⁺W⁻).

The comparison needs no literature value: the stock model is the independent implementation.
Record any convention difference (for example the electroweak input scheme) in `discrepancies`.

## Anticipated feynlag gaps (for the implementer; not claimed as found)

- **HG-1** (the SLHA blocks and the `aS`/`G` naming) decides whether αs runs.
- With three generations and a CKM matrix, the UFO grows. feynlag-models' `export_ufo` currently
  calls `Model.gauge_vertices(groups=[SU2L], …)` because "the unbroken `SU3c` every model
  declares raises" (`feynlag-models/CLAUDE.md`, Architecture section). Exporting the gluon
  self-couplings needs that path to work for `SU3c`. If it does not, that is an FG entry.
