"""MadGraph smoke test of the feynlag-models UFOs: evidence for docs/upstream_gaps.md.

``hepanalysis.ufo_check`` says what a UFO *contains*; this script records what
MadGraph *does* with it. Every probe runs MG5 on a copy of the UFO in ``runs/``
(git-ignored), never on the installed feynlag-models files.

  P1  import model; display multiparticles   -> is a proton ``p`` defined?
  P2  generate p p > X                        -> can a hadron-collider process be built?
  P3  generate X > all all; output            -> which blocks does the param card hold,
                                                 and does MadGraph insert a dummy aS?
  P4  compute_widths X on that param card     -> where does the computed width go, and
                                                 does the model's own width parameter move?

    uv run python scripts/probe_mg5.py [--mg5 PATH/bin/mg5_aMC] [--out FILE]
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
from hepanalysis import models, provenance, ufo_check  # noqa: E402

#: model id -> (particle X probed, its PDG code)
TARGETS = {
    "sm": ("z", 23),
    "sm_ckm": ("z", 23),
    "sm_singlet_z2": ("h2", 35),
    "thdm_type2": ("h2", 35),
}
DEFAULT_MG5 = Path(os.environ.get("MG5_HOME", Path.home() / ".local/mg5dl/MG5_aMC_v3_7_2")) / "bin/mg5_aMC"
_INTERESTING = re.compile(r"error|invalid|warning|no particle|impossible|total:", re.I)
#: MadGraph start-up chatter about optional tools, unrelated to the model
_NOISE = re.compile(r"-config|Please set|set fastjet|set lhapdf|import format|Checking if MG5|"
                    r"failed to connect|default text editor|eps viewer|web browser|gzip", re.I)
_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_DUMMY_AS = re.compile(r"\bAS\s*=\s*(1\.38\d*D-01|0\.138)", re.I)


def run_mg5(mg5, workdir, name, commands):
    script = workdir / f"{name}.mg5"
    script.write_text("\n".join(commands) + "\n")
    r = subprocess.run([sys.executable, str(mg5), "-f", str(script)], cwd=workdir,
                       capture_output=True, text=True, timeout=1800)
    log = r.stdout + r.stderr
    (workdir / f"{name}.log").write_text(log)
    return log


def key_lines(log, limit=12):
    seen, out = set(), []
    for line in log.splitlines():
        s = _ANSI.sub("", line).strip()
        if s and _INTERESTING.search(s) and not _NOISE.search(s) and s not in seen \
                and not s.startswith("#"):
            seen.add(s)
            out.append(s)
    return out[:limit]


def read_param_card(path):
    """(block names, DECAY lines, {block: {code: (value, name)}}) of a param card."""
    blocks, decays, entries, current = [], [], {}, None
    for line in Path(path).read_text().splitlines():
        s = line.strip()
        if s.upper().startswith("BLOCK"):
            current = s.split()[1].upper()
            blocks.append(current)
            entries[current] = {}
        elif s.upper().startswith("DECAY"):
            decays.append(s)
            current = None
        elif current and s and not s.startswith("#"):
            body, _, comment = s.partition("#")
            parts = body.split()
            if len(parts) >= 2:
                entries[current][" ".join(parts[:-1])] = (parts[-1], comment.strip())
    return blocks, decays, entries


def width_entries(entries, name):
    """Where the param card stores parameter ``name``: ``BLOCK code = value`` strings."""
    return [f"{b} {code} = {v}" for b, e in entries.items() for code, (v, n) in e.items()
            if n == name]


def grep_dummy_aS(proc_dir):
    hits = []
    for f in sorted((proc_dir / "Source" / "MODEL").glob("*")):
        if f.is_file():
            for i, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
                if _DUMMY_AS.search(line):
                    hits.append(f"{f.relative_to(proc_dir)}:{i}: {line.strip()}")
    return hits


def probe(mg5, model_id, workdir):
    x, pdg = TARGETS[model_id]
    mdir = workdir / model_id
    mdir.mkdir(parents=True, exist_ok=True)
    ufo = models.copy_ufo(model_id, mdir) if not (mdir / models.ufo_path(model_id).name).exists() \
        else mdir / models.ufo_path(model_id).name
    imp = f"import model {ufo}"
    res = {"model": model_id, "x": x, "pdg": pdg}

    log = run_mg5(mg5, mdir, "p1_multiparticles", [imp, "display multiparticles"])
    res["p1_multiparticles"] = [l.strip() for l in log.splitlines()
                                if re.match(r"\s*(p|j|l\+|l-|vl|vl~)\s*=", l)]
    res["p1_lines"] = key_lines(log)

    log = run_mg5(mg5, mdir, "p2_pp", [imp, f"generate p p > {x}"])
    res["p2_lines"] = key_lines(log)
    res["p2_ok"] = bool(re.search(r"Total:\s*\d+\s*processes", log))

    proc = mdir / "proc_decay"
    log = run_mg5(mg5, mdir, "p3_output", [imp, f"generate {x} > all all", f"output {proc} -f"])
    res["p3_lines"] = key_lines(log)
    card = proc / "Cards" / "param_card.dat"
    if card.exists():
        blocks, decays, entries = read_param_card(card)
        res["p3_blocks"], res["p3_decays"] = blocks, decays
        res["p3_dummy_aS"] = grep_dummy_aS(proc)
        width_name = next((p["width"] for p in ufo_check._calls(ufo / "particles.py", "Particle")
                           if abs(int(p["pdg_code"])) == pdg), None)
        res["width_param"] = width_name
        res["width_before"] = width_entries(entries, width_name)

        log = run_mg5(mg5, mdir, "p4_widths",
                      [imp, f"compute_widths {x} --path={card} --body_decay=2"])
        res["p4_lines"] = key_lines(log)
        blocks2, decays2, entries2 = read_param_card(card)
        res["p4_decays"] = [d for d in decays2 if d.split()[1] == str(pdg)]
        res["width_after"] = width_entries(entries2, width_name)
    else:
        res["p3_blocks"] = None
    return res


def to_markdown(results, mg5):
    st = provenance.stamp()
    out = [f"# MadGraph probe of the feynlag-models UFOs ({st['date']})", "",
           f"Generated by `scripts/probe_mg5.py`. MadGraph: `{mg5}`. "
           f"feynlag {st['feynlag']}, feynlag-models `{st['feynlag-models_commit']}`, "
           f"Python {st['python']}. Each probe ran on a copy of the UFO; full logs were written "
           "to `runs/` (not committed).", ""]
    for r in results:
        out += [f"## `{r['model']}` (probe particle `{r['x']}`, PDG {r['pdg']})", ""]
        out += ["**P1, multiparticles defined after import:** "
                + (", ".join(f"`{m}`" for m in r["p1_multiparticles"]) or "none matching p/j/l/vl"), ""]
        out += [f"**P2, `generate p p > {r['x']}`:** " + ("built" if r["p2_ok"] else "**failed**"), ""]
        out += ["```", *r["p2_lines"], "```", ""]
        if r.get("p3_blocks") is None:
            out += ["**P3:** no param card was written.", "```", *r["p3_lines"], "```", ""]
            continue
        out += [f"**P3, param card of `generate {r['x']} > all all`:** blocks "
                + ", ".join(f"`{b}`" for b in r["p3_blocks"]) + "; DECAY lines: "
                + (", ".join(f"`{d}`" for d in r["p3_decays"]) or "none"), ""]
        out += ["Dummy `aS = 0.138` written by MadGraph: "
                + ("; ".join(f"`{h}`" for h in r["p3_dummy_aS"]) or "not found"), ""]
        out += [f"**P4, `compute_widths {r['x']}`:** DECAY {r['pdg']} after the run: "
                + (", ".join(f"`{d}`" for d in r["p4_decays"]) or "none"),
                f"Model width parameter `{r['width_param']}` (the value the matrix element uses) "
                f"before → after: `{r['width_before']}` → `{r['width_after']}`", ""]
        out += ["```", *r["p4_lines"], "```", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mg5", type=Path, default=DEFAULT_MG5)
    ap.add_argument("--out", type=Path,
                    default=REPO / "docs/evidence" / f"ufo_probe_{datetime.date.today()}.md")
    ap.add_argument("models", nargs="*", default=list(TARGETS))
    args = ap.parse_args()
    if not args.mg5.exists():
        raise SystemExit(f"MadGraph not found at {args.mg5} (set MG5_HOME or pass --mg5)")
    workdir = REPO / "runs" / f"probe_{datetime.date.today()}"
    results = [probe(args.mg5, m, workdir) for m in args.models]
    # repo-relative and ~-relative paths, so the evidence reads the same on any machine
    text = to_markdown(results, args.mg5).replace(str(REPO), ".").replace(str(Path.home()), "~")
    args.out.write_text(text)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
