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

# T02 · Rediscover the Z

The Z boson is the standard candle of a hadron collider. Its mass and width are known to a
few parts in 10⁵, and it is produced copiously. It decays to two clean, isolated leptons.
Every search that uses leptons first checks that it can see the Z correctly. This tutorial
does that check on real 2015 ATLAS data. It has three steps:

1. select Z → μμ candidates;
2. fit the peak and compare the mass with the measured value;
3. compare the event yield with the simulation.

Each step fails in an instructive way before it succeeds, and the failures are the lesson.

**Paper anchor.** ATLAS Collaboration, *Measurement of W± and Z-boson production cross
sections in pp collisions at √s = 13 TeV with the ATLAS detector*, Phys. Lett. B 759, 601
(2016), arXiv:1603.09222 *(cited)*. It used 81 pb⁻¹ of 2015 data, a sample about this size,
and measured σ(Z → ℓℓ, 66 < m_ℓℓ < 116 GeV) = 1.981 ± 0.007 (stat) ± 0.038 (sys) ± 0.042
(lumi) nb. The luminosity uncertainty is larger than the statistical one. Keep that in mind
for step 3.

```{code-cell} ipython3
import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import Markdown, display

from hepanalysis.cutflow import Cutflow
from hepanalysis.plotting import data_mc
from hepanalysis.provenance import Computed

import t02_solutions as sol
from t02_checks import check_1, check_2, check_3, flaw

data, mc, prov = sol.load()
print(f"data: {len(data)} events (2015 period D); MC: {len(mc)} events from DIDs "
      f"{sorted({int(d) for d in ak.to_numpy(mc.did)})}")
```

## 1. Select Z → μμ candidates

The selection is:
- exactly two leptons, both muons, with opposite charge;
- both pass medium identification and loose isolation (T01 showed what isolation does);
- both have pT > 25 GeV;
- the single-muon trigger fired and is matched to at least one of the two.

> **Before running the next cell.** Which cut removes the most events from this skim? Your
> T01 isolation numbers are a clue.

```{code-cell} ipython3
def my_select(ev):
    # your code here: return a numpy boolean mask, one entry per event
    raise NotImplementedError


check_1(my_select)
select = check_1.use(my_select)

pairs = ak.pad_none(data.lep_type, 2)
q = ak.pad_none(data.lep_charge, 2)
cf = Cutflow(data)
cf.apply("exactly two leptons", ak.to_numpy(data.lep_n == 2))
cf.apply("both muons", ak.to_numpy(ak.fill_none((ak.pad_none(cf.events.lep_type, 2)[:, 0] == 13)
                                                & (ak.pad_none(cf.events.lep_type, 2)[:, 1] == 13), False)))
cf.apply("opposite charge", ak.to_numpy(cf.events.lep_charge[:, 0] * cf.events.lep_charge[:, 1] < 0))
cf.apply("medium ID + loose isolation", ak.to_numpy(ak.all(cf.events.lep_isMediumID, axis=1)
                                                    & ak.all(cf.events.lep_isLooseIso, axis=1)))
cf.apply("pT > 25 GeV", ak.to_numpy(ak.all(cf.events.lep_pt > 25, axis=1)))
cf.apply("trigger fired and matched", ak.to_numpy(cf.events.trigM & ak.any(cf.events.lep_isTrigMatched, axis=1)))
display(Markdown(cf.table()))

mask = select(data)
assert mask.sum() == len(cf.events)
m_data = sol.dimuon_mass(data[mask])
lo, hi = sol.WINDOW
n_data = int(((m_data > lo) & (m_data < hi)).sum())
print(f"{mask.sum()} selected events, {n_data} in {lo:g} < m < {hi:g} GeV")
```

**Read it.** Your selection agrees event by event with the step-by-step cutflow. That kind of
redundancy is cheap, and it catches a lot of bugs.

## 2. Fit the peak

The observed line shape is a Breit–Wigner of width Γ_Z, smeared by the detector's momentum
resolution. A Gaussian-smeared Breit–Wigner is a Voigt profile. The fit fixes Γ_Z to the
measured value and fits the mass, the resolution and a linear background. It maximises a
binned Poisson likelihood, which you write.

```{code-cell} ipython3
def my_binned_poisson_nll(observed, expected):
    # your code here: -ln L summed over bins (constants may be dropped)
    raise NotImplementedError


check_2(my_binned_poisson_nll)
nll = check_2.use(my_binned_poisson_nll)

fit = sol.fit_peak(m_data, nll, gamma=float(sol.GAMMA_Z))
m_fit, dm_fit = fit["mass"]
s_fit, ds_fit = fit["sigma"]
assert fit["valid"]
print(f"fitted mass       {m_fit:.3f} ± {dm_fit:.3f} GeV (stat)")
print(f"fitted resolution {s_fit:.3f} ± {ds_fit:.3f} GeV")
print(f"measured m_Z      {sol.M_Z.value} ± {sol.M_Z.unc} GeV  [{sol.M_Z.source}]")
```

> **Before running the next cell.** The fitted mass and the measured one differ by about
> 0.5 GeV, which is 25 times the statistical error. Is the detector miscalibrated by 0.6%? Or
> is something else going on? What one test would tell the two apart?

```{code-cell} ipython3
m_mc, w_mc = sol.selected_masses_and_weights(mc, prov, 1.0, signed=True)
fit_mc = sol.fit_peak(m_mc, nll, gamma=float(sol.GAMMA_Z))
shift_data = m_fit - sol.M_Z.value
shift_mc = fit_mc["mass"][0] - sol.M_Z.value
display(Markdown(
    "| | fitted mass − m_Z [GeV] | resolution [GeV] |\n|---|---|---|\n"
    f"| data | {shift_data:+.3f} ± {dm_fit:.3f} | {s_fit:.2f} |\n"
    f"| MC (generated with m_Z ≈ 91.19) | {shift_mc:+.3f} ± {fit_mc['mass'][1]:.3f} | {fit_mc['sigma'][0]:.2f} |"))
assert abs(shift_data) > 10 * dm_fit            # the offset is real, not a fluctuation...
assert abs(shift_data - shift_mc) < 0.2         # ...and the simulation shows it too
```

**Read it.** The simulation was generated with the right Z mass. The same fit on it comes out
low by nearly the same amount *(computed)*. So the offset belongs to the **fit model**, not
the detector. A symmetric Voigt has no radiative tail: muons that radiate photons (final-state
radiation) pull events to lower mass, and the symmetric shape absorbs that pull by moving its
centre down. What can be compared is **data against simulation, analysed the same way**: they
agree to about 0.1 GeV *(computed)*. The fitted resolutions differ by roughly 10%, data
narrower than MC. That would matter for a resonance search, and T10 comes back to it.

## 3. Count Z bosons: data against simulation

The prediction is $\sum_i w_i$ over the selected MC events in the window, with weights
normalised by `hepanalysis.weights.mc_weight`. Every input is explicit, and so is the
luminosity of 2015 period D. **The release record quotes no per-period luminosity.** There
are two candidates:

- the value written in the official outreach notebook, a secondary source:

```{code-cell} ipython3
print(sol.LUMI_PERIOD_D.value, sol.LUMI_PERIOD_D.unit, "--", sol.LUMI_PERIOD_D.source)
```

- an estimate you compute. Take the 2015 integrated luminosity (cited) and multiply it by
  period D's share of the 2015 events in this skim (computed from the files):

```{code-cell} ipython3
def my_lumi_from_event_fraction(lumi_year, n_period, n_year):
    # your code here
    raise NotImplementedError


check_3(my_lumi_from_event_fraction)
lumi_fraction = check_3.use(my_lumi_from_event_fraction)

n15 = prov["data15_entries_per_period"]
L_est = Computed(lumi_fraction(sol.LUMI_2015, n15["periodD"], sum(n15.values())), "fb^-1",
                 "2015 luminosity x period-D share of 2015 skim events",
                 {"lumi_2015": sol.LUMI_2015.source, "entries": n15})
print(f"L(period D) estimate: {L_est.value:.4f} fb^-1   (2015 total {sol.LUMI_2015.value} fb^-1, cited)")
```

> **Before running the next cell.** The two candidates differ by a factor of two. Before you
> look at the data, which one would you bet on, and why?

```{code-cell} ipython3
rows = ["| luminosity used | MC prediction | data | data / MC |", "|---|---|---|---|"]
for label, L in [("outreach notebook (cited, secondary)", sol.LUMI_PERIOD_D), ("event-fraction estimate (computed)", L_est)]:
    pred = sol.mc_yield_in_window(mc, prov, L, signed=True)
    rows.append(f"| {label}: {float(L):.4f} fb⁻¹ | {pred:.0f} | {n_data} | {n_data / pred:.3f} |")
display(Markdown("\n".join(rows)))

pred_per_fb = sol.mc_yield_in_window(mc, prov, 1.0, signed=True)
L_z = n_data / pred_per_fb
print(f"Z counting: L = N_data / (MC prediction per fb^-1) = {L_z:.4f} fb^-1")
assert abs(L_z / L_est.value - 1) < 0.05
assert abs(L_z / float(sol.LUMI_PERIOD_D) - 1) > 0.3
```

**Read it.** Two independent routes agree to a few per cent *(computed)*:
- the event-fraction estimate, which assumes nothing about Z physics;
- Z counting, which assumes the simulation's cross section and efficiencies.

Both disagree with the value in the outreach notebook by a factor of about two. Neither route
is a luminosity measurement. The first assumes equal skim rates in every period, and the
second is only as good as the Sherpa normalisation. Their agreement is still strong evidence
that 0.105 fb⁻¹ is not the luminosity of *this* file. That is how a wrong input gets caught:
by cross-checking it, not by trusting the source. Remember the paper anchor, where luminosity
was the largest single uncertainty.

```{code-cell} ipython3
bins = np.arange(lo, hi + 1, 1.0)
h_data, _ = np.histogram(m_data, bins=bins)
h_mc, _ = np.histogram(m_mc, bins=bins, weights=w_mc * L_est.value)
fig, (ax, rax) = data_mc(bins, h_data, {r"$Z\to\mu\mu$ (Sherpa)": h_mc}, r"$m_{\mu\mu}$ [GeV]")
ax.set_title(f"2015 period D, L ≈ {L_est.value:.3f} fb⁻¹ (estimate)")
rax.set_ylim(0.5, 1.5)
plt.show()
```

```{admonition} Would you trust this?
:class: warning
- The MC was read from the first 60 000 entries of each sample. Reading other parts of the
  files changes the prediction per entry by about 3% (checked while preparing this tutorial).
  That is a statistical-sampling uncertainty you should quote.
- No background is included. Top pairs and dibosons also give opposite-sign muon pairs. Inside
  66–116 GeV they are a small correction, but how small? T04 answers that.
- The resolution differs between data and MC. Any cut on a narrow mass window inherits that
  difference as a systematic uncertainty.
```

## 4. Find the flaw

Some outreach code normalises Monte Carlo with
`w = lumi * 1000 / sum_of_weights * abs(xsec * filteff * kfac * mcWeight * SFs)`. Compare the
two predictions:

```{code-cell} ipython3
signed = sol.mc_yield_in_window(mc, prov, L_est, signed=True)
absval = sol.mc_yield_in_window(mc, prov, L_est, signed=False)
print(f"signed weights: {signed:.0f}    abs() weights: {absval:.0f}    ratio {absval / signed:.3f}")
neg = float(np.mean(ak.to_numpy(mc.mcWeight) < 0))
print(f"fraction of MC events with negative mcWeight: {neg:.1%}")

for key, text in flaw.options.items():
    print(f"  {key}) {text}")
my_flaw_answer = None   # your answer: "a", "b", "c" or "d"
flaw(my_flaw_answer)
```

## 5. Explore

In a live kernel, change the mass window and the pT threshold and watch data/MC move. The
static documentation shows one setting.

```{code-cell} ipython3
def ratio_for(window_lo=66.0, window_hi=116.0, min_pt=25.0):
    def yields(ev, w=None):
        sel = sol.select_dimuons(ev) & ak.to_numpy(ak.all(ev.lep_pt > min_pt, axis=1))
        m = sol.dimuon_mass(ev[sel])
        inside = (m > window_lo) & (m < window_hi)
        return inside.sum() if w is None else w[sel][inside].sum()
    n = yields(data)
    pred = 0.0
    for did, info in prov["samples"].items():
        if did == "data15_periodD":
            continue
        ev = mc[mc.did == int(did)]
        from hepanalysis.weights import mc_weight
        w = mc_weight(ev, L_est, sol.WEIGHT_FACTORS, True, info["metadata"]["sumOfWeights"], info["fraction_read"])
        pred += yields(ev, w)
    print(f"window [{window_lo:g}, {window_hi:g}] GeV, pT > {min_pt:g}: data {n}, MC {pred:.0f}, data/MC {n / pred:.3f}")

import ipywidgets as w
from hepanalysis.notebook import explore

explore(ratio_for, static=dict(),
        window_lo=w.FloatSlider(value=66, min=40, max=90),
        window_hi=w.FloatSlider(value=116, min=92, max=200),
        min_pt=w.FloatSlider(value=25, min=25, max=50))
```

## Recap

- A Z → μμ selection on one 2015 run period gives about 32 000 candidates in 66–116 GeV
  *(computed)*.
- A symmetric line-shape fit lands 0.5 GeV below m_Z on data **and** on simulation
  *(computed)*: the offset comes from the model. Compare data with MC analysed the same way,
  not a fit with a PDG value.
- The luminosity of the period is not in the release record. The secondary-source value
  disagrees by a factor of about two with two independent estimates that agree with each
  other *(computed)*. Cross-check every normalisation input you did not measure yourself.
- Negative generator weights must keep their sign. abs() inflates this NLO prediction by about
  20% *(computed)*.

**Judgment exercises (no solutions).**
1. The Z sample comes in three flavour slices (b-filter, c-filter, light). What would a
   prediction built from the largest slice alone get wrong, and by how much?
2. You read a pheno paper whose Drell–Yan background is "normalised to data in the Z peak".
   Which of the issues above does that fix, and which does it hide?
