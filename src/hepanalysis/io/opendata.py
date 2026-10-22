"""ATLAS Open Data access (13 TeV education release), through ``atlasopenmagic``.

The release is an explicit argument everywhere (default: the one the tutorials were
written against), so a tutorial never changes data silently when a new release appears.
Files are read with uproot over https; uproot fetches only the branches and entries
asked for, so a 20 GB skim can be sampled column by column.

Units: in the 2025 education release, energies and momenta are stored in GeV
(checked on 2026-10-22: Z -> mumu muons have lep_pt ~ 40 GeV). Older releases used MeV,
so a tutorial that switches release must check again.
"""

from __future__ import annotations

import uproot

RELEASE = "2025e-13tev-beta"
TREE = "analysis"


def _atom(release):
    import atlasopenmagic as atom
    if atom.get_current_release() != release:
        atom.set_release(release)
    return atom


def urls(key, skim, release=RELEASE):
    """https URLs of a dataset: ``key`` is ``'data'`` or an MC dataset number (DID)."""
    found = _atom(release).get_urls(str(key), skim, protocol="https", cache=False)
    return [u.removeprefix("simplecache::") for u in found]


def metadata(did, release=RELEASE):
    """The MC metadata record (cross section, filter efficiency, k-factor, sum of weights...)."""
    return _atom(release).get_metadata(str(did))


def _open(url):
    # uproot's own HTTP source: fsspec's aiohttp path fails on large multi-range reads here
    return uproot.open(url, handler=uproot.source.http.HTTPSource)


def num_entries(url, tree=TREE):
    with _open(url) as f:
        return f[tree].num_entries


def read(url, branches, entry_stop=None, tree=TREE, chunk=25_000):
    """The requested branches of one file as an awkward array.

    Reads in chunks of ``chunk`` entries: one huge multi-range request over https can
    stall, many small ones do not.
    """
    import awkward as ak
    with _open(url) as f:
        t = f[tree]
        stop = t.num_entries if entry_stop is None else min(entry_stop, t.num_entries)
        parts = [t.arrays(list(branches), entry_start=a, entry_stop=min(a + chunk, stop), library="ak")
                 for a in range(0, stop, chunk)]
    return ak.concatenate(parts) if parts else t.arrays(list(branches), entry_stop=0, library="ak")
