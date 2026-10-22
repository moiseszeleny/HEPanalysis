import pytest

from hepanalysis import models, ufo_check


def test_hadron_ready_ufo_passes_every_question(hadron_ready_ufo):
    r = ufo_check.check(hadron_ready_ufo)
    assert r.ready_for_pp
    assert r.has_gluon and r.n_qcd_vertices == 1 and r.n_vertices == 2
    assert r.charged_leptons == ["e", "mu"]
    assert r.lha_blocks == ["DECAY", "MASS", "SMINPUTS"]
    assert r.masses_outside_mass_block == [] and r.widths_outside_decay_block == []
    assert r.has_aS and r.has_G
    assert r.issues == []


def test_pilot_layout_is_flagged(lepton_only_ufo):
    r = ufo_check.check(lepton_only_ufo, placeholders=["WH2", "not_a_width"])
    assert not r.ready_for_pp
    assert [n for _, n in r.missing_proton_partons] == ["g", "d", "u", "s", "c"]
    assert r.n_qcd_vertices == 0   # Identity colour flow is a colour singlet
    assert r.charged_leptons == ["ta"]
    assert r.lha_blocks == ["FEYNLAG"]
    # MH2 is internal (derived), so only external masses can be misplaced
    assert r.masses_outside_mass_block == ["MT (FEYNLAG)", "MTA (FEYNLAG)"]
    assert r.widths_outside_decay_block == ["WT (FEYNLAG)", "WH2 (FEYNLAG)"]
    assert not r.has_aS
    assert r.placeholder_widths == ["WH2"]
    assert len(r.issues) == 5


def test_report_text_and_cli(hadron_ready_ufo, capsys):
    assert ufo_check.main([str(hadron_ready_ufo)]) == 0
    assert "ready for pp collisions: yes" in capsys.readouterr().out


@pytest.mark.parametrize("model_id", ["sm", "sm_ckm", "sm_singlet_z2", "thdm_type2"])
def test_parses_every_feynlag_models_ufo(model_id):
    """The parser reads the real files (the particle list matches the UFO's own count)."""
    r = ufo_check.check_model(model_id)
    text = (models.ufo_path(model_id) / "particles.py").read_text()
    assert len(r.particles) == text.count("= Particle(")
    assert r.n_vertices == (models.ufo_path(model_id) / "vertices.py").read_text().count("= Vertex(")
