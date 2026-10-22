"""Build the small committed samples that T01 and T02 read offline.

    uv run python docs/tutorials/data/prepare_2muons.py

* data: all of ATLAS 2015 period D in the ``2muons`` skim (one file, ~125k events);
* the number of entries of every 2015 data period in the skim (for T02's luminosity estimate);
* MC: the first ``N_MC`` entries of each Sherpa Z -> mumu flavour slice (DIDs 700323-5),
  with the weight branches and the fraction read, so a tutorial can normalise them
  (the generator sum of weights is taken from the release metadata, in double precision).

Writes ``2muons_data15_periodD.parquet``, ``zmumu_mc.parquet`` and ``provenance.json``
next to this script. Only the columns the tutorials use are kept, in float32.
"""

import json
from pathlib import Path

import awkward as ak

from hepanalysis import provenance
from hepanalysis.io import opendata as od

HERE = Path(__file__).resolve().parent
SKIM = "2muons"
N_MC = 60_000
LEPTON = ["lep_n", "lep_pt", "lep_eta", "lep_phi", "lep_e", "lep_charge", "lep_type",
          "lep_isMediumID", "lep_isLooseIso", "lep_isTrigMatched", "trigM"]
WEIGHTS = ["mcWeight", "xsec", "filteff", "kfac",
           "ScaleFactor_PILEUP", "ScaleFactor_MUON", "ScaleFactor_LepTRIGGER"]
MC_DIDS = ["700323", "700324", "700325"]


def slim(a):
    out = {}
    for f in a.fields:
        x = a[f]
        if "float" in str(ak.type(x)):
            x = ak.values_astype(x, "float32")
        out[f] = x
    return ak.zip(out, depth_limit=1)


def main():
    prov = {"release": od.RELEASE, "skim": SKIM, "stamp": provenance.stamp(), "samples": {}}

    data_url = next(u for u in od.urls("data", SKIM) if "data15_periodD" in u)
    data = slim(od.read(data_url, LEPTON))
    ak.to_parquet(data, HERE / "2muons_data15_periodD.parquet", compression="zstd")
    prov["samples"]["data15_periodD"] = {"url": data_url, "entries": len(data), "fraction_read": 1.0}

    prov["data15_entries_per_period"] = {
        u.rsplit("data15_", 1)[1].split(".")[0]: od.num_entries(u)
        for u in od.urls("data", SKIM) if "data15_" in u}

    parts = []
    for did in MC_DIDS:
        url = od.urls(did, SKIM)[0]
        total = od.num_entries(url)
        a = slim(od.read(url, LEPTON + WEIGHTS, entry_stop=N_MC))
        a = ak.with_field(a, int(did), "did")
        parts.append(a)
        md = od.metadata(did)
        prov["samples"][did] = {"url": url, "physics_short": md["physics_short"],
                                "entries_in_file": total, "entries_read": len(a),
                                "fraction_read": len(a) / total,
                                "metadata": {k: md[k] for k in ("cross_section_pb", "genFiltEff",
                                                                 "kFactor", "sumOfWeights",
                                                                 "nEvents", "generator")}}
    ak.to_parquet(ak.concatenate(parts), HERE / "zmumu_mc.parquet", compression="zstd")
    (HERE / "provenance.json").write_text(json.dumps(prov, indent=2))


if __name__ == "__main__":
    main()
