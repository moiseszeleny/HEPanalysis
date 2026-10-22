# Model request: `seesaw_lhc` (a heavy-neutrino UFO for LHC searches)

**Requested by**: HEPanalysis T13: heavy neutrinos, the same-sign dilepton + jets signature of
lepton-number violation, and where fast detector simulation stops (displaced vertices).

**Status**: **blocked on FG-3** (`feynlag-models/FEYNLAG_GAPS.md`: feynlag has no UFO path for
Majorana fermions; feynlag `docs/roadmap.md` item E). Filed on 2026-10-22 at the user's request,
so that the demand is recorded. Do not start it until FG-3 is resolved. Nothing is built from
here.

**Minimum level requested**: **L4**, once FG-3 is resolved.

## Motivation

`seesaw_type1` and `seesaw_type1_2n` are L2 and literature-checked, and their heavy-neutrino
couplings (W ℓ N, Z ν N, h ν N) exist symbolically. They ship no UFO: `seesaw_type1/model.py`
sets `extra["ufo"] = False`, and `hepanalysis.models.ufo_path("seesaw_type1")` is `None`. That
is pinned here by `tests/test_upstream_gaps.py::test_heavy_neutrino_model_ships_a_ufo`.

## Requested content (after FG-3)

- A type-I seesaw on the hadron-ready base (`model_requests/sm_qcd.md`), with at least one heavy
  Majorana N mixing with e and μ. The light-neutrino sector of `seesaw_type1_2n` can be reused.
- Benchmark inputs in the physical basis: m_N and the active–sterile mixing |V_ℓN|². Γ_N is
  computed, and with it whether N decays promptly at the benchmark, which T13 needs.

## Checks requested

- **L4:** σ(pp → W\* → ℓ N) at 13 TeV, compared with an independent public heavy-neutrino UFO.
  The HeavyN models of Degrande, Mattelaer, Ruiz, Turner, Phys. Rev. D 94, 053002 (2016),
  arXiv:1602.06957 are one option; the implementer verifies the reference and the convention
  map.
- Lepton-number violation: the same-sign and opposite-sign ℓℓ rates should come out equal for a
  single Majorana N at the benchmark. That is a direct test of the Majorana fermion-flow handling
  FG-3 introduces.
