"""Is this UFO ready for a hadron collider?

A static report on a UFO directory: it parses ``particles.py``, ``parameters.py`` and
``vertices.py`` with ``ast`` and never imports or executes them. It answers the
questions a theorist should ask before handing a model file to MadGraph:

* Can MadGraph build a proton from it (gluon and light quarks present)?
* Are the QCD vertices there (colour-charged vertices, not only ``Identity`` flow)?
* Which charged leptons exist (a Drell-Yan Z' search needs e and mu)?
* Are masses and widths in the SLHA ``MASS`` / ``DECAY`` blocks? MadGraph's
  ``Auto`` widths read the ``DECAY`` block, and Pythia reads both from the SLHA
  header of the event file.
* Is the strong coupling called ``aS`` (with ``G``)? MadGraph runs alpha_s only
  through a parameter of that name.
* Which widths does the model itself mark as guessed placeholders?

The MadGraph behaviour behind these questions is checked by running MadGraph,
not here: see ``scripts/probe_mg5.py`` and ``docs/evidence/``.

    python -m hepanalysis.ufo_check thdm_type2            # a feynlag-models id
    python -m hepanalysis.ufo_check path/to/SOME_UFO [--json]
"""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

#: MadGraph's default 4-flavour proton: ``p = g u c d s u~ c~ d~ s~``
PROTON_4F = {21: "g", 1: "d", 2: "u", 3: "s", 4: "c"}
CHARGED_LEPTONS = {11: "e", 13: "mu", 15: "ta"}
_COLOURED = ("T(", "f(", "d(")


def _literal(node):
    """A keyword value as Python data: literals, ``Param.X`` -> ``'X'``, ``P.x`` -> ``'x'``."""
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_literal(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        return {ast.unparse(k): ast.unparse(v) for k, v in zip(node.keys, node.values)}
    try:
        return ast.literal_eval(node)
    except ValueError:
        return ast.unparse(node)


def _calls(path, func):
    """Keyword arguments of every top-level ``X = func(...)`` in a UFO file."""
    tree = ast.parse(Path(path).read_text())
    out = []
    for stmt in tree.body:
        if not (isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call)):
            continue
        call = stmt.value
        if isinstance(call.func, ast.Name) and call.func.id == func:
            out.append({kw.arg: _literal(kw.value) for kw in call.keywords})
    return out


@dataclass
class UFOReport:
    path: str
    particles: dict = field(default_factory=dict)      # pdg -> name
    missing_proton_partons: list = field(default_factory=list)
    has_gluon: bool = False
    n_vertices: int = 0
    n_qcd_vertices: int = 0
    charged_leptons: list = field(default_factory=list)
    lha_blocks: list = field(default_factory=list)
    masses_outside_mass_block: list = field(default_factory=list)
    widths_outside_decay_block: list = field(default_factory=list)
    has_aS: bool = False
    has_G: bool = False
    placeholder_widths: list = field(default_factory=list)
    issues: list = field(default_factory=list)

    @property
    def ready_for_pp(self):
        return not self.missing_proton_partons and self.n_qcd_vertices > 0

    def to_text(self):
        def names(pdgs):
            return ", ".join(f"{p} ({n})" for p, n in pdgs) or "none"
        lines = [
            f"UFO: {self.path}",
            f"  particles (PDG): {', '.join(f'{p}:{n}' for p, n in sorted(self.particles.items()))}",
            f"  proton (4F) partons missing: {names(self.missing_proton_partons)}",
            f"  gluon: {'yes' if self.has_gluon else 'no'}; "
            f"QCD (colour-charged) vertices: {self.n_qcd_vertices} of {self.n_vertices}",
            f"  charged leptons: {', '.join(self.charged_leptons) or 'none'}",
            f"  LHA blocks of external parameters: {', '.join(self.lha_blocks)}",
            f"  masses not in MASS block: {', '.join(self.masses_outside_mass_block) or 'none'}",
            f"  widths not in DECAY block: {', '.join(self.widths_outside_decay_block) or 'none'}",
            f"  parameter aS: {'yes' if self.has_aS else 'no'}; parameter G: {'yes' if self.has_G else 'no'}",
            f"  placeholder widths (model metadata): {', '.join(self.placeholder_widths) or 'none'}",
            f"  ready for pp collisions: {'yes' if self.ready_for_pp else 'NO'}",
        ]
        if self.issues:
            lines.append("  issues:")
            lines += [f"    - {i}" for i in self.issues]
        return "\n".join(lines)


def check(ufo_dir, placeholders=()):
    """Build a ``UFOReport`` for ``ufo_dir``.

    ``placeholders`` are parameter names the model's metadata marks as guessed
    (``feynlag-models`` ``benchmark.placeholders``); a UFO alone cannot know them.
    """
    ufo_dir = Path(ufo_dir)
    particles = _calls(ufo_dir / "particles.py", "Particle")
    params = {p["name"]: p for p in _calls(ufo_dir / "parameters.py", "Parameter")}
    vertices = _calls(ufo_dir / "vertices.py", "Vertex")

    r = UFOReport(path=str(ufo_dir))
    r.particles = {abs(int(p["pdg_code"])): p["name"] for p in particles}
    r.missing_proton_partons = [(pdg, n) for pdg, n in PROTON_4F.items() if pdg not in r.particles]
    r.has_gluon = 21 in r.particles
    r.n_vertices = len(vertices)
    r.n_qcd_vertices = sum(any(t in c for c in v.get("color", []) for t in _COLOURED) for v in vertices)
    r.charged_leptons = [n for pdg, n in CHARGED_LEPTONS.items() if pdg in r.particles]

    external = {n: p for n, p in params.items() if p.get("nature") == "external"}
    r.lha_blocks = sorted({p.get("lhablock", "?") for p in external.values()})
    for p in particles:
        for attr, block, bucket in (("mass", "MASS", r.masses_outside_mass_block),
                                    ("width", "DECAY", r.widths_outside_decay_block)):
            name = p.get(attr, "ZERO")
            if name == "ZERO" or name in bucket:
                continue
            par = params.get(name, {})
            if par.get("nature") == "external" and par.get("lhablock") != block:
                bucket.append(f"{name} ({par.get('lhablock')})")
    r.has_aS = "aS" in params
    r.has_G = "G" in params
    widths = {p.get("width") for p in particles}
    r.placeholder_widths = [n for n in placeholders if n in widths]

    if r.missing_proton_partons:
        r.issues.append("MadGraph cannot build its default proton: missing "
                        + ", ".join(n for _, n in r.missing_proton_partons))
    if r.n_qcd_vertices == 0:
        r.issues.append("no colour-charged vertex: no gluon couplings, so no QCD in the hard process")
    if r.masses_outside_mass_block or r.widths_outside_decay_block:
        r.issues.append("masses/widths are not in the SLHA MASS/DECAY blocks "
                        "(MadGraph 'Auto' widths and Pythia's SLHA reading rely on them)")
    if not r.has_aS:
        r.issues.append("no parameter named aS: MadGraph's running of alpha_s is tied to that name")
    if r.placeholder_widths:
        r.issues.append("widths marked as guessed placeholders: " + ", ".join(r.placeholder_widths))
    return r


def check_model(model_id):
    """``check`` on a feynlag-models model's committed UFO, with its placeholders."""
    from . import models
    path = models.ufo_path(model_id)
    if path is None:
        raise ValueError(f"{model_id} ships no UFO")
    return check(path, placeholders=models.placeholders(model_id))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    targets = [a for a in argv if a != "--json"]
    if not targets:
        print(__doc__)
        return 2
    for t in targets:
        r = check(t) if Path(t).is_dir() else check_model(t)
        if as_json:
            print(json.dumps(asdict(r) | {"ready_for_pp": r.ready_for_pp}, indent=2))
        else:
            print(r.to_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
