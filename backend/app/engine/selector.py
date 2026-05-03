"""
Rule-based algorithm selector.

Given a small description of a problem instance (type, size, time budget,
quality requirement) we walk a fixed decision flow and pick exactly one
algorithm. Along the way we record every check we made and which branch
we took, so the front-end can render a flowchart of the actual decision.

The rules are deliberately simple and explicit. No ML, no scoring — just
"if this then that". Easier to explain, easier to debug.

Problem types supported right now:
    - knapsack
    - routing       (single-source shortest path on a non-negative graph)
    - sorting
    - search        (membership + index lookup on a sorted array)

Quality:
    - exact         must be the optimum
    - approximate   any reasonable answer is fine, prefer fast
    - best-effort   spec-default; we apply normal rules

Time budget T is in milliseconds. We use it as a soft hint: very small
budgets push us toward greedy / D&C even when DP would otherwise win.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


# ---------------------------------------------------------------------------
# data shapes
# ---------------------------------------------------------------------------

ProblemType = Literal["knapsack", "routing", "sorting", "search"]
Quality = Literal["exact", "approximate", "best-effort"]


@dataclass
class ProblemSpec:
    problem_type: ProblemType
    n: int                              # input size (items / nodes / array length)
    time_budget_ms: int                 # how long the user is willing to wait
    quality: Quality = "best-effort"

    # extra problem-specific bits the selector might peek at
    has_negative_weights: bool = False  # for routing
    is_sorted: bool = False             # for search
    force_brute_force: bool = False     # explicit correctness check


@dataclass
class DecisionStep:
    # one node in the flowchart we hand back to the UI
    question: str
    answer: str
    branch: str           # short label, used as edge text in the diagram


@dataclass
class Selection:
    algorithm: str                       # e.g. "knapsack_dp"
    justification: str                   # one paragraph, plain english
    expected_complexity: str             # big-O text
    quality_guarantee: str               # "exact" / "approx ratio X" / etc.
    trace: list[DecisionStep] = field(default_factory=list)


# ---------------------------------------------------------------------------
# thresholds — tuned to keep runs snappy on a laptop
# ---------------------------------------------------------------------------

# knapsack DP table size limit (n * capacity cells). past this we punt to
# greedy / brute-force depending on size. capacity isn't in ProblemSpec yet,
# so for now we just guard on n alone and trust the API layer to validate.
DP_N_LIMIT = 500

# brute force only kicks in below this. matches the algorithm module caps.
BRUTE_FORCE_KNAPSACK_LIMIT = 20
BRUTE_FORCE_ROUTING_LIMIT = 8
BRUTE_FORCE_SORT_LIMIT = 8

# "very small" time budget — below this we lean greedy/D&C aggressively
TINY_BUDGET_MS = 50


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

def select(spec: ProblemSpec) -> Selection:
    """Return the chosen algorithm plus the trail of decisions taken."""

    # explicit override always wins. lets the user verify other algos.
    if spec.force_brute_force:
        return _brute_force_path(spec, reason="user requested correctness check")

    # dispatch on problem family. each branch handles its own rules.
    if spec.problem_type == "knapsack":
        return _select_knapsack(spec)
    if spec.problem_type == "routing":
        return _select_routing(spec)
    if spec.problem_type == "sorting":
        return _select_sorting(spec)
    if spec.problem_type == "search":
        return _select_search(spec)

    # shouldn't happen — Pydantic / Literal will normally catch this earlier
    raise ValueError(f"unknown problem type: {spec.problem_type!r}")


# ---------------------------------------------------------------------------
# per-family decision flows
# ---------------------------------------------------------------------------

def _select_knapsack(spec: ProblemSpec) -> Selection:
    trace: list[DecisionStep] = []
    trace.append(DecisionStep(
        question="What is the problem type?",
        answer="knapsack",
        branch="knapsack",
    ))

    # 1) tiny input + exact requested -> brute force is fine and proves optimum
    if spec.n <= BRUTE_FORCE_KNAPSACK_LIMIT and spec.quality == "exact" and spec.n <= 15:
        trace.append(DecisionStep(
            question=f"Is n small enough for exhaustive search (n <= 15)?",
            answer=f"yes (n={spec.n})",
            branch="tiny+exact",
        ))
        return Selection(
            algorithm="brute_force_knapsack",
            justification=(
                f"Input is tiny (n={spec.n}) and the user asked for an exact "
                f"answer, so we enumerate all 2^n subsets. This guarantees the "
                f"true optimum and lets us double-check any heuristic later."
            ),
            expected_complexity="O(2^n * n)",
            quality_guarantee="exact",
            trace=trace,
        )

    # 2) very tight time budget -> we don't have time to fill a DP table
    if spec.time_budget_ms < TINY_BUDGET_MS and spec.quality != "exact":
        trace.append(DecisionStep(
            question=f"Is time budget very tight (<{TINY_BUDGET_MS}ms)?",
            answer=f"yes ({spec.time_budget_ms}ms)",
            branch="tight-budget",
        ))
        # NOTE: we don't actually have a knapsack-greedy module yet (spec only
        # asked for dijkstra-greedy). fall back to brute force on small n,
        # otherwise punt to DP and accept the budget overshoot.
        if spec.n <= BRUTE_FORCE_KNAPSACK_LIMIT:
            return _brute_force_path(spec, reason="tight budget but n is tiny")
        # falls through to DP below

    # 3) DP is the right call when n is in range
    if spec.n <= DP_N_LIMIT:
        trace.append(DecisionStep(
            question=f"Is n within the DP table limit (n <= {DP_N_LIMIT})?",
            answer=f"yes (n={spec.n})",
            branch="dp-fits",
        ))
        return Selection(
            algorithm="knapsack_dp",
            justification=(
                f"0/1 knapsack is the textbook DP problem: it has overlapping "
                f"sub-problems (the same (i, w) cell is reused across many "
                f"recursive calls) and clean optimal sub-structure. With n="
                f"{spec.n} the table fits comfortably in memory, so we fill it "
                f"bottom-up and back-track for the exact optimum."
            ),
            expected_complexity="O(n * W)  where W is capacity",
            quality_guarantee="exact",
            trace=trace,
        )

    # 4) too big for DP, no greedy module -> warn the user
    trace.append(DecisionStep(
        question=f"Is n within the DP table limit (n <= {DP_N_LIMIT})?",
        answer=f"no (n={spec.n})",
        branch="too-big",
    ))
    return Selection(
        algorithm="knapsack_dp",   # we still try, but flag it
        justification=(
            f"n={spec.n} is above the recommended DP threshold ({DP_N_LIMIT}). "
            f"We still run DP because no greedy 0/1 knapsack module is wired "
            f"up yet, but expect heavy memory use. Consider lowering n."
        ),
        expected_complexity="O(n * W)",
        quality_guarantee="exact (but slow for large n)",
        trace=trace,
    )


def _select_routing(spec: ProblemSpec) -> Selection:
    trace: list[DecisionStep] = []
    trace.append(DecisionStep(
        question="What is the problem type?",
        answer="routing",
        branch="routing",
    ))

    # negative weights kill dijkstra. if we had bellman-ford we'd route there;
    # for now we reject and let the API layer surface a clean error.
    if spec.has_negative_weights:
        trace.append(DecisionStep(
            question="Are any edge weights negative?",
            answer="yes",
            branch="negative-edges",
        ))
        # TODO: add Bellman-Ford (DP-flavoured) when negative weights appear.
        # spec mentions DP for "shortest path with negative weights" but we
        # don't have that solver yet. surface a meaningful error instead.
        return Selection(
            algorithm="unsupported",
            justification=(
                "Edge weights include negatives. Dijkstra's greedy choice is "
                "unsafe here (a longer path could later be shortened by a "
                "negative edge). A Bellman-Ford / DP solver is the right "
                "answer but isn't implemented yet."
            ),
            expected_complexity="n/a",
            quality_guarantee="n/a",
            trace=trace,
        )

    trace.append(DecisionStep(
        question="Are any edge weights negative?",
        answer="no",
        branch="non-negative",
    ))

    # very small graph + explicit exact request -> use brute force routing
    if spec.n <= BRUTE_FORCE_ROUTING_LIMIT and spec.quality == "exact" and spec.n <= 6:
        trace.append(DecisionStep(
            question=f"Is the graph tiny enough for exhaustive routing (nodes <= 6)?",
            answer=f"yes (n={spec.n})",
            branch="tiny-graph",
        ))
        return Selection(
            algorithm="brute_force_routing",
            justification=(
                f"Graph is small (n={spec.n} nodes) and exact distances were "
                f"requested. Enumerating every permutation of intermediate "
                f"nodes gives a ground-truth answer we can compare Dijkstra "
                f"against."
            ),
            expected_complexity="O(n!)",
            quality_guarantee="exact",
            trace=trace,
        )

    # default for routing: dijkstra. it's the spec's chosen greedy.
    trace.append(DecisionStep(
        question="Is a known greedy-optimal solver available for this case?",
        answer="yes (Dijkstra on non-negative weights)",
        branch="greedy-fits",
    ))
    return Selection(
        algorithm="dijkstra_greedy",
        justification=(
            "All edge weights are non-negative, which makes Dijkstra's local "
            "choice — always relax the closest unsettled node — provably "
            "optimal. We get every shortest path from the source in "
            "O((V + E) log V) using a binary heap."
        ),
        expected_complexity="O((V + E) log V)",
        quality_guarantee="exact (optimal greedy choice on non-negative graphs)",
        trace=trace,
    )


def _select_sorting(spec: ProblemSpec) -> Selection:
    trace: list[DecisionStep] = []
    trace.append(DecisionStep(
        question="What is the problem type?",
        answer="sorting",
        branch="sorting",
    ))

    # tiny + user wants a correctness check -> permutation sort
    if spec.n <= BRUTE_FORCE_SORT_LIMIT and spec.quality == "exact" and spec.n <= 6:
        trace.append(DecisionStep(
            question="Is n tiny enough for permutation-based sort (n <= 6)?",
            answer=f"yes (n={spec.n})",
            branch="tiny-sort",
        ))
        return Selection(
            algorithm="brute_force_sort",
            justification=(
                f"n={spec.n} is small enough to try every permutation. This is "
                f"only useful as a teaching / verification aid — merge sort "
                f"would still finish faster — but it satisfies the explicit "
                f"correctness check."
            ),
            expected_complexity="O(n!)",
            quality_guarantee="exact",
            trace=trace,
        )

    # default: merge sort. independent halves -> classic D&C territory.
    trace.append(DecisionStep(
        question="Do sub-problems overlap?",
        answer="no — sorting halves are independent",
        branch="independent-halves",
    ))
    return Selection(
        algorithm="merge_sort",
        justification=(
            "Sorting splits cleanly into two independent halves which are "
            "sorted recursively and merged in linear time. Sub-problems do "
            "not overlap, so divide & conquer beats DP here."
        ),
        expected_complexity="O(n log n)",
        quality_guarantee="exact (stable sort)",
        trace=trace,
    )


def _select_search(spec: ProblemSpec) -> Selection:
    trace: list[DecisionStep] = []
    trace.append(DecisionStep(
        question="What is the problem type?",
        answer="search",
        branch="search",
    ))

    if not spec.is_sorted:
        trace.append(DecisionStep(
            question="Is the input sorted?",
            answer="no",
            branch="unsorted",
        ))
        return Selection(
            algorithm="brute_force_search",
            justification=(
                "Input is not sorted, so binary search would be unsafe. We "
                "fall back to a linear scan — O(n) but correct on any input."
            ),
            expected_complexity="O(n)",
            quality_guarantee="exact",
            trace=trace,
        )

    trace.append(DecisionStep(
        question="Is the input sorted?",
        answer="yes",
        branch="sorted",
    ))
    return Selection(
        algorithm="binary_search",
        justification=(
            "The array is sorted, so we can halve the search window each step "
            "via divide & conquer. This is the canonical example of "
            "independent sub-problems with no overlap."
        ),
        expected_complexity="O(log n)",
        quality_guarantee="exact",
        trace=trace,
    )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _brute_force_path(spec: ProblemSpec, *, reason: str) -> Selection:
    """Common brute-force selection when the user forces it."""
    family_to_algo = {
        "knapsack": ("brute_force_knapsack", "O(2^n * n)"),
        "routing": ("brute_force_routing", "O(n!)"),
        "sorting": ("brute_force_sort", "O(n!)"),
        "search": ("brute_force_search", "O(n)"),
    }
    algo, complexity = family_to_algo[spec.problem_type]
    return Selection(
        algorithm=algo,
        justification=(
            f"Brute force selected because {reason}. The result is exact and "
            f"useful for sanity-checking other algorithms, but the runtime is "
            f"prohibitive on larger inputs."
        ),
        expected_complexity=complexity,
        quality_guarantee="exact",
        trace=[DecisionStep(
            question="Was brute force explicitly requested?",
            answer="yes",
            branch="forced",
        )],
    )


# ---------------------------------------------------------------------------
# helper for the API: convert dataclasses to plain dicts for JSON
# ---------------------------------------------------------------------------

def selection_to_dict(sel: Selection) -> dict[str, Any]:
    return {
        "algorithm": sel.algorithm,
        "justification": sel.justification,
        "expected_complexity": sel.expected_complexity,
        "quality_guarantee": sel.quality_guarantee,
        "trace": [
            {"question": s.question, "answer": s.answer, "branch": s.branch}
            for s in sel.trace
        ],
    }
