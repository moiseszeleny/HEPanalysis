"""Monte Carlo event weights.

    w_i = L[fb^-1] * 1000 * prod(factors_i) / sum_of_weights / fraction_read

Every input is an explicit argument, because each is a decision a reader must be able
to see: which correction factors enter, whether negative generator weights keep their
sign, and which fraction of the sample was actually read.
"""

from __future__ import annotations

import awkward as ak
import numpy as np


def mc_weight(events, lumi_fb, factors, signed, sum_of_weights, fraction_read):
    """Per-event weights normalising an MC sample to ``lumi_fb``.

    events
        awkward array with every branch named in ``factors``.
    lumi_fb
        integrated luminosity in fb^-1 (a float, ``Cited`` or ``Computed``; a
        ``TodoVerify`` refuses to be used).
    factors
        branch names multiplied together, e.g. ``["xsec", "filteff", "kfac",
        "mcWeight", "ScaleFactor_PILEUP", "ScaleFactor_MUON"]``. ``xsec`` is in pb.
    signed
        ``True`` keeps the sign of each factor (correct for generators with negative
        weights); ``False`` takes ``abs()`` of each, as some outreach examples do.
    sum_of_weights
        the generator-level sum of ``mcWeight`` for the whole sample, before any skim.
    fraction_read
        entries read / entries in the file; a partial read is scaled up by its inverse.
    """
    if not 0 < fraction_read <= 1:
        raise ValueError("fraction_read must be in (0, 1]")
    w = np.full(len(events), float(lumi_fb) * 1000.0 / float(sum_of_weights) / fraction_read)
    for name in factors:
        f = ak.to_numpy(events[name]).astype(float)
        w = w * (f if signed else np.abs(f))
    return w
