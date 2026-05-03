"""
Divide & Conquer family.

Three solvers in here, each picked based on the problem_type the engine
hands us:
    - merge_sort        for sorting
    - binary_search     for searching a sorted array
    - fast_exponent     for raising a number to an integer power

D&C fits when sub-problems are independent (no overlap). If they overlapped
we'd be looking at DP instead — that's the routing the engine does.

Each solver tracks the recursion tree (depth + sub-problem sizes per level)
and returns it in the trace so the UI can visualize the splits.
"""

from __future__ import annotations

from typing import Any

from .common import AlgoResult, Timer


# ---------------------------------------------------------------------------
# merge sort
# ---------------------------------------------------------------------------

def merge_sort(arr: list[int]) -> AlgoResult:
    # we record sub-problem sizes per recursion depth as we go
    levels: dict[int, list[int]] = {}
    max_depth = [0]   # mutable single-element list so the inner fn can write

    def _sort(a: list[int], depth: int) -> list[int]:
        levels.setdefault(depth, []).append(len(a))
        if depth > max_depth[0]:
            max_depth[0] = depth
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left = _sort(a[:mid], depth + 1)
        right = _sort(a[mid:], depth + 1)
        return _merge(left, right)

    def _merge(l: list[int], r: list[int]) -> list[int]:
        out: list[int] = []
        i = j = 0
        # two-pointer merge, picks the smaller head each step
        while i < len(l) and j < len(r):
            if l[i] <= r[j]:
                out.append(l[i]); i += 1
            else:
                out.append(r[j]); j += 1
        # whichever side has leftovers gets dumped on the end
        out.extend(l[i:])
        out.extend(r[j:])
        return out

    with Timer() as t:
        sorted_arr = _sort(list(arr), 0)

    return AlgoResult(
        algorithm="merge_sort",
        problem_type="sorting",
        solution={"sorted": sorted_arr},
        # for sorting "value" doesn't really mean much, just use input length.
        # the comparison table cares more about runtime here.
        value=float(len(sorted_arr)),
        runtime_ms=t.ms,
        trace={
            "recursion_depth": max_depth[0],
            "subproblem_sizes_by_level": {
                str(k): v for k, v in sorted(levels.items())
            },
        },
        note="Stable O(n log n) sort; deterministic regardless of input order.",
    )


# ---------------------------------------------------------------------------
# binary search
# ---------------------------------------------------------------------------

def binary_search(arr: list[int], target: int) -> AlgoResult:
    # input must already be sorted — caller's job. we don't re-sort silently.
    steps: list[dict[str, int]] = []

    with Timer() as t:
        lo, hi = 0, len(arr) - 1
        found = -1
        depth = 0
        while lo <= hi:
            depth += 1
            mid = (lo + hi) // 2
            steps.append({"lo": lo, "hi": hi, "mid": mid, "value": arr[mid]})
            if arr[mid] == target:
                found = mid
                break
            if arr[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1

    return AlgoResult(
        algorithm="binary_search",
        problem_type="search",
        solution={"index": found, "target": target},
        value=float(found),
        runtime_ms=t.ms,
        trace={
            "recursion_depth": depth,
            "steps": steps,
            "n": len(arr),
        },
        note="Halves the search window each step; assumes input is sorted.",
    )


# ---------------------------------------------------------------------------
# fast exponentiation (binary exponentiation)
# ---------------------------------------------------------------------------

def fast_exponent(base: float, exp: int) -> AlgoResult:
    # negative exponents become a final reciprocal
    if exp < 0:
        flip = True
        exp = -exp
    else:
        flip = False

    levels: list[dict[str, Any]] = []

    def _pow(b: float, e: int, depth: int) -> float:
        levels.append({"depth": depth, "base": b, "exp": e})
        if e == 0:
            return 1.0
        half = _pow(b, e // 2, depth + 1)
        # square the half-result, multiply once more if exponent was odd
        if e % 2 == 0:
            return half * half
        return half * half * b

    with Timer() as t:
        result = _pow(base, exp, 0)
        if flip:
            result = 1.0 / result

    return AlgoResult(
        algorithm="fast_exponent",
        problem_type="exponent",
        solution={"result": result, "base": base, "exp": exp if not flip else -exp},
        value=float(result),
        runtime_ms=t.ms,
        trace={
            "recursion_depth": max((lvl["depth"] for lvl in levels), default=0),
            "levels": levels,
        },
        note="O(log n) multiplications via repeated squaring.",
    )
