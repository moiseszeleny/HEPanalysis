"""What this repo is waiting for upstream, pinned as strict xfails.

Each test asserts something a tutorial needs. Today it fails, for the reason given
in its ticket (``docs/upstream_gaps.md`` or ``model_requests/``). When a pin bump
fixes the gap the test XPASSes, strict mode turns that into a failure, and the
xfail marker comes off as the ticket moves to Resolved.
"""

import pytest
from feynlag_models.registry import build

from hepanalysis import models
from hepanalysis.provenance import Cited
from hepanalysis.ufo_check import check_model

#: the BSM models Track B simulates at the LHC
LHC_MODELS = ["sm_singlet_z2", "thdm_type2"]

M_H = Cited(125.20, 0.11, "GeV",
            "PDG 2024 (S. Navas et al., Phys. Rev. D 110, 030001), Higgs mass, OUR AVERAGE "
            "(pdglive S126M)", "2026-10-22")


def strict_xfail(ticket):
    return pytest.mark.xfail(strict=True, reason=f"open upstream: {ticket}")


@strict_xfail("model_requests/sm_qcd.md + model_requests/lhc_scalars.md")
@pytest.mark.parametrize("model_id", LHC_MODELS)
def test_bsm_ufo_can_build_a_proton(model_id):
    """Needs g, u, d, s, c and colour-charged (QCD) vertices: P2 of the MadGraph probe."""
    assert check_model(model_id).ready_for_pp


@strict_xfail("HG-1")
@pytest.mark.parametrize("model_id", LHC_MODELS)
def test_masses_and_widths_live_in_slha_blocks(model_id):
    """Today MadGraph writes MASS/DECAY as 'dependent, ignored' copies; FEYNLAG is what it reads."""
    r = check_model(model_id)
    assert r.masses_outside_mass_block == [] and r.widths_outside_decay_block == []


@strict_xfail("HG-1")
@pytest.mark.parametrize("model_id", LHC_MODELS)
def test_strong_coupling_is_named_aS(model_id):
    """Without aS, MadGraph inserts AS = 0.138 and compute_widths raises NameError (probe P3, P4)."""
    r = check_model(model_id)
    assert r.has_aS and r.has_G


@strict_xfail("model_requests/lhc_scalars.md")
@pytest.mark.parametrize("model_id", LHC_MODELS)
def test_no_placeholder_widths(model_id):
    assert check_model(model_id).placeholder_widths == []


@strict_xfail("model_requests/lhc_scalars.md")
def test_singlet_benchmark_light_higgs_at_the_measured_mass():
    """At the shipped benchmark m_h1 = 120.44 GeV (feynlag-models sm_singlet_z2 README, spectrum.md)."""
    m_h1 = float(build("sm_singlet_z2").values()["MH1"])
    assert abs(m_h1 - M_H.value) < 3 * M_H.unc


@strict_xfail("FG-3 (feynlag-models/FEYNLAG_GAPS.md) + model_requests/seesaw_lhc.md")
def test_heavy_neutrino_model_ships_a_ufo():
    assert models.ufo_path("seesaw_type1") is not None
