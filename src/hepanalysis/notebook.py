"""Notebook plumbing: interactive "explore" cells that degrade to a static plot.

Widgets need a live frontend. The docs build sets ``HEPANALYSIS_STATIC=1`` (in
``docs/conf.py``; executed kernels inherit it), and then ``explore`` calls the function
once with the static settings instead of drawing sliders.
"""

from __future__ import annotations

import os

STATIC_ENV = "HEPANALYSIS_STATIC"


def is_static():
    return os.environ.get(STATIC_ENV) == "1"


def explore(func, static, **widgets):
    """``ipywidgets.interact(func, **widgets)`` in a live kernel, else ``func(**static)``."""
    if not is_static():
        try:
            import ipywidgets
            return ipywidgets.interact(func, **widgets)
        except ImportError:
            pass
    return func(**static)
