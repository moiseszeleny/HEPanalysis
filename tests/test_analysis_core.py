import awkward as ak
import numpy as np
import pytest

from hepanalysis import checkpoints as cp
from hepanalysis.cutflow import Cutflow
from hepanalysis.objects import delta_phi, delta_r, invariant_mass
from hepanalysis.provenance import TodoVerify
from hepanalysis.weights import mc_weight


def test_invariant_mass_of_back_to_back_massless_pair():
    # two massless particles, pT = 45 GeV each, back to back at eta = 0: m = 90 GeV
    pt = ak.Array([[45.0, 45.0]])
    m = invariant_mass(pt, ak.Array([[0.0, 0.0]]), ak.Array([[0.0, np.pi]]), pt)
    assert m[0] == pytest.approx(90.0)


def test_invariant_mass_is_computed_in_float64():
    # float32 inputs (as stored in the files) must be promoted before m^2 = E^2 - p^2 cancels
    f32 = lambda x: np.asarray(x, dtype=np.float32)  # noqa: E731
    pt, eta, phi = f32([30.0, 30.0]), f32([1.0, 1.01]), f32([0.0, 0.01])
    e = f32(pt.astype(float) * np.cosh(eta.astype(float)))
    m = invariant_mass(ak.Array([pt]), ak.Array([eta]), ak.Array([phi]), ak.Array([e]))[0]
    p = [x.astype(float) for x in (pt, eta, phi, e)]
    px, py = np.sum(p[0] * np.cos(p[2])), np.sum(p[0] * np.sin(p[2]))
    pz, en = np.sum(p[0] * np.sinh(p[1])), np.sum(p[3])
    assert m == pytest.approx(np.sqrt(en**2 - px**2 - py**2 - pz**2), rel=1e-9)


def test_delta_phi_wraps_and_delta_r():
    assert delta_phi(3.0, -3.0) == pytest.approx(6.0 - 2 * np.pi)
    assert delta_phi(np.pi, -np.pi) == pytest.approx(0.0)
    assert -np.pi < delta_phi(-np.pi, 0.0) <= np.pi
    assert delta_r(0.0, 3.0, 0.0, -3.0) == pytest.approx(2 * np.pi - 6.0)


def test_mc_weight_explicit_choices():
    ev = ak.Array({"xsec": [2.0, 2.0], "mcWeight": [1.0, -1.0]})
    w = mc_weight(ev, 10.0, ["xsec", "mcWeight"], signed=True, sum_of_weights=4.0, fraction_read=0.5)
    assert w.tolist() == pytest.approx([10000.0, -10000.0])
    wabs = mc_weight(ev, 10.0, ["xsec", "mcWeight"], signed=False, sum_of_weights=4.0, fraction_read=0.5)
    assert wabs.sum() == pytest.approx(20000.0)
    with pytest.raises(TypeError, match="TODO_VERIFY"):
        mc_weight(ev, TodoVerify("lumi"), ["xsec"], signed=True, sum_of_weights=1.0, fraction_read=1.0)
    with pytest.raises(ValueError):
        mc_weight(ev, 1.0, ["xsec"], signed=True, sum_of_weights=1.0, fraction_read=0.0)


def test_cutflow_records_counts():
    ev = ak.Array({"x": [1, 2, 3, 4]})
    cf = Cutflow(ev, weights=[1.0, 1.0, 2.0, 2.0]).apply("x>1", ev.x > 1)
    cf.apply("x>2", cf.events.x > 2)
    assert [r[1] for r in cf.rows] == [4, 3, 2] and cf.rows[-1][2] == 4.0
    assert "| x>2 | 2 | 4 |" in cf.table()
    with pytest.raises(ValueError):
        cf.apply("bad", [True])


def test_checkpoints(capsys):
    def ref(x):
        return 2 * x

    c = cp.function_matches("double", ref, [(1.0,), (np.arange(3.0),)], hints=["multiply"])
    assert c(lambda x: 2 * x)
    assert not c(lambda x: x)

    def todo(x):
        raise NotImplementedError

    assert not c(todo) and "not attempted yet" in capsys.readouterr().out
    assert c.use(todo) is ref
    assert c.hint() == "multiply"
    n = cp.numeric_tolerance("n", 91.19, rel_tol=1e-3)
    assert n(91.2) and not n(90.0) and n.use(90.0) == 91.19
    q = cp.choice("flaw", {"a": "x", "b": "y"}, "b", {"a": "no", "b": "yes"})
    assert q("B") and not q("a") and not q("z")
    with pytest.raises(ValueError):
        cp.choice("bad", {"a": "x"}, "b", {"a": "no"})
