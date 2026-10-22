"""Reference solutions for T00 (anatomy of a search)."""

import numpy as np


def n_expected(sigma_pb, lumi_fb, efficiency):
    """Expected events: sigma [pb] x 1000 [fb/pb] x L [fb^-1] x efficiency."""
    return sigma_pb * 1000.0 * lumi_fb * efficiency


def z_naive(s, b):
    return s / np.sqrt(b)


def z_asimov(s, b):
    """Median discovery significance for a counting experiment with known background
    (Cowan, Cranmer, Gross, Vitells, Eur. Phys. J. C 71, 1554 (2011), arXiv:1007.1727)."""
    s, b = np.asarray(s, dtype=float), np.asarray(b, dtype=float)
    return np.sqrt(2.0 * ((s + b) * np.log1p(s / b) - s))
