# Upstream gaps: what HEPanalysis needs from `feynlag` and `feynlag-models`

These are problems found here that block tutorials in this repo but have to be fixed upstream.
This repo never edits a sibling repo (`../CLAUDE.md`). Each entry below is a proposal; the hub
relays it, and the fix comes back as a pin bump.

Ids are `HG-n`. That keeps them apart from feynlag-models' `FG-n` and feynlag-anomalies' `UG-n`.
Requests for new or changed models live in `model_requests/<id>.md`.

Every open item is pinned by a strict xfail in `tests/test_upstream_gaps.py`. When a pin bump
fixes the gap, that test XPASSes and the suite fails. The entry then moves to **Resolved** and
the xfail marker comes off.

The evidence comes from two places, both at the pins in `pyproject.toml` (feynlag 0.3.0,
feynlag-models `cb0678a`):
- `python -m hepanalysis.ufo_check <model_id>`: a static read of the UFO files;
- [`docs/evidence/ufo_probe_2026-10-22.md`](evidence/ufo_probe_2026-10-22.md): MadGraph 3.7.2
  run on copies of the UFOs, written by `scripts/probe_mg5.py`.

## Open

### HG-1: the UFO writer puts every parameter in one non-SLHA block and has no `aS` (`feynlag`)

**Repo**: `feynlag`. **Discovered**: 2026-10-22, while preparing the first MadGraph tutorials.
**Blocks**: every tutorial that simulates a feynlag-models BSM state (T03 onward for Track B);
automatic widths; Pythia and MadSpin reading masses and widths from the event file's SLHA header.

**Symptom**: `write_ufo` gives every external parameter `lhablock='FEYNLAG'`
(`src/feynlag/export/ufo/writer.py:497` on `main`). That includes particle masses
(`MT`, `MB`, `MTA`), widths (`WZ`, `WW`, `WH`, `WT`, and the BSM `WH2`, `WHH`, `WA0`, `WHp`)
and the strong coupling, which is called `gs`. `ufo_check` reports `FEYNLAG` as the only block
in all four shipped UFOs (`sm`, `sm_ckm`, `sm_singlet_z2`, `thdm_type2`). The MadGraph probe
shows three consequences, the same for all four models:

1. **Editing a width in the DECAY block does nothing.**
   - MadGraph writes `Block MASS` and the `DECAY` lines into the param card under the header
     "Dependent parameters … MG5 ignores those values but they are important for interfacing
     the output of MG5 to external program such as Pythia".
   - The matrix element reads the width from `FEYNLAG` (e.g. `WH2` is `FEYNLAG 16`, `WHH` is
     `FEYNLAG 19`).
   - So editing `DECAY 35` does not reach the calculation (MadGraph's own header says so), and
     `set DECAY 35 Auto` runs the width computation that fails in point 3.
   - By the same header, the ignored copy is the one handed on to Pythia, so the two values can
     disagree with no warning.
2. **MadGraph inserts a dummy strong coupling.**
   - There is no parameter named `aS`, so MadGraph writes `AS = 1.380000D-01` into
     `Source/MODEL/intparam_definition.inc` (lines 42, 88, 62 and 109 for the four models).
     This matches MG5 3.7.2 `madgraph/iolibs/export_v4.py:7081-7084`, which adds a dummy `aS`
     when the model has none.
   - Today this is harmless only because the UFOs have no QCD vertices. Once gluon vertices are
     exported (`model_requests/sm_qcd.md`), the QCD couplings would be built from a fixed `gs`,
     while MadGraph runs only `G`/`aS` with the scale.
3. **Automatic widths are impossible.**
   - `compute_widths <X>` stops with `NameError: name 'aS' is not defined`, raised in MG5 3.7.2
     `mg5decay/decay_objects.py:1959` (`read_param_card`).
   - This happens for `z` in `sm` and `sm_ckm` and for `h2` in `sm_singlet_z2` and `thdm_type2`.
   - The model's width parameter is left unchanged: `WH2` is still `FEYNLAG 16 = 1.0`.

**Proposal** (the design is feynlag's call):
1. Write each particle's external mass as `lhablock='MASS', lhacode=[pdg]` and its external width
   as `lhablock='DECAY', lhacode=[pdg]`.
2. Export the strong coupling as an external `aS` (`SMINPUTS`, code 3) plus an internal
   `G = 2*cmath.sqrt(aS)*cmath.sqrt(cmath.pi)`, and write every QCD coupling in terms of `G`, as
   the stock MadGraph `sm` does.
   - This could be a mapping inside the writer, so that models keep their own symbol (`gs`) and
     feynlag-models' tests are unaffected.
   - Optionally, offer the `aEWM1`/`Gf`/`MZ` electroweak input scheme in `SMINPUTS` as well.
3. Keep the remaining model parameters in a model block, as now.
4. Pin it with a MadGraph round-trip test: `compute_widths` runs, and `set DECAY <pdg> Auto`
   changes the width the matrix element uses.

**Pinned here by**:
- `tests/test_upstream_gaps.py::test_masses_and_widths_live_in_slha_blocks`
- `tests/test_upstream_gaps.py::test_strong_coupling_is_named_aS`

**Status**: open. Filed on 2026-10-22 at the user's request ("Check the gaps … and do request to
fill these gaps"). Nothing in feynlag was touched from here.

### HG-2: no UFO path for the loop-induced scalar couplings to gluons and photons (`feynlag`)

**Repo**: `feynlag`. **Discovered**: 2026-10-22. **Blocks**: T11 (heavy scalar). Gluon fusion
gg → S is the main production mode of a heavy neutral scalar at the LHC.

**Symptom**:
- The exported vertex classes are tree-level only: FFS, FFV, SSS, SSSS, VSS, VVS, VVSS, VVV,
  VVVV (`feynlag-models/models/thdm_type2/metadata.yaml`, `outputs.ufo_scope`).
- feynlag already evaluates the SM-like effective gg, γγ and Zγ couplings for decays
  (`src/feynlag/pheno/loop.py`).
- There is no operator for S G^a_{μν} G^{aμν} or S F_{μν}F^{μν}. The `FieldStrength` building
  block is noted in `docs/roadmap.md` (phase C3) as never implemented. There is also no UFO
  Lorentz structure for such a vertex.
- So a feynlag UFO cannot produce `g g > h2`, even after the gluon sector is exported.

**Proposal**: an effective dimension-5 route. Add the S GG and S AA operators, with the Wilson
coefficient computed from the model's own couplings through `pheno/loop.py`. Export them with the
Lorentz structures MadGraph's `heft` model uses for its effective ggh vertices; the three- and
four-gluon contact terms are needed for gauge invariance. The normalisation and the set of
vertices are for feynlag to derive and cite.

**Fallback used here until then**: for the singlet only, gg → h2 is taken as
sin²θ × σ(gg → H_SM at m_{h2}), tagged as a cited cross section from the LHC Higgs Cross Section
Working Group (YR4, arXiv:1610.07922). This works only because every h2 coupling is the SM one
× (−sin θ) (`sm_singlet_z2` key result). It does **not** carry over to the 2HDM, where the top
and bottom loops are rescaled differently, so T11 will say so.

**Status**: open, lower priority than HG-1. Filed on 2026-10-22 at the user's request. Nothing
in feynlag was touched from here.

### FG-3 (existing, feynlag-models): one more consumer, no new ticket

The Majorana UFO export (`feynlag-models/FEYNLAG_GAPS.md` FG-3; feynlag `docs/roadmap.md` item E)
also blocks T13 here: heavy neutrinos, and the same-sign dilepton signature of lepton-number
violation. This entry only records that HEPanalysis now consumes FG-3 too. The fix and the
ticket stay where they are.

- **Pinned here by**: `tests/test_upstream_gaps.py::test_heavy_neutrino_model_ships_a_ufo`.
- **Model side**: `model_requests/seesaw_lhc.md`, which is blocked on FG-3.

## Model requests (`model_requests/`, consumed by feynlag-models)

| request | what | unblocks | status |
|---|---|---|---|
| [`sm_qcd`](../model_requests/sm_qcd.md) | a hadron-collider SM base: three generations, gluon + QCD vertices, L4 against MadGraph's `sm` | all pp simulation | open |
| [`lhc_scalars`](../model_requests/lhc_scalars.md) | `sm_singlet_z2` and `thdm_type2` on that base: computed widths, physical-basis inputs, a benchmark with m_h1 at the measured Higgs mass, L4 | T08, T09, T11 | open (part of it needs HG-1) |
| [`zprime`](../model_requests/zprime.md) | a Z′ from the U(1)_X family, with an exportable UFO, L4 | T10 | open |
| [`vll`](../model_requests/vll.md) | a vector-like lepton mixing with τ, L4 | T12 | open |
| [`seesaw_lhc`](../model_requests/seesaw_lhc.md) | a heavy-neutrino UFO on the hadron base | T13 | blocked on FG-3 |

## Resolved

(none yet)
