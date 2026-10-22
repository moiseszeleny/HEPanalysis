"""Read-only access to feynlag-models.

Models are loaded only through ``feynlag_models.registry`` (a stack-wide rule, see
``../CLAUDE.md``). Nothing here writes into the installed feynlag-models package: a
UFO that MadGraph will touch is copied first (``copy_ufo``).
"""

from __future__ import annotations

import shutil
from pathlib import Path

from feynlag_models import MODELS_DIR, registry


def model_ids():
    return registry.model_ids()


def metadata(model_id):
    return registry.metadata(model_id)


def maturity(model_id):
    return int(metadata(model_id)["maturity_level"])


def ufo_path(model_id):
    """The model's committed UFO directory, or ``None`` if it ships no UFO."""
    ufo = metadata(model_id).get("outputs", {}).get("ufo")
    return MODELS_DIR / model_id / ufo if ufo else None


def placeholders(model_id):
    """Benchmark inputs the model itself marks as guessed (e.g. widths set to 1 GeV)."""
    return list(metadata(model_id)["benchmark"].get("placeholders", []))


def copy_ufo(model_id, dest):
    """Copy a model's UFO into ``dest`` and return the copy's path.

    MadGraph writes caches into a UFO directory when it imports it, so it must
    only ever see a copy.
    """
    src = ufo_path(model_id)
    if src is None:
        raise ValueError(f"{model_id} ships no UFO (maturity L{maturity(model_id)})")
    out = Path(dest) / src.name
    shutil.copytree(src, out, ignore=shutil.ignore_patterns("__pycache__", "*.pkl"))
    return out
