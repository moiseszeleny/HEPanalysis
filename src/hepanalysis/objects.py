"""Kinematics of reconstructed objects.

Tutorial T01 derives each of these by hand first; the functions here are the
library versions the later tutorials call. Inputs are in GeV (see docs/conventions.md).
"""

from __future__ import annotations

import awkward as ak
import numpy as np
import vector

vector.register_awkward()


def _f64(x):
    return ak.values_astype(x, "float64") if isinstance(x, ak.Array) else np.asarray(x, dtype=np.float64)


def four_vectors(pt, eta, phi, e):
    """Awkward/numpy momentum four-vectors from (pT, eta, phi, E), in float64.

    Files often store float32. m^2 = E^2 - p^2 cancels catastrophically for light, boosted
    systems, and in float32 a 0.3 GeV dimuon can come out at 0.43 GeV (T01 shows this).
    """
    return vector.zip({"pt": _f64(pt), "eta": _f64(eta), "phi": _f64(phi), "energy": _f64(e)})


def invariant_mass(pt, eta, phi, e, axis=-1):
    """Invariant mass of the sum of the objects along ``axis`` (e.g. the leptons of an event)."""
    p4 = four_vectors(pt, eta, phi, e)
    total = ak.sum(p4, axis=axis) if isinstance(p4, ak.Array) else p4
    return total.mass


def delta_phi(phi1, phi2):
    """phi1 - phi2 wrapped into (-pi, pi]."""
    d = np.mod(np.asarray(phi1) - np.asarray(phi2) + np.pi, 2 * np.pi) - np.pi
    return np.where(d == -np.pi, np.pi, d)


def delta_r(eta1, phi1, eta2, phi2):
    return np.hypot(np.asarray(eta1) - np.asarray(eta2), delta_phi(phi1, phi2))
