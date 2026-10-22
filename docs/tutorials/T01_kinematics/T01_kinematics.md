---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# T01 · Kinematics and physics objects

A detector does not record "a Z boson". It records objects: muons, electrons, photons, jets,
missing transverse momentum. Each comes with a direction, an energy, and a list of quality
flags that some reconstruction group decided were sensible. This tutorial works with real
ATLAS muons from 2015. You rebuild the two quantities every later search uses, the invariant
mass and the angular distance ΔR, from the stored variables, and then look at what the
quality flags do to the sample.

**Paper anchor.** ATLAS Collaboration, *The ATLAS Experiment at the CERN Large Hadron
Collider*, JINST 3, S08003 (2008) *(cited)*. It is the detector paper. Its inner tracker, which
every muon here is matched to, covers |η| < 2.5. Step 0 checks the data against that.

**Data.** All events of the ATLAS 2015 run period D in the `2muons` skim of the 2025 Open Data
release for education (`2025e-13tev-beta`, CC0). The cut-down copy committed in
`../data/` was made by `../data/prepare_2muons.py`. Its provenance (URLs, release, tool
versions) is in `../data/provenance.json`.

```{code-cell} ipython3
import json
from pathlib import Path

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np

from hepanalysis.objects import delta_phi as lib_delta_phi, invariant_mass

import t01_solutions as sol
from t01_checks import check_1, check_2, check_3, check_4, flaw

prov = json.loads(Path("../data/provenance.json").read_text())
pairs = sol.load_pairs()
print(f"release {prov['release']}, skim {prov['skim']}: {len(pairs)} events with exactly two leptons")
```

## 0. Look before you compute

```{code-cell} ipython3
eta = ak.to_numpy(ak.flatten(pairs.lep_eta))
pt = ak.to_numpy(ak.flatten(pairs.lep_pt))
types, counts = np.unique(ak.to_numpy(ak.flatten(pairs.lep_type)), return_counts=True)
print("lepton types (PDG |id|):", dict(zip(types.tolist(), counts.tolist())))
print(f"max |eta| = {np.abs(eta).max():.4f},  min pT = {pt.min():.2f} GeV")
assert np.abs(eta).max() < 2.5
```

**Read it.** Every lepton has |η| < 2.5 *(computed)*, which is the tracker acceptance of the
detector paper *(cited)*. There are no muons outside the tracker in this sample. The minimum
pT of exactly 10 GeV is a **skim cut**, not physics. In events with exactly two leptons,
both are muons *(computed)*. Events with three or more leptons in the same skim do contain
electrons, so a selection still has to ask for muons explicitly.

## 1. The invariant mass, by hand

The files store each lepton as $(p_T, \eta, \phi, E)$. With
$p_x = p_T\cos\phi$, $p_y = p_T\sin\phi$ and $p_z = p_T\sinh\eta$,

$$m_{12}^2 = (E_1 + E_2)^2 - |\vec p_1 + \vec p_2|^2 .$$

> **Before running the next cell.** Two muons of 45 GeV each, back to back in the transverse
> plane at η = 0: what is their invariant mass? And what if both have η = 1 instead?

```{code-cell} ipython3
def my_invariant_mass_pair(pt1, eta1, phi1, e1, pt2, eta2, phi2, e2):
    # your code here: numpy arrays in, numpy array of masses out
    raise NotImplementedError


check_1(my_invariant_mass_pair)
mass_pair = check_1.use(my_invariant_mass_pair)

masses = mass_pair(*sol.pair_columns(pairs))
library = ak.to_numpy(invariant_mass(pairs.lep_pt, pairs.lep_eta, pairs.lep_phi, pairs.lep_e))
assert np.allclose(masses, library, rtol=1e-5, atol=1e-4)
print(f"{len(masses)} masses; agrees with hepanalysis.objects.invariant_mass")
```

From here on the library function is used. It is the same formula: the assert above shows
the two agree.

```{admonition} Precision is physics too
:class: note
The files store float32. For a light, boosted pair, $E^2$ and $|\vec p|^2$ are nearly equal,
and in float32 their difference loses most of its digits. On this sample a 0.32 GeV dimuon
comes out at 0.43 GeV if the arithmetic stays in float32 *(computed while writing this
tutorial)*. Both your function and the library convert to float64 first. Check that any code
you reuse does the same.
```

## 2. Angles wrap around

ΔR = √(Δη² + Δφ²) measures how close two objects are. It enters isolation cones,
overlap removal and jet matching. φ is an angle, so Δφ has to be wrapped into (−π, π].

```{code-cell} ipython3
def my_delta_phi(phi1, phi2):
    # your code here
    raise NotImplementedError


check_2(my_delta_phi)
dphi = check_2.use(my_delta_phi)
assert np.allclose(dphi(np.array([3.0, 0.5]), np.array([-3.0, 0.2])), lib_delta_phi(np.array([3.0, 0.5]), np.array([-3.0, 0.2])))
```

## 3. The dimuon mass spectrum

> **Before running the next cell.** Which peaks do you expect between 1 and 120 GeV in
> opposite-sign dimuons? Write down their masses before you look.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(masses, bins=np.logspace(np.log10(0.25), np.log10(300), 300), histtype="step", color="k")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel(r"$m_{\mu\mu}$ [GeV]"); ax.set_ylabel("events / bin")
plt.show()
```

```{code-cell} ipython3
def my_peak_position(masses, lo, hi, width):
    # your code here: centre of the most populated bin of width `width` in [lo, hi)
    raise NotImplementedError


check_3(my_peak_position)
peak = check_3.use(my_peak_position)
for lo, hi, width in [(2.5, 3.7, 0.02), (8.0, 11.0, 0.05), (70.0, 110.0, 0.5)]:
    print(f"most populated bin in [{lo}, {hi}): {peak(masses, lo, hi, width):.3f} GeV")
```

**Read it.** Three structures stand out *(computed)*: one near 3.1 GeV (J/ψ), one near
9.5 GeV (the ϒ family), and the Z near 91 GeV. A bin maximum is a crude estimate of a mass.
T02 fits the Z peak properly and compares it with the measured Z mass.

## 4. What the quality flags do

Every lepton carries an identification flag (`lep_isMediumID`) and an isolation flag
(`lep_isLooseIso`, little activity around the track). Muons from Z decays are "prompt" and
alone. Muons from b- and c-hadron decays sit inside jets.

> **Before running the next cell.** Is the fraction of events whose two muons are both
> isolated higher at 20–60 GeV or at 80–100 GeV? By how much?

```{code-cell} ipython3
def my_isolated_fraction(both_isolated, masses, lo, hi):
    # your code here
    raise NotImplementedError


check_4(my_isolated_fraction)
iso_fraction = check_4.use(my_isolated_fraction)
both_iso = np.asarray(pairs.lep_isLooseIso[:, 0] & pairs.lep_isLooseIso[:, 1])
f_low, f_z = iso_fraction(both_iso, masses, 20, 60), iso_fraction(both_iso, masses, 80, 100)
print(f"both isolated: {f_low:.1%} at 20-60 GeV, {f_z:.1%} at 80-100 GeV")
assert f_z > 3 * f_low
```

**Read it.** Near the Z almost all pairs pass isolation. Between 20 and 60 GeV only about a
quarter do *(computed)*. The low-mass continuum here is dominated by non-prompt muons from
heavy-flavour decays, which is a statement about the *sample*, not about Drell–Yan. An
isolation cut is therefore a background-rejection decision, and its efficiency for the
signal has to be known separately. T02 does that with the MC scale factors.

```{admonition} Would you trust this?
:class: warning
The flags are ATLAS's definitions, and this course cannot re-derive their efficiencies. When
a later tutorial compares data with simulation, the simulation has to be corrected for the
difference in flag efficiencies between data and MC (the `ScaleFactor_*` branches). Ask of
any recast: does it model the experiment's ID and isolation efficiencies, or does it assume
they are 100%?
```

## 5. Find the flaw

An overlap-removal step drops a muon if any jet lies within ΔR < 0.4. It is coded as

```python
def naive_delta_r(eta1, phi1, eta2, phi2):
    return np.sqrt((eta1 - eta2) ** 2 + (phi1 - phi2) ** 2)
```

What is wrong?

```{code-cell} ipython3
for key, text in flaw.options.items():
    print(f"  {key}) {text}")

my_flaw_answer = None   # your answer: "a", "b", "c" or "d"
flaw(my_flaw_answer)
```

## 6. Explore

In a live kernel, move the pT threshold and toggle isolation to see which part of the
spectrum each cut removes. The static documentation shows one fixed setting.

```{code-cell} ipython3
lead_pt = np.asarray(ak.max(pairs.lep_pt, axis=1))

def plot_spectrum(min_pt=10.0, require_isolation=False):
    keep = (lead_pt > min_pt) & (both_iso if require_isolation else True)
    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.logspace(np.log10(0.25), np.log10(300), 200)
    ax.hist(masses, bins=bins, histtype="step", color="grey", label="all")
    ax.hist(masses[keep], bins=bins, histtype="step", color="k", label="selected")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.legend()
    ax.set_xlabel(r"$m_{\mu\mu}$ [GeV]"); ax.set_title(f"kept {keep.mean():.1%}")
    plt.show()

import ipywidgets as w
from hepanalysis.notebook import explore

explore(plot_spectrum, static=dict(min_pt=25.0, require_isolation=True),
        min_pt=w.FloatSlider(value=10, min=10, max=60, step=1),
        require_isolation=w.Checkbox(value=False))
```

## Recap

- $(p_T, \eta, \phi, E) \to m$: the formula is three lines. The library version agrees with it
  to floating-point precision (*computed*).
- Δφ must be wrapped. An unwrapped ΔR silently breaks isolation and overlap removal near
  φ = ±π.
- Real dimuon spectra show J/ψ, ϒ and Z. The continuum between them depends on the sample
  definition: isolation keeps about 94% of pairs near the Z, but only about 27% at 20–60 GeV
  (*computed*).

**Judgment exercises (no solutions).**
1. The skim requires pT > 10 GeV. Which part of the low-mass spectrum does that sculpt, and
   would you fit the J/ψ line shape on this sample?
2. A pheno paper recasts a dimuon search with Delphes and no isolation requirement. In which
   mass range is its background estimate least reliable?
