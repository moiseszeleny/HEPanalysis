# Syllabus

Each tutorial is a solved notebook in `docs/tutorials/`. It follows the stack's style: a
prediction before each step, `MOVE` cells, an `assert` behind every claim, a **Would you trust
this?** box, and a recap. Judgment exercises come without solutions.

The last column lists what each tutorial waits for upstream (`upstream_gaps`). Track A depends
on nothing upstream, so it is written first.

## Track A: foundations, using only SM benchmarks

The SM results come first so that every later BSM claim has something to be compared with.

| id | tutorial | data | blocked by |
|---|---|---|---|
| T00 | Anatomy of a search: Lagrangian → UFO → events → objects → selection → likelihood → limit → reinterpretation. What a theorist can and cannot do with public results | — | — |
| T01 | Kinematics and physics objects: pT, η, invariant mass, missing ET, isolation | ATLAS Open Data | — |
| T02 | **Rediscover the Z**: the dilepton peak, then MadGraph σ × BR × L × ε against the observed yield. Calibrates trust in the scale, resolution and efficiency | Open Data + MadGraph `sm` | — |
| T03 | The simulation chain: σ, PDFs, scale uncertainties, K-factors, weights and luminosity | MadGraph `sm` → Pythia8 → Delphes | — |
| T04 | Backgrounds: Monte Carlo against data-driven estimates (sidebands, ABCD, fake factors) | Open Data | — |
| T05 | Statistics I, by hand: Poisson likelihood, profile likelihood, CLs, Asimov; then pyhf | toy + Open Data | — |
| T06 | Statistics II: shape fits, nuisance parameters, the look-elsewhere effect, discovery against exclusion | Open Data | — |
| T07 | **Rediscover the Higgs**: H → γγ and H → ZZ\* → 4ℓ; local and global significance, signal strength μ. The template the BSM tracks reuse | Open Data | — |

## Track B: BSM searches with feynlag-models

| id | tutorial | model | blocked by |
|---|---|---|---|
| T08 | From Lagrangian to UFO: registry → UFO → param card; reading a UFO; `ufo_check` | `sm_singlet_z2`, `thdm_type2` | `sm_qcd`, `lhc_scalars` (part needs HG-1) |
| T09 | **Validate your UFO**: compare with an independent implementation; check the narrow-width approximation, interference and widths | as T08 | as T08 |
| T10 | Z′ → ℓℓ: a bump hunt on the Open Data dileptons; σ × BR limit, then (g′, M_Z′) | `zprime` | `sm_qcd`, `zprime` |
| T11 | Heavy scalar h2/H → ZZ → 4ℓ (reusing T07); sin θ for the singlet, (tan β, cos(β−α)) for the 2HDM | `sm_singlet_z2`, `thdm_type2` | `lhc_scalars`; gg → S needs HG-2 (cited fallback for the singlet only) |
| T12 | Vector-like leptons: multilepton counting with control regions | `vll` | `sm_qcd`, `vll` |
| T13 | Heavy neutrinos: same-sign dileptons + jets (lepton-number violation); where Delphes stops (displaced vertices) | `seesaw_lhc` | **FG-3** |

## Track C: reinterpretation and judgment

| id | tutorial | data | blocked by |
|---|---|---|---|
| T14 | HEPData + published full likelihoods (pyhf patchsets): reinterpret an ATLAS search for a Track B model | HEPData | a Track B model at L4 |
| T15 | The recast-tool landscape (MadAnalysis5 PAD, CheckMATE, SModelS, Contur): when to use each; validating a recast against a published cutflow | HEPData | — |
| T16 | Case studies in judgment: the 750 GeV diphoton excess, the 95 GeV excess (feynlag-anomalies `higgs_95gev`), reading an experimental paper, a trust checklist | literature | — |

The facts about ATLAS Open Data (file locations, the metadata interface, the licence of the
outreach notebooks) are `TODO_VERIFY`. They are checked when T01 is written.
