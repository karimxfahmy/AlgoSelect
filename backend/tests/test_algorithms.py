"""
Sanity tests for each algorithm module.

These are not exhaustive — they're the kind of tests I write while building
to make sure I didn't break the obvious cases. Edge cases (empty inputs,
huge inputs) probably deserve more attention later.
"""

from app.algorithms import (
    knapsack_dp,
    dijkstra_greedy,
    divide_conquer,
    brute_force,
)


# ---------- knapsack ----------

def test_knapsack_dp_classic():
    # textbook example
    res = knapsack_dp.solve(weights=[2, 3, 4, 5], values=[3, 4, 5, 6], capacity=5)
    assert res.solution["value"] == 7
    # items 0 (w=2,v=3) + 1 (w=3,v=4) = w 5, v 7. nothing else fits at cap 5.
    assert sorted(res.solution["items"]) == [0, 1]


def test_knapsack_dp_matches_brute_force():
    # if these ever diverge, one of them is wrong
    weights = [3, 1, 4, 1, 5, 9, 2]
    values = [6, 1, 7, 1, 8, 12, 3]
    cap = 10
    dp_res = knapsack_dp.solve(weights, values, cap)
    bf_res = brute_force.knapsack(weights, values, cap)
    assert dp_res.solution["value"] == bf_res.solution["value"]


# ---------- dijkstra ----------

def test_dijkstra_simple_undirected():
    g = {
        "nodes": ["A", "B", "C", "D"],
        "edges": [
            {"u": "A", "v": "B", "w": 1},
            {"u": "B", "v": "C", "w": 2},
            {"u": "A", "v": "C", "w": 5},
            {"u": "C", "v": "D", "w": 1},
        ],
        "source": "A",
    }
    res = dijkstra_greedy.solve(g)
    d = res.solution["distances"]
    assert d["A"] == 0
    assert d["B"] == 1
    assert d["C"] == 3
    assert d["D"] == 4


def test_dijkstra_rejects_negative():
    g = {
        "nodes": ["A", "B"],
        "edges": [{"u": "A", "v": "B", "w": -1}],
        "source": "A",
    }
    try:
        dijkstra_greedy.solve(g)
    except ValueError:
        return
    assert False, "expected ValueError on negative edge"


# ---------- divide & conquer ----------

def test_merge_sort_sorts_random():
    arr = [5, 2, 8, 1, 9, 3, 7, 4, 6]
    res = divide_conquer.merge_sort(arr)
    assert res.solution["sorted"] == sorted(arr)


def test_binary_search_hits():
    arr = list(range(0, 100, 2))   # 0, 2, 4, ... 98
    res = divide_conquer.binary_search(arr, 42)
    assert res.solution["index"] == 21


def test_binary_search_misses():
    arr = list(range(0, 100, 2))
    res = divide_conquer.binary_search(arr, 43)
    assert res.solution["index"] == -1


def test_fast_exponent_matches_pow():
    res = divide_conquer.fast_exponent(2, 10)
    assert res.solution["result"] == 1024


def test_fast_exponent_negative():
    res = divide_conquer.fast_exponent(2, -3)
    assert abs(res.solution["result"] - 0.125) < 1e-9


# ---------- brute force ----------

def test_brute_force_routing_matches_dijkstra():
    g = {
        "nodes": ["A", "B", "C", "D"],
        "edges": [
            {"u": "A", "v": "B", "w": 2},
            {"u": "B", "v": "C", "w": 1},
            {"u": "A", "v": "C", "w": 4},
            {"u": "C", "v": "D", "w": 3},
        ],
        "source": "A",
    }
    dj = dijkstra_greedy.solve(g)
    bf = brute_force.routing(g)
    # both should agree on every distance
    for n in g["nodes"]:
        assert dj.solution["distances"][n] == bf.solution["distances"][n]
