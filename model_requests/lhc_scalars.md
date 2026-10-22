# Model request: LHC-ready `sm_singlet_z2` and `thdm_type2`

**Requested by**: HEPanalysis:
- T08 (from Lagrangian to UFO);
- T09 (validate your UFO);
- T11 (heavy scalar: h2/H → ZZ → 4ℓ, the sin θ and (tan β, cos(β−α)) interpretations).

**Status**: open. Filed on 2026-10-22 at the user's request. Item 1 depends on
`model_requests/sm_qcd.md`, and item 2 partly on HG-1 (`docs/upstream_gaps.md`). Nothing is
built from here.

**Minimum level requested**: **L4**.

## Motivation

Both models are L3 and verified against the literature. Four things keep them out of a
hadron-collider analysis. Evidence is from `python -m hepanalysis.ufo_check <id>` and
`docs/evidence/ufo_probe_2026-10-22.md`.

1. **No proton.** They are built on the one-generation `sm`, with no gluon (P2:
   `InvalidCmd : No particle p in model`).
2. **Placeholder widths.**
   - `WH2` (singlet) and `WHH`, `WA0`, `WHp` (2HDM) are 1.0 GeV and listed under
     `benchmark.placeholders`.
   - MadGraph cannot compute them either: `compute_widths h2` raises
     `NameError: name 'aS' is not defined` (P4; see HG-1).
   - A resonance search depends directly on Γ, both for the line shape and for whether the
     narrow-width approximation holds.
3. **The singlet benchmark has its light Higgs at 120.44 GeV.**
   - `build("sm_singlet_z2").values()["MH1"]` = 120.443 GeV, consistent with `outputs/spectrum.md`
     and the README ("m_{h_1} ≈ 120 GeV").
   - λ is set from MH = 125 GeV before mixing, and the mixing then pushes h1 down.
   - The measured mass is 125.20 ± 0.11 GeV (PDG 2024, S. Navas et al., Phys. Rev. D 110, 030001,
     "OUR AVERAGE", pdglive S126M; read 2026-10-22).
   - An LHC tutorial has to start from a point where h1 *is* the observed Higgs.
4. **The inputs are in the λ basis.**
   - Analyses scan physical quantities: (m_h2, sin θ) for the singlet, and
     (m_H, m_A, m_{H±}, tan β, cos(β−α)) for the 2HDM.
   - This is the open question in `models/thdm_type2/NEXT_STEPS.md` §3 and the "no physical-basis
     input inversion" item in §4. For the 2HDM the tree-level inversion already exists by hand
     (`benchmark.derived_from`, Gunion–Haber Eqs. 10–13).

## Requested changes

The implementer may change the existing models or add LHC children, e.g. `sm_singlet_z2_lhc`.
- Re-base on the hadron-ready SM (`model_requests/sm_qcd.md`).
- Physical-basis external inputs, with the λ_i as `InternalParameter`s:
  - singlet: (m_h1, m_h2, sin θ, v_S), with m_h1 at the cited measured value;
  - 2HDM: (m_h, m_H, m_A, m_{H±}, tan β, cos(β−α), m_12²).
  The reverse map should be pinned by a test, as `derived_from` already is.
- Widths computed for the new states at the benchmark, instead of placeholders. Either:
  - with feynlag's `DecayCalculator` (`feynlag.pheno`, tree-level 1 → 2 and off-shell
    h → WW\*/ZZ\*; `models/sm_singlet_z2/NEXT_STEPS.md` already names Γ(h2 → h1h1)); or
  - once HG-1 is fixed, as `DECAY … Auto` entries that MadGraph computes.
  If both are available, the comparison between them is a useful L4 cross-check.
- Loop-induced gg → S and S → γγ need HG-2. Until then, `ufo_scope.omitted` should say so.

## L4 checks requested

- **Singlet.** σ(pp → h2 jj, VBF) = sin²θ × σ(stock MadGraph `sm`, with m_H set to m_h2), at
  √s = 13 TeV with the same PDF, scales and cuts. This follows from the key result "every h2
  coupling = SM coupling × (−sin θ)", so it needs no literature number.
- **2HDM.**
  - A cross section compared with an independent public 2HDM UFO, such as one from the FeynRules
    model database. Which UFO to use, and its conventions, is for the implementer to verify.
  - The channels are the implementer's choice, e.g. pp → H → ZZ via VBF, or pp → t b H±.
  - The convention map (signs of A and H±, already discrepancy D-3) is recorded in `metadata.yaml`.

## Notes

- T11's fallback for gg → h2 before HG-2 is the cited SM gluon-fusion cross section × sin²θ
  (LHC Higgs Cross Section Working Group YR4, arXiv:1610.07922). That fallback is valid for the
  singlet only.
- The 2HDM's existing bounds table (`models/thdm_type2/NEXT_STEPS.md` §2) is what T11 will
  compare against. Its `TODO(verify)` rows are where T14's HEPData reinterpretation can help.
