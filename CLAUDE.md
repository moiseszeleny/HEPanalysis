# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

`hepanalysis` teaches collider data analysis for **BSM searches** to **working theorists and
postdocs**: people who build models but have never run an analysis. The aim is research
judgment, knowing when a limit can be trusted. It is a small Python library plus solved
tutorials (`docs/tutorials/`, Sphinx + myst-nb, like feynlag). It is in English.

It is the fourth consumer of the feynlag stack (`../CLAUDE.md`): feynlag → feynlag-models →
{feynlag-anomalies, HEPanalysis}.
- It pins `feynlag==0.3.0` and `feynlag-models @ git+…@cb0678a`. These are the same pins as
  feynlag-anomalies, and they must stay in step with it.
- Models load only through `feynlag_models.registry`, wrapped read-only by `hepanalysis.models`.

The three data sources:
1. our own simulation (MadGraph 3.7.2 → Pythia8 → Delphes);
2. ATLAS Open Data (13 TeV);
3. published likelihoods (HEPData, pyhf).

The plan of record is `docs/syllabus.md`: Track A (SM benchmarks), Track B (BSM: Z′, heavy
scalar, VLL, heavy neutrinos), Track C (reinterpretation and judgment).

## Commands

```bash
uv sync --all-extras                                  # after any pyproject/uv.lock change
uv run pytest -q                                      # fast suite (slow is deselected by default)
uv run pytest -q -rxX tests/test_upstream_gaps.py     # what is still waiting upstream
uv run python -m hepanalysis.ufo_check thdm_type2     # static UFO readiness report (id or path)
uv run python scripts/probe_mg5.py                    # MadGraph probe → docs/evidence/ufo_probe_<date>.md
uv run sphinx-build -W docs docs/_build               # docs; must stay warning-free
```

- MadGraph lives at `~/.local/mg5dl/MG5_aMC_v3_7_2` (override with `MG5_HOME`). Scratch output
  goes to `runs/`, which is git-ignored.
- MadGraph writes caches into any UFO it imports, so it only ever sees a copy
  (`hepanalysis.models.copy_ufo`), never the installed feynlag-models files.

## Hard rules

1. **Glass-box library.**
   - Physics decisions (cuts, signal regions, background models, test statistics, CL) are
     explicit arguments and never defaults; a function raises if one is missing.
   - Code goes into the library only once a tutorial has first done the same step by hand and
     `assert`ed agreement.
   - Plumbing (I/O, generator drivers, bookkeeping, plotting) can go straight in.
2. **Honesty.**
   - No experimental number without a source and the date it was read (`provenance.Cited`).
     Otherwise use `TodoVerify` / `TODO_VERIFY`; never guess.
   - Take citations from INSPIRE (`curl -G https://inspirehep.net/api/literature --data-urlencode
     "q=arxiv:<id>"`), not from memory.
   - Tag every claim in prose **computed** or **cited**.
   - Never weaken a failing test.
3. **Maturity gates.**
   - Simulate only models at L3 or above whose UFO passes `ufo_check` (`ready_for_pp`).
   - Present a limit only from an L4 model, or from a tutorial that does the L4-style
     cross-check itself and says so.
4. **No edits to sibling repos.**
   - Gaps go in `docs/upstream_gaps.md` (`HG-n`), and model needs go in `model_requests/<id>.md`.
   - Each open item is pinned by a strict xfail in `tests/test_upstream_gaps.py`.
   - Evidence for a ticket comes from `ufo_check` or `scripts/probe_mg5.py` output, never from
     expectation.
   - When you file or close one, end the reply with the `HANDOFF` line from `../CLAUDE.md`.
5. **Conventions.**
   - Model quantities keep `feynlag-models/CONVENTIONS.md`.
   - The analysis conventions (units, weights, kinematics, statistics) are in
     `docs/conventions.md`.

## Tutorial format (chosen by the user, 2026-10-22)

- **Files.** Each tutorial is `docs/tutorials/Txx_<slug>/` holding:
  - `Txx_<slug>.md`: a MyST/jupytext text notebook with no stored outputs;
  - `txx_solutions.py`: the reference solutions;
  - `txx_checks.py`: the checkpoints, built only from the solutions or `Cited` values, never
    from literals.
- **Shared data.** Shared derived data lives in `docs/tutorials/data/`, with its `prepare_*.py`
  and `provenance.json`.
- **Exercises and checkpoints.** The reader writes `def my_x(...): raise NotImplementedError`,
  then calls `check_k(my_x)` and `x = check_k.use(my_x)` (the reference is the fallback).
  Checkpoints come from `hepanalysis.checkpoints`.
- **Every tutorial has:**
  - a paper anchor, verified on INSPIRE;
  - prediction blockquotes;
  - "read it" discussions tagged computed or cited;
  - a **Would you trust this?** admonition;
  - a **find the flaw** `choice` checkpoint;
  - an **Explore** cell with ipywidgets (live kernel only, with a static fallback plot);
  - a recap, and judgment exercises without solutions.
- **Execution.** The docs build executes the notebooks (myst-nb `cache` mode, raise on error),
  so `sphinx-build -W` is the notebook test. `tests/test_tutorial_solutions.py` checks that
  every reference passes its own checkpoints.
- **Offline only.** Tutorials read only committed derived samples; the network is used only
  by `prepare_*.py`.

## Workflow

- **Pin bumps.** A pin bump arrives through the hub cascade (`../CLAUDE.md`). Bump feynlag and
  feynlag-models together with feynlag-anomalies, run `uv sync --all-extras`, and run the suite.
  If a strict xfail XPASSes:
  1. remove its marker;
  2. move the ticket to **Resolved**;
  3. update `docs/syllabus.md`.
- **Commits.** Commit with `git -c user.name="Moises Zeleny" -c user.email="moiseszeleny@gmail.com"
  commit …`, and stage explicit paths. Creating the GitHub repo or pushing needs the user's OK.
