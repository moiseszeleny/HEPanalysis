"""Checkpoints for T02. Expected values come from t02_solutions, never from literals."""

import numpy as np

from hepanalysis.checkpoints import choice, function_matches

import t02_solutions as sol

_data, _mc, _prov = sol.load()
_rng = np.random.default_rng(1)

check_1 = function_matches(
    "step_1 selection", sol.select_dimuons, cases=[(_data,), (_mc[:20000],)],
    hints=["Ask for: exactly two leptons, both with lep_type == 13, opposite charges.",
           "Then: both lep_isMediumID and lep_isLooseIso, both pT > 25 GeV, trigM fired, "
           "and at least one lepton with lep_isTrigMatched (ak.all / ak.any along axis=1)."])

_mu = _rng.uniform(1, 50, size=30)
check_2 = function_matches(
    "step_2 binned Poisson NLL", sol.binned_poisson_nll,
    cases=[(_rng.poisson(_mu), _mu), (np.array([0, 3, 10]), np.array([0.5, 2.0, 12.0]))],
    hints=["For one bin, P(n | mu) = mu^n e^(-mu) / n!.",
           "-ln L = sum(mu - n ln mu) + sum(ln n!); drop the last term, it does not depend on the model."])

_n = _prov["data15_entries_per_period"]
check_3 = function_matches(
    "step_3 luminosity from the event fraction", sol.lumi_from_event_fraction,
    cases=[(float(sol.LUMI_2015), _n["periodD"], sum(_n.values())), (10.0, 1, 4)],
    hints=["If every period records the same number of skimmed events per pb^-1, a period's share "
           "of the events is its share of the luminosity."])

flaw = choice(
    "find the flaw",
    {"a": "Sherpa's cross section is leading order, so a k-factor of 1 is wrong.",
     "b": "abs() of the generator weight discards the negative weights' cancellation and inflates the prediction.",
     "c": "The trigger scale factor should not be applied when the trigger is required in data.",
     "d": "Nothing is wrong."},
    correct="b",
    explanations={
        "a": "The metadata labels this Sherpa sample NLO and the release sets kfac = 1; that is a "
             "choice to document, not the error here.",
        "b": "Right. Sherpa at NLO produces negative weights that cancel part of the positive ones. "
             "Taking abs() makes every event count positively: compare the two yields above.",
        "c": "The scale factor corrects the simulated trigger efficiency to the measured one; it is "
             "exactly what makes the trigger requirement comparable between data and MC.",
        "d": "Recompute the prediction with signed=False and compare.",
    },
    hints=["Look at the sign of mcWeight in the MC sample."])
