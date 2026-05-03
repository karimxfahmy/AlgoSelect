"""
Shared types used by every algorithm module.

Keeping these in one place so the engine and the API don't have to import
from every individual solver. Each algorithm returns an AlgoResult so the
selector can compare them in a uniform way.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any


@dataclass
class AlgoResult:
    # name of the algorithm that produced this (e.g. "knapsack_dp")
    algorithm: str

    # the problem family this result belongs to
    problem_type: str

    # the actual answer, shape depends on problem_type
    # knapsack -> {"value": int, "items": [...]}
    # dijkstra -> {"distances": {...}, "paths": {...}}
    # sorting  -> {"sorted": [...]}
    # search   -> {"index": int}
    solution: dict[str, Any]

    # objective value (higher is better for knapsack, lower is better for
    # routing). The selector uses this when ranking experiment results.
    value: float

    # how long the run took, in milliseconds. Real wall-clock, not estimated.
    runtime_ms: float

    # extra stuff worth showing the user (DP table, recursion trace, number
    # of states evaluated, etc). Free-form by design.
    trace: dict[str, Any] = field(default_factory=dict)

    # human-readable note. Greedy uses this to warn about approximation.
    note: str = ""


class Timer:
    """Tiny context manager so timing code reads cleanly.

    Usage:
        with Timer() as t:
            do_stuff()
        print(t.ms)
    """

    def __enter__(self) -> "Timer":
        self._start = perf_counter()
        return self

    def __exit__(self, *exc) -> None:
        self.ms = (perf_counter() - self._start) * 1000.0
