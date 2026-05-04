"""
Brute force solvers — for verifying correctness on tiny inputs.

These are deliberately the dumbest possible implementations. We use them
as ground truth so the engine can compute an approximation ratio for the
greedy / DP results when the input is small enough.

Hard ceilings (also enforced by the selector):
    - knapsack:   n <= 20   (2^n subsets)
    - routing:    nodes <= 8 (n! permutations of visit order — TSP-style)
    - search:     n <= 1000 (linear scan, basically free)
    - sorting:    n <= 8     (try every permutation, mostly a teaching tool)
    - exponent:   exp <= 1_000_000 (linear repeated multiplication)

Anything bigger and we refuse — the engine should not have routed here.
"""

from __future__ import annotations

from itertools import permutations
from typing import Any

from .common import AlgoResult, Timer


# ---------------------------------------------------------------------------
# knapsack — try every subset
# ---------------------------------------------------------------------------

def knapsack(weights: list[int], values: list[int], capacity: int) -> AlgoResult:
    n = len(weights)
    if n > 20:
        # 2^20 is already a million subsets, beyond that the user is asking
        # for trouble. fail fast rather than hang.
        raise ValueError("brute force knapsack capped at n=20")

    states = 0
    best_val = 0
    best_mask = 0

    with Timer() as t:
        # iterate every bitmask. bit i set means item i is in the bag.
        for mask in range(1 << n):
            states += 1
            w = 0
            v = 0
            for i in range(n):
                if mask & (1 << i):
                    w += weights[i]
                    v += values[i]
            if w <= capacity and v > best_val:
                best_val = v
                best_mask = mask

    chosen = [i for i in range(n) if best_mask & (1 << i)]

    return AlgoResult(
        algorithm="brute_force_knapsack",
        problem_type="knapsack",
        solution={
            "value": best_val,
            "items": chosen,
            "weight_used": sum(weights[i] for i in chosen),
        },
        value=float(best_val),
        runtime_ms=t.ms,
        trace={
            "states_evaluated": states,
            "n": n,
            "warning": "Brute force is exponential — only safe for tiny inputs.",
        },
        note="Exact optimum by enumerating all 2^n subsets.",
    )


# ---------------------------------------------------------------------------
# routing — try every permutation (Hamiltonian path style, single source)
# ---------------------------------------------------------------------------

def routing(graph: dict[str, Any]) -> AlgoResult:
    nodes: list[str] = list(graph["nodes"])
    edges: list[dict[str, Any]] = graph["edges"]
    source: str = graph["source"]
    directed: bool = bool(graph.get("directed", False))

    n = len(nodes)
    if n > 8:
        raise ValueError("brute force routing capped at 8 nodes")

    # build distance matrix; missing edges = inf
    INF = float("inf")
    idx = {name: i for i, name in enumerate(nodes)}
    dmat = [[INF] * n for _ in range(n)]
    for i in range(n):
        dmat[i][i] = 0
    for e in edges:
        u, v, w = idx[e["u"]], idx[e["v"]], float(e["w"])
        dmat[u][v] = min(dmat[u][v], w)
        if not directed:
            dmat[v][u] = min(dmat[v][u], w)

    src = idx[source]
    others = [i for i in range(n) if i != src]
    states = 0

    # for each destination we find the shortest path by trying every
    # permutation of the intermediate nodes. very expensive, but it gives
    # us a ground-truth answer to compare dijkstra against.
    best_dist: dict[str, float] = {nodes[src]: 0.0}
    best_path: dict[str, list[str]] = {nodes[src]: [nodes[src]]}

    with Timer() as t:
        for dest in others:
            mids_pool = [m for m in others if m != dest]
            best = INF
            best_seq: list[int] = []
            # try all subset sizes 0..len(mids_pool) and all orderings
            for k in range(len(mids_pool) + 1):
                for perm in permutations(mids_pool, k):
                    states += 1
                    seq = [src, *perm, dest]
                    total = 0.0
                    ok = True
                    for a, b in zip(seq, seq[1:]):
                        if dmat[a][b] == INF:
                            ok = False
                            break
                        total += dmat[a][b]
                    if ok and total < best:
                        best = total
                        best_seq = seq
            best_dist[nodes[dest]] = best if best != INF else None  # type: ignore
            best_path[nodes[dest]] = [nodes[i] for i in best_seq] if best_seq else []

    total_obj = sum(v for v in best_dist.values() if v not in (None, INF))

    return AlgoResult(
        algorithm="brute_force_routing",
        problem_type="routing",
        solution={
            "distances": best_dist,
            "paths": best_path,
            "source": source,
        },
        value=float(total_obj),
        runtime_ms=t.ms,
        trace={
            "states_evaluated": states,
            "n_nodes": n,
            "warning": "Permutation search; infeasible past ~10 nodes.",
        },
        note="Exact shortest paths via exhaustive permutation search.",
    )


# ---------------------------------------------------------------------------
# search — linear scan (the brute force version of binary search)
# ---------------------------------------------------------------------------

def linear_search(arr: list[int], target: int) -> AlgoResult:
    states = 0
    found = -1

    with Timer() as t:
        for i, x in enumerate(arr):
            states += 1
            if x == target:
                found = i
                break

    return AlgoResult(
        algorithm="brute_force_search",
        problem_type="search",
        solution={"index": found, "target": target},
        value=float(found),
        runtime_ms=t.ms,
        trace={"states_evaluated": states, "n": len(arr)},
        note="Linear scan — works on unsorted input but slower than binary search.",
    )


# ---------------------------------------------------------------------------
# sorting — try every permutation. ridiculous, but it's a real brute force.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# exponent — naive repeated multiplication. the obvious O(n) baseline
# ---------------------------------------------------------------------------

def naive_exponent(base: float, exp: int) -> AlgoResult:
    # negative exp -> compute the positive power, flip at the end
    if exp < 0:
        flip = True
        exp = -exp
    else:
        flip = False

    if exp > 1_000_000:
        # at this point even the linear loop starts to drag. fast_exponent
        # would handle it in microseconds; refuse here to keep things honest.
        raise ValueError("naive exponent capped at exp=1_000_000")

    states = 0
    result = 1.0

    with Timer() as t:
        for _ in range(exp):
            result *= base
            states += 1
        if flip:
            result = 1.0 / result

    return AlgoResult(
        algorithm="naive_exponent",
        problem_type="exponent",
        solution={"result": result, "base": base, "exp": exp if not flip else -exp},
        value=float(result),
        runtime_ms=t.ms,
        trace={
            "states_evaluated": states,
            "warning": "Linear in exp; fast exponentiation does it in O(log exp).",
        },
        note="Multiplies one factor at a time — the obvious O(n) baseline.",
    )


def permutation_sort(arr: list[int]) -> AlgoResult:
    n = len(arr)
    if n > 8:
        raise ValueError("brute force sort capped at n=8")

    states = 0
    best: list[int] = list(arr)

    with Timer() as t:
        for perm in permutations(arr):
            states += 1
            ok = True
            for a, b in zip(perm, perm[1:]):
                if a > b:
                    ok = False
                    break
            if ok:
                best = list(perm)
                break

    return AlgoResult(
        algorithm="brute_force_sort",
        problem_type="sorting",
        solution={"sorted": best},
        value=float(n),
        runtime_ms=t.ms,
        trace={
            "states_evaluated": states,
            "warning": "O(n!) — only kept around for correctness checks.",
        },
        note="Tries every permutation until a sorted one is found.",
    )
