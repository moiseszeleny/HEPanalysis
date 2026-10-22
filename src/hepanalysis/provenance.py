"""Where every number comes from.

Three kinds of numbers appear in an analysis, and the library keeps them apart:

* ``Cited``: an external number (a measured mass, a published cross section, a
  luminosity). It cannot exist without a source and the date that source was read.
* ``Computed``: a number this library or a tutorial produced, together with the
  inputs it was produced from.
* ``TodoVerify``: a number we need but have not sourced yet. It refuses to take part
  in arithmetic, so an unsourced value can never leak into a result.
"""

from __future__ import annotations

import datetime
import platform
from dataclasses import dataclass, field
from importlib import metadata as _importlib_metadata


@dataclass(frozen=True)
class Cited:
    """An external number with its source.

    ``unc`` is a symmetric uncertainty or a ``(minus, plus)`` pair, in the same
    ``unit`` as ``value``. ``checked_on`` is the ISO date the source was read.
    """

    value: float
    unc: float | tuple[float, float] | None
    unit: str
    source: str
    checked_on: str
    tag: str = field(default="cited", init=False)

    def __post_init__(self):
        if not self.source.strip():
            raise ValueError("a Cited number needs a source")
        try:
            datetime.date.fromisoformat(self.checked_on)
        except ValueError as exc:
            raise ValueError(
                f"checked_on must be an ISO date (YYYY-MM-DD), got {self.checked_on!r}") from exc

    def __float__(self):
        return float(self.value)


@dataclass(frozen=True)
class Computed:
    """A number produced here, with the inputs it was computed from."""

    value: float
    unit: str
    how: str
    inputs: dict = field(default_factory=dict)
    tag: str = field(default="computed", init=False)

    def __float__(self):
        return float(self.value)


@dataclass(frozen=True)
class TodoVerify:
    """A placeholder for a number nobody has sourced yet.

    Any attempt to use it as a number raises ``TypeError``.
    """

    what: str
    tag: str = field(default="TODO_VERIFY", init=False)

    def _refuse(self, *_):
        raise TypeError(f"TODO_VERIFY: {self.what} has no source yet; cite it before using it")

    __float__ = __add__ = __radd__ = __sub__ = __rsub__ = _refuse
    __mul__ = __rmul__ = __truediv__ = __rtruediv__ = __pow__ = _refuse


def _version(dist):
    try:
        return _importlib_metadata.version(dist)
    except _importlib_metadata.PackageNotFoundError:
        return None


def _direct_url(dist):
    """The commit a git-pinned distribution was installed from, if any."""
    try:
        text = _importlib_metadata.distribution(dist).read_text("direct_url.json")
    except _importlib_metadata.PackageNotFoundError:
        return None
    if not text:
        return None
    import json
    info = json.loads(text)
    vcs = info.get("vcs_info", {})
    return vcs.get("commit_id")


def stamp():
    """Tool versions behind a result: attach this to anything a tutorial reports."""
    return {
        "hepanalysis": _version("hepanalysis"),
        "feynlag": _version("feynlag"),
        "feynlag-models": _version("feynlag-models"),
        "feynlag-models_commit": _direct_url("feynlag-models"),
        "python": platform.python_version(),
        "date": datetime.date.today().isoformat(),
    }
