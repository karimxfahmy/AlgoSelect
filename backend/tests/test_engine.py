"""
Tests for the rule-based selector and the experiment runner.

These exist mostly to make sure I don't accidentally break a routing rule
when I add new ones later. They check the *picked algorithm*, not the
phrasing of the justification (that's allowed to change).
"""

from app.engine.selector import ProblemSpec, select
from app.engine.runner import run_one, run_experiment


# ---------- selector ----------

def test_knapsack_default_picks_dp():
    sel = select(ProblemSpec(problem_type="knapsack", n=50, time_budget_ms=1000))
    assert sel.algorithm == "knapsack_dp"
    assert "DP" in sel.justification or "dp" in sel.justification.lower()


def test_knapsack_tiny_exact_picks_brute_force():
    sel = select(ProblemSpec(
        problem_type="knapsack", n=10, time_budget_ms=1000, quality="exact"
    ))
    assert sel.algorithm == "brute_force_knapsack"


def test_routing_default_picks_dijkstra():
    sel = select(ProblemSpec(problem_type="routing", n=20, time_budget_ms=500))
    assert sel.algorithm == "dijkstra_greedy"


def test_routing_with_negative_weights_is_unsupported():
    sel = select(ProblemSpec(
        problem_type="routing", n=5, time_budget_ms=500,
        has_negative_weights=True,
    ))
    assert sel.algorithm == "unsupported"


def test_sorting_default_picks_merge_sort():
    sel = select(ProblemSpec(problem_type="sorting", n=100, time_budget_ms=200))
    assert sel.algorithm == "merge_sort"


def test_search_unsorted_picks_linear():
    sel = select(ProblemSpec(
        problem_type="search", n=100, time_budget_ms=200, is_sorted=False
    ))
    assert sel.algorithm == "brute_force_search"


def test_search_sorted_picks_binary():
    sel = select(ProblemSpec(
        problem_type="search", n=100, time_budget_ms=200, is_sorted=True
    ))
    assert sel.algorithm == "binary_search"


def test_force_brute_force_wins():
    sel = select(ProblemSpec(
        problem_type="knapsack", n=200, time_budget_ms=10000,
        force_brute_force=True,
    ))
    assert sel.algorithm == "brute_force_knapsack"


def test_decision_trace_is_populated():
    sel = select(ProblemSpec(problem_type="routing", n=10, time_budget_ms=500))
    assert len(sel.trace) >= 2  # type check + greedy-fits check


# ---------- runner ----------

def test_run_one_knapsack_dp():
    res = run_one("knapsack_dp", {
        "weights": [2, 3, 4, 5],
        "values": [3, 4, 5, 6],
        "capacity": 5,
    })
    assert res.solution["value"] == 7


def test_run_experiment_knapsack_ranks_correctly():
    out = run_experiment("knapsack", {
        "weights": [1, 2, 3, 4],
        "values":  [1, 4, 5, 7],
        "capacity": 6,
    })
    finished = [r for r in out["ranked"] if not r.get("skipped")]
    # both algorithms should agree on the optimum
    assert len({r["value"] for r in finished}) == 1
    # both should report ratio 1.0 against the best
    for r in finished:
        assert r["approximation_ratio"] == 1.0


def test_run_experiment_skips_brute_force_when_too_big():
    # 21 items is one over the brute-force cap
    weights = [1] * 21
    values = [1] * 21
    out = run_experiment("knapsack", {
        "weights": weights, "values": values, "capacity": 5,
    })
    skipped = [r for r in out["ranked"] if r.get("skipped")]
    assert any(r["algorithm"] == "brute_force_knapsack" for r in skipped)


def test_run_experiment_routing_matches_between_algos():
    g = {
        "nodes": ["A", "B", "C", "D"],
        "edges": [
            {"u": "A", "v": "B", "w": 1},
            {"u": "B", "v": "C", "w": 2},
            {"u": "C", "v": "D", "w": 1},
            {"u": "A", "v": "D", "w": 10},
        ],
        "source": "A",
    }
    out = run_experiment("routing", {"graph": g})
    finished = [r for r in out["ranked"] if not r.get("skipped")]
    # dijkstra and brute-force should agree on the total
    assert len({r["value"] for r in finished}) == 1
