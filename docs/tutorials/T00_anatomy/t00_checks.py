"""Checkpoints for T00. Expected values come from t00_solutions, never from literals."""

import numpy as np

from hepanalysis.checkpoints import choice, function_matches

import t00_solutions as sol

check_1 = function_matches(
    "step_1 n_expected", sol.n_expected,
    cases=[(1.0, 1.0, 1.0), (0.05, 36.0, 0.3), (np.array([1e-3, 2.0]), 140.0, 0.01)],
    hints=["Cross sections are in pb, luminosity in fb^-1: how many fb are in one pb?",
           "1 pb = 1000 fb, so N = sigma[pb] * 1000 * L[fb^-1] * efficiency."])

check_2 = function_matches(
    "step_2 z_asimov", sol.z_asimov,
    cases=[(10.0, 100.0), (3.0, 0.36), (np.array([1.0, 5.0, 50.0]), np.array([0.1, 10.0, 1e4]))],
    hints=["Start from the Poisson likelihood ratio of s+b against b alone, evaluated on the "
           "'Asimov' data set n = s + b.",
           "Z = sqrt(2 * ((s + b) * ln(1 + s/b) - s)). Use np.log1p for accuracy at small s/b."])

flaw = choice(
    "find the flaw",
    {"a": "The luminosity is in the wrong unit.",
     "b": "s/sqrt(b) is used where the background is far too small for the Gaussian approximation.",
     "c": "The signal efficiency was not applied.",
     "d": "Nothing: Z = 5 is a discovery."},
    correct="b",
    explanations={
        "a": "The yields s and b are already event counts; no luminosity enters the claim.",
        "b": "Right. s/sqrt(b) assumes b >> 1 and s << b. Here b = 0.36: the Asimov "
             "significance of the same numbers is about 3, not 5.",
        "c": "s is quoted as the expected number of selected events, so efficiency is in it.",
        "d": "Recompute the significance with z_asimov(3, 0.36) before believing the 5.",
    },
    hints=["Compare z_naive(3, 0.36) with z_asimov(3, 0.36)."])
