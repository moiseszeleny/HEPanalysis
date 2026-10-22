"""A cutflow: the cuts are the reader's, the bookkeeping is the library's."""

from __future__ import annotations

import numpy as np


class Cutflow:
    """Apply named boolean masks in order and record raw and weighted counts after each.

    >>> cf = Cutflow(events, weights)
    >>> cf.apply("two muons", events.lep_n >= 2).apply("opposite sign", q1 * q2 < 0)
    >>> print(cf.table())
    """

    def __init__(self, events, weights=None):
        self.events = events
        self.weights = np.ones(len(events)) if weights is None else np.asarray(weights, dtype=float)
        self.rows = [("all", len(events), float(self.weights.sum()))]

    def apply(self, name, mask):
        mask = np.asarray(mask, dtype=bool)
        if mask.shape != (len(self.events),):
            raise ValueError(f"cut {name!r}: mask has shape {mask.shape}, expected ({len(self.events)},)")
        self.events = self.events[mask]
        self.weights = self.weights[mask]
        self.rows.append((name, len(self.events), float(self.weights.sum())))
        return self

    def table(self):
        lines = ["| cut | events | weighted | efficiency (cumulative) |", "|---|---|---|---|"]
        first = self.rows[0][2] or 1.0
        for name, n, w in self.rows:
            lines.append(f"| {name} | {n} | {w:.4g} | {w / first:.3f} |")
        return "\n".join(lines)
