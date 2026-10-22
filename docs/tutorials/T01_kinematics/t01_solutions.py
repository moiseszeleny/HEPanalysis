"""Reference solutions for T01 (kinematics and physics objects)."""

from pathlib import Path

import awkward as ak
import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data" / "2muons_data15_periodD.parquet"


def load_pairs():
    """Events with exactly two leptons from the committed period-D sample (GeV)."""
    d = ak.from_parquet(DATA)
    return d[d.lep_n == 2]


def invariant_mass_pair(pt1, eta1, phi1, e1, pt2, eta2, phi2, e2):
    """m^2 = (E1 + E2)^2 - |p1 + p2|^2, with p = (pT cos phi, pT sin phi, pT sinh eta)."""
    px = pt1 * np.cos(phi1) + pt2 * np.cos(phi2)
    py = pt1 * np.sin(phi1) + pt2 * np.sin(phi2)
    pz = pt1 * np.sinh(eta1) + pt2 * np.sinh(eta2)
    m2 = (e1 + e2) ** 2 - (px ** 2 + py ** 2 + pz ** 2)
    return np.sqrt(np.maximum(m2, 0.0))


def delta_phi(phi1, phi2):
    """phi1 - phi2 wrapped into (-pi, pi]."""
    d = np.mod(np.asarray(phi1) - np.asarray(phi2) + np.pi, 2 * np.pi) - np.pi
    return np.where(d == -np.pi, np.pi, d)


def peak_position(masses, lo, hi, width):
    """Centre of the most populated bin of width ``width`` in [lo, hi)."""
    edges = np.arange(lo, hi + 0.5 * width, width)
    counts, edges = np.histogram(masses, bins=edges)
    i = int(np.argmax(counts))
    return 0.5 * (edges[i] + edges[i + 1])


def isolated_fraction(both_isolated, masses, lo, hi):
    """Fraction of events with lo < m < hi whose two leptons both pass isolation."""
    window = (masses > lo) & (masses < hi)
    return float(np.mean(np.asarray(both_isolated)[window]))


def pair_columns(pairs):
    """(pt1, eta1, phi1, e1, pt2, eta2, phi2, e2) as numpy arrays."""
    cols = []
    for i in (0, 1):
        cols += [ak.to_numpy(pairs[f][:, i]).astype(float)
                 for f in ("lep_pt", "lep_eta", "lep_phi", "lep_e")]
    return tuple(cols)
