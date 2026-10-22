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

# T00 · Anatomy of a search

A search for new physics turns a Lagrangian into a statement about data: *this model, with
these parameters, is excluded* (or, rarely, *something is there*). Between the two sit about
eight stages. Each one is run by a different tool and owned by a different group of people,
and each one can quietly go wrong. This tutorial maps those stages before any of them is
done in earnest. It also asks two questions that matter to a theorist: which stages can you
redo yourself from public information, and which can you only trust?

**Paper anchor.** K. Cranmer, S. Kraml, H. B. Prosper (eds.), *Publishing statistical models:
Getting the most out of particle physics experiments*, SciPost Phys. 12, 037 (2022),
arXiv:2109.04981 *(cited)*. It is a community document on exactly this question: what
experiments should publish so that people outside them can reuse a search.

**How to use these tutorials.** Each step has an exercise cell with
`raise NotImplementedError`. Replace it with your code and run the check cell under it. A
wrong answer prints a nudge, and `check_k.hint()` reveals staged hints. If you skip a step,
`check_k.use(...)` hands the reference solution to the cells below, so the notebook still
runs end to end. The reference solutions live in `t00_solutions.py`; look only after you
have tried.

```{code-cell} ipython3
import numpy as np
from IPython.display import Markdown, display

from t00_checks import check_1, check_2, flaw
```

## 1. The chain, stage by stage

| stage | tool (in this course) | what it produces | a typical way to go wrong | can a theorist redo it? |
|---|---|---|---|---|
| model | feynlag / feynlag-models | Lagrangian, Feynman rules, UFO | a wrong sign or a missing vertex; placeholder widths | yes, it is yours |
| hard process | MadGraph | parton-level events, σ | wrong PDF or scale choice; LO used where NLO matters | yes |
| shower + hadronisation | Pythia8 | particle-level events | a mismatched merging scale; double counting | yes |
| detector | real detector, or Delphes | reconstructed objects | fast simulation misses fakes, pile-up, long-lived particles | only approximately |
| selection | the analysis | events in signal and control regions | cuts tuned on the data you then test | if the cuts are public |
| background estimate | MC + data-driven | expected yields with uncertainties | a mismodelled tail; a closure test never done | rarely; you reuse theirs |
| statistical model | pyhf / likelihood | the likelihood of the data given μ | missing correlated uncertainties | **only if the likelihood is published** |
| result | CLs / p-values | a limit or a significance | local significance quoted as global | yes, from the likelihood |

The last column is the theme of the whole course. Upstream of the detector you control
everything. Downstream of it, you depend on what the experiment published.

## 2. From a cross section to a number of events

The first number in any search is how many signal events to expect:
$N = \sigma \times L \times \varepsilon$. Cross sections come from MadGraph in **pb**,
luminosities are quoted in **fb⁻¹**, and ε is the fraction of signal events that survive the
selection.

> **Before running the next cell.** A signal has σ = 50 fb and the selection efficiency is
> 30%. Roughly how many events does it give in the 36 fb⁻¹ of the ATLAS 2015–16 data? Write
> the function, then check your estimate against it.

```{code-cell} ipython3
def my_n_expected(sigma_pb, lumi_fb, efficiency):
    # your code here
    raise NotImplementedError


check_1(my_n_expected)
n_expected = check_1.use(my_n_expected)
print(f"sigma = 50 fb, L = 36 fb^-1, eff = 0.3  ->  N = {n_expected(0.05, 36.0, 0.3):.0f} events")
```

**Read it.** About 540 events *(computed)*. That is plenty if the background is small, and
hopeless if it is a million.

## 3. How significant is an excess?

The textbook estimate of the significance of s signal events over b background events is
$Z = s/\sqrt{b}$. It is the large-b limit of a better formula: the median significance
of a counting experiment with known background, evaluated on the "Asimov" data set n = s + b
(Cowan, Cranmer, Gross, Vitells, Eur. Phys. J. C 71, 1554 (2011), arXiv:1007.1727,
*cited*):

$$Z_A = \sqrt{2\left[(s+b)\ln\left(1 + \frac{s}{b}\right) - s\right]} .$$

> **Before running the next cell.** Expand $Z_A$ for $s \ll b$. Do you get $s/\sqrt{b}$
> back? In which direction does $s/\sqrt{b}$ go wrong when b is small: does it overstate or
> understate the significance?

```{code-cell} ipython3
def my_z_asimov(s, b):
    # your code here
    raise NotImplementedError


check_2(my_z_asimov)
z_asimov = check_2.use(my_z_asimov)

rows = ["| s | b | s/√b | Z_A |", "|---|---|---|---|"]
for s, b in [(10, 100), (10, 10), (3, 1), (3, 0.36)]:
    rows.append(f"| {s} | {b} | {s/np.sqrt(b):.2f} | {z_asimov(s, b):.2f} |")
display(Markdown("\n".join(rows)))
assert z_asimov(10, 100) / (10 / np.sqrt(100)) > 0.97          # large b: they agree
assert z_asimov(3, 0.36) < 0.65 * (3 / np.sqrt(0.36))          # small b: s/√b overstates
```

**Read it.** The two agree to within a few per cent when b is large. When b is below one
event, $s/\sqrt b$ overstates the significance by more than half *(computed)*. Searches for
heavy new states are exactly where backgrounds are tiny, so this is the regime that matters.

```{admonition} Would you trust this?
:class: warning
Both formulas assume the background is **known exactly**. A real background estimate carries
an uncertainty, and with a 20% uncertainty on b, a "5σ" counting excess can shrink a lot.
T05 adds that uncertainty as a nuisance parameter. Until then, treat any Z built from s and b
alone as an upper bound on the real significance.
```

## 4. Find the flaw

A proceedings contribution claims: *"After all cuts we expect b = 0.36 background events and
observe 3 more than expected, a significance of s/√b = 3/0.6 = 5.0σ: a discovery."*

```{code-cell} ipython3
for key, text in flaw.options.items():
    print(f"  {key}) {text}")

my_flaw_answer = None   # your answer: "a", "b", "c" or "d"
flaw(my_flaw_answer)
```

## 5. Explore

In a live kernel, the sliders show how $s/\sqrt b$ and $Z_A$ separate as the background
shrinks. In the static documentation only the fixed plot below is shown.

```{code-cell} ipython3
import matplotlib.pyplot as plt

def plot_significance(s=3.0):
    b = np.logspace(-2, 3, 200)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.loglog(b, s / np.sqrt(b), label=r"$s/\sqrt{b}$")
    ax.loglog(b, z_asimov(s, b), label=r"$Z_A$")
    ax.axhline(5, color="grey", ls=":", lw=1)
    ax.set_xlabel("background b"); ax.set_ylabel("significance Z"); ax.legend()
    ax.set_title(f"s = {s:g}")
    plt.show()

import ipywidgets as w
from hepanalysis.notebook import explore

explore(plot_significance, static=dict(s=3.0),
        s=w.FloatLogSlider(value=3, base=10, min=-1, max=2, step=0.05))
```

## Recap

- A search is a chain of about eight stages. A theorist controls everything up to the
  detector, and after it can only reuse what the experiments publish (*cited*: Cranmer,
  Kraml, Prosper 2022).
- $N = \sigma[\text{pb}] \times 1000 \times L[\text{fb}^{-1}] \times \varepsilon$.
- $s/\sqrt b$ is a large-background approximation. Near zero background it overstates the
  significance, and $Z_A$ should be used instead (*computed*).

**Judgment exercises (no solutions).**
1. Pick a BSM search you have cited recently. For each stage in the table, say whether its
   output is public: is the likelihood on HEPData? Are the cutflows?
2. Two analyses quote the same expected limit, one with b ≈ 0.1 and one with b ≈ 100. Which
   one's limit moves more if the background uncertainty doubles? Why?
