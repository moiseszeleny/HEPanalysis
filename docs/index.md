# hepanalysis

Collider data analysis for **new-physics searches**, for people who build models: working
theorists and postdocs who have never run an analysis.

The library is deliberately small and **glass-box**:

- **Decisions are arguments, never defaults.** No function chooses a cut, a signal region, a
  background model or a test statistic for you.
- **Do it by hand, then use the library.** Each tutorial first does a step by hand, then calls
  the library and checks that the two agree.
- **Every number carries its provenance.** An external number has a source and the date the
  source was read; an unsourced one is `TODO_VERIFY` and refuses to enter arithmetic.

Models come from the verified [feynlag](https://github.com/moiseszeleny/feynlag) /
[feynlag-models](https://github.com/moiseszeleny/feynlag-models) stack. Data come from three
places: our own simulation (MadGraph → Pythia8 → Delphes), ATLAS Open Data, and published
likelihoods on HEPData.

```{toctree}
:maxdepth: 2
:caption: Course

syllabus
conventions
```

```{toctree}
:maxdepth: 1
:caption: Reference

api
```

```{toctree}
:maxdepth: 1
:caption: Upstream

upstream_gaps
evidence/ufo_probe_2026-10-22
```
