"""Reference solutions for T02 (rediscover the Z)."""

import json
from pathlib import Path

import awkward as ak
import numpy as np
from iminuit import Minuit
from scipy.special import voigt_profile

from hepanalysis.objects import invariant_mass
from hepanalysis.provenance import Cited
from hepanalysis.weights import mc_weight

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

M_Z = Cited(91.1879, 0.0020, "GeV", "PDG live, 2026 edition, Z boson summary (pdglive node S044)",
            "2026-10-22")
GAMMA_Z = Cited(2.4955, 0.0023, "GeV", "PDG live, 2026 edition, Z boson summary (pdglive node S044)",
                "2026-10-22")
#: integrated luminosity of 2015 period D, as stated in the official outreach notebook.
#: A secondary source (the release record itself quotes no luminosity): treat with care.
LUMI_PERIOD_D = Cited(0.105, None, "fb^-1",
                      "ATLAS outreach notebook 13-TeV-examples/uproot_python/HZZAnalysis.ipynb "
                      "(release 2025e-13tev-beta), cell 'Luminosity of periodD in data 15'",
                      "2026-10-22")
LUMI_2015 = Cited(3.24, 0.04, "fb^-1",
                  "ATLAS Collaboration, Eur. Phys. J. C 83, 982 (2023), arXiv:2212.09379v2, Table 8 "
                  "(2015, after standard data-quality requirements)", "2026-10-22")
WEIGHT_FACTORS = ["xsec", "filteff", "kfac", "mcWeight",
                  "ScaleFactor_PILEUP", "ScaleFactor_MUON", "ScaleFactor_LepTRIGGER"]
WINDOW = (66.0, 116.0)


def load():
    data = ak.from_parquet(DATA_DIR / "2muons_data15_periodD.parquet")
    mc = ak.from_parquet(DATA_DIR / "zmumu_mc.parquet")
    prov = json.loads((DATA_DIR / "provenance.json").read_text())
    return data, mc, prov


def select_dimuons(ev):
    """Exactly two muons, opposite charge, medium ID, loose isolation, pT > 25 GeV,
    single-muon trigger fired and matched to at least one of them."""
    two = ev.lep_n == 2
    ev2 = ak.pad_none(ev.lep_type, 2)
    is_mu = ak.fill_none((ev2[:, 0] == 13) & (ev2[:, 1] == 13), False)
    q = ak.pad_none(ev.lep_charge, 2)
    os_ = ak.fill_none(q[:, 0] * q[:, 1] < 0, False)
    good = ak.all(ev.lep_isMediumID, axis=1) & ak.all(ev.lep_isLooseIso, axis=1)
    hard = ak.all(ev.lep_pt > 25.0, axis=1)
    trig = ev.trigM & ak.any(ev.lep_isTrigMatched, axis=1)
    return ak.to_numpy(two & is_mu & os_ & good & hard & trig)


def dimuon_mass(ev):
    return ak.to_numpy(invariant_mass(ev.lep_pt, ev.lep_eta, ev.lep_phi, ev.lep_e))


def binned_poisson_nll(observed, expected):
    """-ln L for independent Poisson bins, dropping the observed-only constant ln(n!)."""
    expected = np.asarray(expected, dtype=float)
    return float(np.sum(expected - np.asarray(observed) * np.log(expected)))


def peak_model(x, n_sig, mass, sigma, gamma, slope, n_bkg, width, lo, hi):
    """Expected counts per bin: a Breit-Wigner (width ``gamma``) smeared by a Gaussian
    resolution ``sigma`` (a Voigt profile), plus a linear background, for bin centres x."""
    sig = n_sig * width * voigt_profile(x - mass, sigma, gamma / 2.0)
    centre, half = 0.5 * (lo + hi), 0.5 * (hi - lo)
    bkg = n_bkg * width / (hi - lo) * (1.0 + slope * (x - centre) / half)
    return sig + bkg


def fit_peak(masses, nll, gamma, lo=WINDOW[0], hi=WINDOW[1], width=0.5):
    """Fit mass and resolution with Gamma fixed to ``gamma``; ``nll`` is the likelihood used."""
    edges = np.arange(lo, hi + 0.5 * width, width)
    counts, _ = np.histogram(masses, bins=edges)
    x = 0.5 * (edges[1:] + edges[:-1])

    def cost(n_sig, mass, sigma, slope, n_bkg):
        mu = peak_model(x, n_sig, mass, sigma, gamma, slope, n_bkg, width, lo, hi)
        return nll(counts, np.clip(mu, 1e-9, None))

    cost.errordef = Minuit.LIKELIHOOD
    n = counts.sum()
    m = Minuit(cost, n_sig=0.95 * n, mass=91.0, sigma=2.0, slope=0.0, n_bkg=0.05 * n)
    m.limits["sigma"] = (0.1, 10.0)
    m.limits["n_bkg"] = (0.0, None)
    m.limits["slope"] = (-1.0, 1.0)
    m.migrad()
    m.hesse()
    return {k: (m.values[k], m.errors[k]) for k in m.parameters} | {"valid": m.valid,
                                                                  "counts": counts, "x": x}


def mc_yield_in_window(mc, prov, lumi_fb, signed, factors=WEIGHT_FACTORS, window=WINDOW):
    """Expected selected Z -> mumu events in the mass window, summed over the flavour slices."""
    total = 0.0
    for did, info in prov["samples"].items():
        if did == "data15_periodD":
            continue
        ev = mc[mc.did == int(did)]
        sel = select_dimuons(ev)
        ev = ev[sel]
        m = dimuon_mass(ev)
        w = mc_weight(ev, lumi_fb, factors, signed=signed,
                      sum_of_weights=float(info["metadata"]["sumOfWeights"]),
                      fraction_read=float(info["fraction_read"]))
        inside = (m > window[0]) & (m < window[1])
        total += float(w[inside].sum())
    return total


def lumi_from_event_fraction(lumi_year, n_period, n_year):
    """Share of a year's luminosity in one period, assuming the skim's event rate per unit
    luminosity is the same in every period (same triggers, same detector conditions)."""
    return float(lumi_year) * n_period / n_year


def selected_masses_and_weights(mc, prov, lumi_fb, signed, factors=WEIGHT_FACTORS):
    """Selected MC dimuon masses and their weights, all flavour slices together."""
    ms, ws = [], []
    for did, info in prov["samples"].items():
        if did == "data15_periodD":
            continue
        ev = mc[mc.did == int(did)]
        ev = ev[select_dimuons(ev)]
        ms.append(dimuon_mass(ev))
        ws.append(mc_weight(ev, lumi_fb, factors, signed=signed,
                            sum_of_weights=float(info["metadata"]["sumOfWeights"]),
                            fraction_read=float(info["fraction_read"])))
    return np.concatenate(ms), np.concatenate(ws)
