"""Checkpoints for tutorial exercises: feedback on the reader's answer, with staged hints.

The pattern follows feynlag-anomalies' ``checkpoints/core.py`` (``Checkpoint`` with
staged ``.hint()``, ``numeric_tolerance``, ``exact_match``), reimplemented here so this
repo does not depend on that one. Two additions:

* ``use(answer)`` returns the reader's answer when it passes and the reference
  solution otherwise (with a visible note), so the rest of the notebook keeps working
  while the reader is still stuck on one step.
* an exercise left as ``raise NotImplementedError`` is reported as "not attempted yet"
  instead of crashing the notebook.

Expected values always come from a tutorial's ``solutions`` module or from a ``Cited``
number, never from a literal typed into the checks file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np


@dataclass
class Checkpoint:
    name: str
    check_fn: Callable[[Any], tuple[bool, str]]
    reference: Any = None
    hints: list[str] = field(default_factory=list)
    _hint_level: int = field(default=0, init=False, repr=False)

    def evaluate(self, answer) -> tuple[bool, str]:
        """``(passed, message)`` without printing; a reader's error never propagates."""
        try:
            return self.check_fn(answer)
        except NotImplementedError:
            return False, "not attempted yet"
        except Exception as exc:  # noqa: BLE001  (the reader's code may raise anything)
            return False, f"your code raised {type(exc).__name__}: {exc}"

    def __call__(self, answer) -> bool:
        ok, message = self.evaluate(answer)
        suffix = f" -- {message}" if message else ""
        if ok:
            print(f"[{self.name}] correct{suffix}")
        else:
            nudge = " Call .hint() for a nudge." if self.hints else ""
            print(f"[{self.name}] not yet{suffix}.{nudge}")
        return ok

    def use(self, answer):
        """The reader's answer if it passes, else the reference (so later cells still run)."""
        if self.evaluate(answer)[0]:
            return answer
        print(f"[{self.name}] using the reference solution for the cells below.")
        return self.reference

    def hint(self, level: int | None = None) -> str:
        """Reveal the next staged hint (or jump to ``level``, 1-indexed)."""
        if not self.hints:
            raise ValueError(f"checkpoint {self.name!r} has no hints")
        if level is not None:
            if not 1 <= level <= len(self.hints):
                raise ValueError(f"hint level must be between 1 and {len(self.hints)}")
            self._hint_level = level
        else:
            self._hint_level = min(self._hint_level + 1, len(self.hints))
        text = self.hints[self._hint_level - 1]
        print(f"[{self.name}] hint {self._hint_level}/{len(self.hints)}: {text}")
        return text


def _close(a, b, rel_tol, abs_tol):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return a.shape == b.shape and bool(np.allclose(a, b, rtol=rel_tol, atol=abs_tol, equal_nan=True))


def numeric_tolerance(name, expected, rel_tol=1e-6, abs_tol=0.0, hints=None) -> Checkpoint:
    """Passes if the answer (a number or an array) is within tolerance of ``expected``."""

    def check_fn(answer):
        if _close(answer, expected, rel_tol, abs_tol):
            return True, ""
        return False, "the value does not match"

    return Checkpoint(name, check_fn, reference=expected, hints=list(hints or []))


def function_matches(name, reference_fn, cases, rel_tol=1e-6, abs_tol=0.0, hints=None) -> Checkpoint:
    """Passes if the reader's function agrees with ``reference_fn`` on every case.

    ``cases`` is a list of argument tuples. The reference function becomes the
    fallback that ``use`` returns.
    """

    def check_fn(fn):
        if not callable(fn):
            return False, "expected a function"
        for i, args in enumerate(cases):
            if not _close(fn(*args), reference_fn(*args), rel_tol, abs_tol):
                return False, f"case {i} disagrees with the reference"
        return True, f"agrees on {len(cases)} cases"

    return Checkpoint(name, check_fn, reference=reference_fn, hints=list(hints or []))


def exact_match(name, expected, hints=None) -> Checkpoint:
    def check_fn(answer):
        return (answer == expected, "" if answer == expected else "not the expected answer")

    return Checkpoint(name, check_fn, reference=expected, hints=list(hints or []))


def choice(name, options: dict[str, str], correct: str, explanations: dict[str, str],
           hints=None) -> Checkpoint:
    """A multiple-choice question (used by the "find the flaw" sections).

    ``explanations`` maps every option key to why it is right or wrong; the reader
    sees the explanation of the option they picked.
    """
    if correct not in options or set(explanations) != set(options):
        raise ValueError("correct must be an option and every option needs an explanation")

    def check_fn(answer):
        key = str(answer).strip().lower()
        if key not in options:
            return False, f"pick one of {sorted(options)}"
        return key == correct, explanations[key]

    cp = Checkpoint(name, check_fn, reference=correct, hints=list(hints or []))
    cp.options = options
    return cp


__all__ = ["Checkpoint", "numeric_tolerance", "function_matches", "exact_match", "choice"]
