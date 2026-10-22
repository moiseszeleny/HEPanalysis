"""Checkpoints for T01. Expected values come from t01_solutions, never from literals."""

import numpy as np

from hepanalysis.checkpoints import choice, function_matches

import t01_solutions as sol

_pairs = sol.load_pairs()
_cols = sol.pair_columns(_pairs[:200])
_masses = sol.invariant_mass_pair(*sol.pair_columns(_pairs))
_iso = np.asarray(_pairs.lep_isLooseIso[:, 0] & _pairs.lep_isLooseIso[:, 1])

check_1 = function_matches(
    "step_1 invariant mass", sol.invariant_mass_pair, cases=[_cols], rel_tol=1e-5, abs_tol=1e-4,
    hints=["Build the Cartesian momentum of each lepton first: px = pT cos(phi), "
           "py = pT sin(phi), pz = pT sinh(eta).",
           "m^2 = (E1 + E2)^2 - (px1 + px2)^2 - (py1 + py2)^2 - (pz1 + pz2)^2; "
           "clip tiny negative m^2 from rounding before the square root."])

check_2 = function_matches(
    "step_2 delta phi", sol.delta_phi,
    cases=[(3.0, -3.0), (-3.0, 3.0), (0.5, 0.2), (np.array([np.pi, -np.pi, 6.0]), np.array([-np.pi, 0.0, 0.0]))],
    hints=["phi is an angle: 3.0 and -3.0 are only 2*pi - 6 = 0.28 rad apart.",
           "Shift by pi, take the remainder modulo 2*pi, shift back: "
           "np.mod(d + pi, 2*pi) - pi (then map -pi to +pi)."])

check_3 = function_matches(
    "step_3 peak position", sol.peak_position,
    cases=[(_masses, 2.5, 3.7, 0.02), (_masses, 8.0, 11.0, 0.05), (_masses, 70.0, 110.0, 0.5)],
    hints=["np.histogram with edges np.arange(lo, hi + width/2, width), then np.argmax.",
           "Return the centre of the winning bin, not its left edge."])

check_4 = function_matches(
    "step_4 isolated fraction", sol.isolated_fraction,
    cases=[(_iso, _masses, 20.0, 60.0), (_iso, _masses, 80.0, 100.0)],
    hints=["Select the window with a boolean mask on the masses, then average the "
           "'both isolated' booleans inside it."])

flaw = choice(
    "find the flaw",
    {"a": "Muons cannot be matched with a cone of 0.4.",
     "b": "The azimuthal difference is not wrapped, so pairs on either side of phi = ±pi look far apart.",
     "c": "Pseudorapidity should be replaced by rapidity for muons.",
     "d": "Nothing is wrong."},
    correct="b",
    explanations={
        "a": "A cone of 0.4 is a common choice; the problem is how the distance is computed.",
        "b": "Right. phi1 - phi2 can be up to 2*pi; without wrapping, a muon at phi = 3.1 and "
             "a track at phi = -3.1 are 6.2 apart instead of 0.08.",
        "c": "For muons (m << pT) rapidity and pseudorapidity are practically equal.",
        "d": "Try the function on phi1 = 3.1, phi2 = -3.1.",
    },
    hints=["Evaluate naive_delta_r(0.0, 3.1, 0.0, -3.1) by hand."])
