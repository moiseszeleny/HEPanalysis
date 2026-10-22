"""Plots used across tutorials: data over a stacked MC prediction, with a ratio panel."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np


def data_mc(bins, data, mc, xlabel, ylabel="events / bin", mc_unc=None):
    """``data``: counts per bin; ``mc``: {label: weighted counts per bin} (stacked in order).

    ``mc_unc`` (per-bin absolute uncertainty of the total prediction) is drawn as a band.
    Returns ``(fig, (ax, rax))``.
    """
    bins = np.asarray(bins, dtype=float)
    centres = 0.5 * (bins[1:] + bins[:-1])
    fig, (ax, rax) = plt.subplots(2, 1, sharex=True, figsize=(6.4, 5.6),
                                  gridspec_kw={"height_ratios": [3, 1], "hspace": 0.05})
    bottom = np.zeros(len(centres))
    for label, values in mc.items():
        ax.stairs(bottom + values, bins, baseline=bottom, fill=True, label=label, alpha=0.8)
        bottom = bottom + values
    if mc_unc is not None:
        ax.stairs(bottom + mc_unc, bins, baseline=bottom - mc_unc, fill=True, hatch="///",
                  color="none", edgecolor="grey", label="MC uncertainty")
    data = np.asarray(data, dtype=float)
    ax.errorbar(centres, data, yerr=np.sqrt(data), fmt="ko", ms=3, label="data")
    ax.set_ylabel(ylabel)
    ax.legend()
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(bottom > 0, data / bottom, np.nan)
        rerr = np.where(bottom > 0, np.sqrt(data) / bottom, np.nan)
    rax.errorbar(centres, ratio, yerr=rerr, fmt="ko", ms=3)
    rax.axhline(1.0, color="grey", lw=1)
    rax.set_ylabel("data / MC")
    rax.set_xlabel(xlabel)
    return fig, (ax, rax)
