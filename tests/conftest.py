import textwrap

import pytest


def _write_ufo(root, particles, parameters, vertices):
    root.mkdir()
    (root / "particles.py").write_text(textwrap.dedent(particles))
    (root / "parameters.py").write_text(textwrap.dedent(parameters))
    (root / "vertices.py").write_text(textwrap.dedent(vertices))
    return root


@pytest.fixture
def hadron_ready_ufo(tmp_path):
    """A minimal UFO that passes every readiness question (positive control)."""
    quarks = "\n        ".join(
        f"{n} = Particle(pdg_code={pdg}, name='{n}', antiname='{n}~', spin=2, color=3, "
        f"mass=Param.ZERO, width=Param.ZERO, charge=0)"
        for n, pdg in (("d", 1), ("u", 2), ("s", 3), ("c", 4)))
    return _write_ufo(
        tmp_path / "GOOD_UFO",
        f"""
        g = Particle(pdg_code=21, name='g', antiname='g', spin=3, color=8, mass=Param.ZERO, width=Param.ZERO, charge=0)
        {quarks}
        e__minus__ = Particle(pdg_code=11, name='e-', antiname='e+', spin=2, color=1, mass=Param.ZERO, width=Param.ZERO, charge=-1)
        mu__minus__ = Particle(pdg_code=13, name='mu-', antiname='mu+', spin=2, color=1, mass=Param.ZERO, width=Param.ZERO, charge=-1)
        Zp = Particle(pdg_code=32, name='Zp', antiname='Zp', spin=3, color=1, mass=Param.MZp, width=Param.WZp, charge=0)
        """,
        """
        ZERO = Parameter(name='ZERO', nature='internal', type='real', value='0.0', texname='0')
        aS = Parameter(name='aS', nature='external', type='real', value=0.118, texname='a_s', lhablock='SMINPUTS', lhacode=[3])
        G = Parameter(name='G', nature='internal', type='real', value='2*cmath.sqrt(aS)*cmath.sqrt(cmath.pi)', texname='G')
        MZp = Parameter(name='MZp', nature='external', type='real', value=3000.0, texname='M', lhablock='MASS', lhacode=[32])
        WZp = Parameter(name='WZp', nature='external', type='real', value=30.0, texname='W', lhablock='DECAY', lhacode=[32])
        """,
        """
        V_1 = Vertex(name='V_1', particles=[P.u__tilde__, P.u, P.g], color=['T(3,2,1)'], lorentz=[L.FFV1], couplings={(0,0):C.GC_1})
        V_2 = Vertex(name='V_2', particles=[P.u__tilde__, P.u, P.Zp], color=['Identity(1,2)'], lorentz=[L.FFV1], couplings={(0,0):C.GC_2})
        """)


@pytest.fixture
def lepton_only_ufo(tmp_path):
    """A UFO with the feynlag-models pilot layout: one generation, one LHA block, no gluon."""
    return _write_ufo(
        tmp_path / "PILOT_UFO",
        """
        t = Particle(pdg_code=6, name='t', antiname='t~', spin=2, color=3, mass=Param.MT, width=Param.WT, charge=2/3)
        ta__minus__ = Particle(pdg_code=15, name='ta-', antiname='ta+', spin=2, color=1, mass=Param.MTA, width=Param.ZERO, charge=-1)
        h2 = Particle(pdg_code=35, name='h2', antiname='h2', spin=1, color=1, mass=Param.MH2, width=Param.WH2, charge=0)
        """,
        """
        ZERO = Parameter(name='ZERO', nature='internal', type='real', value='0.0', texname='0')
        gs = Parameter(name='gs', nature='external', type='real', value=1.2, texname='g_s', lhablock='FEYNLAG', lhacode=[1])
        MT = Parameter(name='MT', nature='external', type='real', value=173.0, texname='m_t', lhablock='FEYNLAG', lhacode=[2])
        MTA = Parameter(name='MTA', nature='external', type='real', value=1.777, texname='m', lhablock='FEYNLAG', lhacode=[3])
        WT = Parameter(name='WT', nature='external', type='real', value=1.49, texname='w', lhablock='FEYNLAG', lhacode=[4])
        WH2 = Parameter(name='WH2', nature='external', type='real', value=1.0, texname='w', lhablock='FEYNLAG', lhacode=[5])
        MH2 = Parameter(name='MH2', nature='internal', type='complex', value='400.0', texname='m')
        """,
        """
        V_1 = Vertex(name='V_1', particles=[P.t__tilde__, P.t, P.h2], color=['Identity(1,2)'], lorentz=[L.FFS1], couplings={(0,0):C.GC_1})
        """)
