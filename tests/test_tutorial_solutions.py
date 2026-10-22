"""Every tutorial's reference solutions pass its own checkpoints, and every find-the-flaw key is consistent.

Each tutorial's ``tNN_checks.py`` imports ``tNN_solutions`` by name, as the notebook does
from its own directory, so the tutorial directory goes on ``sys.path`` for the import.
"""

import importlib
import sys
from pathlib import Path

import pytest

from hepanalysis.checkpoints import Checkpoint

TUTORIALS = sorted(p for p in (Path(__file__).resolve().parent.parent / "docs" / "tutorials").glob("T*_*")
                   if p.is_dir())


@pytest.mark.parametrize("tdir", TUTORIALS, ids=lambda p: p.name)
def test_reference_solutions_pass_their_checkpoints(tdir, capsys):
    prefix = tdir.name[:3].lower()
    sys.path.insert(0, str(tdir))
    try:
        checks = importlib.import_module(f"{prefix}_checks")
    finally:
        sys.path.remove(str(tdir))
    found = {n: c for n, c in vars(checks).items() if isinstance(c, Checkpoint)}
    assert found, f"{tdir.name} defines no checkpoints"
    for name, cp in found.items():
        assert cp.evaluate(cp.reference)[0], f"{tdir.name}:{name} rejects its own reference"
        if hasattr(cp, "options"):
            wrong = [k for k in cp.options if k != cp.reference]
            assert all(not cp.evaluate(k)[0] for k in wrong), f"{tdir.name}:{name} accepts a wrong option"
