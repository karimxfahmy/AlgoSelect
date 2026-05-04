"""
Algorithm runner + experiment mode.

The runner has two jobs:
    1. Given a Selection (from the selector) and a payload, execute the
       chosen algorithm and return its AlgoResult.
    2. In experiment mode, run *every* applicable algorithm on the same
       input and return them ranked so the UI can show a comparison table.

We keep the dispatch table tiny and explicit. Adding a new algorithm means
one new entry per problem family — no magic registries.
"""

from __future__ import annotations

from typing import Any, Callable

from app.algorithms import (
    brute_force,
    dijkstra_greedy,
    divide_conquer,
    knapsack_dp,
)
from app.algorithms.common import AlgoResult


# ---------------------------------------------------------------------------
# direct execution: one algorithm at a time
# ---------------------------------------------------------------------------

def run_one(algorithm: str, payload: dict[str, Any]) -> AlgoResult:
    """Run a single named algorithm against a problem payload.

    Payload shape depends on the problem family. The API layer is what
    validates that — by the time we get here we trust the keys are present.
    """
    if algorithm == "knapsack_dp":
        return knapsack_dp.solve(
            weights=payload["weights"],
            values=payload["values"],
            capacity=payload["capacity"],
        )

    if algorithm == "brute_force_knapsack":
        return brute_force.knapsack(
            weights=payload["weights"],
            values=payload["values"],
            capacity=payload["capacity"],
        )

    if algorithm == "dijkstra_greedy":
        return dijkstra_greedy.solve(payload["graph"])

    if algorithm == "brute_force_routing":
        return brute_force.routing(payload["graph"])

    if algorithm == "merge_sort":
        return divide_conquer.merge_sort(payload["array"])

    if algorithm == "brute_force_sort":
        return brute_force.permutation_sort(payload["array"])

    if algorithm == "binary_search":
        return divide_conquer.binary_search(
            arr=payload["array"], target=payload["target"]
        )

    if algorithm == "brute_force_search":
        return brute_force.linear_search(
            arr=payload["array"], target=payload["target"]
        )

    if algorithm == "fast_exponent":
        return divide_conquer.fast_exponent(
            base=payload["base"], exp=payload["exp"]
        )

    if algorithm == "naive_exponent":
        return brute_force.naive_exponent(
            base=payload["base"], exp=payload["exp"]
        )

    # the selector occasionally returns "unsupported" (e.g. negative-weight
    # routing). callers must check for that before getting here.
    raise ValueError(f"unknown or unsupported algorithm: {algorithm!r}")


# ---------------------------------------------------------------------------
# experiment mode: run every applicable algorithm and rank the results
# ---------------------------------------------------------------------------

# which algorithms are eligible for which problem family. brute force is
# included only when the input is small enough (the algorithm modules will
# raise otherwise; we pre-filter to keep the table clean).
_FAMILY_ALGOS: dict[str, list[str]] = {
    "knapsack": ["knapsack_dp", "brute_force_knapsack"],
    "routing": ["dijkstra_greedy", "brute_force_routing"],
    "sorting": ["merge_sort", "brute_force_sort"],
    "search":  ["binary_search", "brute_force_search"],
    "exponent": ["fast_exponent", "naive_exponent"],
}


def run_experiment(
    problem_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Run every applicable algorithm and rank them.

    Ranking is per-family:
      - knapsack: higher value is better
      - routing:  lower total distance is better
      - sorting:  pure runtime race (all results should be identical)
      - search:   exact-match race (all results should be identical)

    We also compute an approximation ratio against the best (= ground truth)
    so the UI can highlight how close greedy/heuristic results came.
    """
    algos = _FAMILY_ALGOS.get(problem_type)
    if not algos:
        raise ValueError(f"no experiment defined for problem type {problem_type!r}")

    runs: list[dict[str, Any]] = []

    for algo in algos:
        # brute force has hard input caps. skip cleanly instead of crashing.
        if not _is_applicable(algo, payload):
            runs.append({
                "algorithm": algo,
                "skipped": True,
                "reason": "input too large for this algorithm",
            })
            continue

        try:
            res = run_one(algo, payload)
        except Exception as exc:
            # don't let one busted algorithm sink the whole comparison
            runs.append({
                "algorithm": algo,
                "skipped": True,
                "reason": f"runtime error: {exc}",
            })
            continue

        runs.append({
            "algorithm": res.algorithm,
            "skipped": False,
            "value": res.value,
            "runtime_ms": res.runtime_ms,
            "solution": res.solution,
            "trace": res.trace,
            "note": res.note,
        })

    # figure out the "best" value to compute approximation ratios against
    finished = [r for r in runs if not r.get("skipped")]
    best_value = _pick_best_value(problem_type, finished)
    for r in finished:
        r["approximation_ratio"] = _approx_ratio(problem_type, r["value"], best_value)

    # rank: best first
    finished.sort(key=lambda r: _rank_key(problem_type, r))
    skipped = [r for r in runs if r.get("skipped")]
    ordered = finished + skipped

    return {
        "problem_type": problem_type,
        "ranked": ordered,
        "best_value": best_value,
    }


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

# input-size limits mirror what brute_force.py enforces. keep these in sync.
_BRUTE_FORCE_LIMITS = {
    "brute_force_knapsack": ("weights", 20),
    "brute_force_routing":  ("graph_nodes", 8),
    "brute_force_sort":     ("array", 8),
    # linear search has no real cap, but keep it bounded so the UI doesn't
    # show a 100k-row scan in the table
    "brute_force_search":   ("array", 100_000),
    "naive_exponent":       ("exp", 1_000_000),
}


def _is_applicable(algorithm: str, payload: dict[str, Any]) -> bool:
    if algorithm not in _BRUTE_FORCE_LIMITS:
        return True
    key, cap = _BRUTE_FORCE_LIMITS[algorithm]
    if key == "weights":
        return len(payload.get("weights", [])) <= cap
    if key == "graph_nodes":
        return len(payload.get("graph", {}).get("nodes", [])) <= cap
    if key == "array":
        return len(payload.get("array", [])) <= cap
    if key == "exp":
        return abs(int(payload.get("exp", 0))) <= cap
    return True


def _pick_best_value(problem_type: str, runs: list[dict[str, Any]]) -> float | None:
    if not runs:
        return None
    if problem_type == "knapsack":
        return max(r["value"] for r in runs)
    if problem_type == "routing":
        # lower is better; ignore zero/none placeholders
        candidates = [r["value"] for r in runs if r["value"] > 0]
        return min(candidates) if candidates else None
    # sorting/search don't really have a "best value" — pick the first one
    return runs[0]["value"]


def _approx_ratio(
    problem_type: str, value: float, best: float | None
) -> float | None:
    if best is None or best == 0:
        return None
    if problem_type == "knapsack":
        # higher value is better, ratio is value / best (1.0 == optimal)
        return round(value / best, 4)
    if problem_type == "routing":
        # lower is better, ratio is best / value (1.0 == optimal)
        return round(best / value, 4) if value > 0 else None
    return 1.0


def _rank_key(problem_type: str, run: dict[str, Any]) -> tuple:
    # primary key: solution quality. secondary: runtime (faster wins ties).
    if problem_type == "knapsack":
        return (-run["value"], run["runtime_ms"])
    if problem_type == "routing":
        return (run["value"] if run["value"] > 0 else float("inf"), run["runtime_ms"])
    # sorting/search: just sort by runtime
    return (run["runtime_ms"],)
