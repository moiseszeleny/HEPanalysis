import pytest

from hepanalysis import models, provenance
from hepanalysis.provenance import Cited, Computed, TodoVerify


def test_registry_sees_the_pinned_catalogue():
    ids = models.model_ids()
    assert {"sm", "sm_singlet_z2", "thdm_type2", "seesaw_type1"} <= set(ids)
    assert models.maturity("thdm_type2") == 3


def test_ufo_path_and_copy(tmp_path):
    src = models.ufo_path("thdm_type2")
    assert (src / "particles.py").exists()
    out = models.copy_ufo("thdm_type2", tmp_path)
    assert (out / "parameters.py").read_text() == (src / "parameters.py").read_text()
    assert not (out / "__pycache__").exists()


def test_models_without_ufo_refuse_to_copy(tmp_path):
    assert models.ufo_path("seesaw_type1") is None
    with pytest.raises(ValueError, match="no UFO"):
        models.copy_ufo("seesaw_type1", tmp_path)


def test_model_module_imports_through_the_registry():
    from feynlag_models import registry
    assert hasattr(registry.load("thdm_type2"), "build")


def test_cited_needs_source_and_iso_date():
    mz = Cited(91.1880, 0.0020, "GeV", "PDG 2024, Z boson summary table", "2026-10-22")
    assert float(mz) == 91.1880 and mz.tag == "cited"
    with pytest.raises(ValueError, match="source"):
        Cited(1.0, None, "GeV", "  ", "2026-10-22")
    with pytest.raises(ValueError, match="ISO date"):
        Cited(1.0, None, "GeV", "somewhere", "October 2026")


def test_todo_verify_refuses_arithmetic():
    lumi = TodoVerify("integrated luminosity of the 2025 ATLAS open-data release")
    for op in (lambda x: x * 2.0, lambda x: 2.0 * x, lambda x: x + 1, float):
        with pytest.raises(TypeError, match="TODO_VERIFY"):
            op(lumi)


def test_computed_and_stamp():
    c = Computed(0.5, "", "toy efficiency", {"n_pass": 5, "n_all": 10})
    assert c.tag == "computed" and float(c) == 0.5
    s = provenance.stamp()
    assert s["feynlag"] == "0.3.0"
    assert s["feynlag-models_commit"] == "cb0678a5c5b64628e3a93d256051a44f245f5f22"
