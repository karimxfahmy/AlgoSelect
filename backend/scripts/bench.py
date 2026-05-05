"""
Tiny benchmark script that produces the numbers used in the comparison
report. Run from the backend folder:

    python scripts/bench.py

Not a real benchmark suite — single runs, no warm-up. Good enough for the
report and for spotting big regressions.
"""

import sys
from pathlib import Path

# add the backend dir to sys.path so `app.*` imports resolve when the
# script is launched directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import random
from app.engine.runner import run_experiment


def gen_knapsack(n, seed=1):
    rng = random.Random(seed)
    weights = [rng.randint(1, 10) for _ in range(n)]
    values = [rng.randint(1, 20) for _ in range(n)]
    cap = sum(weights) // 2
    return {"weights": weights, "values": values, "capacity": cap}


def gen_routing(n, seed=2):
    rng = random.Random(seed)
    nodes = [chr(65 + i) for i in range(n)]
    edges = []
    # ring + a few random shortcuts
    for i in range(n):
        edges.append({"u": nodes[i], "v": nodes[(i + 1) % n], "w": rng.randint(1, 9)})
    for _ in range(n // 2):
        a, b = rng.sample(range(n), 2)
        edges.append({"u": nodes[a], "v": nodes[b], "w": rng.randint(1, 9)})
    return {"nodes": nodes, "edges": edges, "source": nodes[0], "directed": False}


def report():
    print("=" * 64)
    print("Knapsack — DP vs Brute Force")
    print("=" * 64)
    for n in (5, 10, 15, 18):
        out = run_experiment("knapsack", gen_knapsack(n))
        print(f"\nn = {n}")
        for r in out["ranked"]:
            if r.get("skipped"):
                print(f"  {r['algorithm']:25s}  skipped ({r['reason']})")
            else:
                print(f"  {r['algorithm']:25s}  value={r['value']:6.0f}  "
                      f"runtime={r['runtime_ms']:8.4f}ms  "
                      f"ratio={r['approximation_ratio']}")

    print("\n" + "=" * 64)
    print("Routing — Dijkstra vs Brute Force")
    print("=" * 64)
    for n in (4, 6, 8):
        out = run_experiment("routing", {"graph": gen_routing(n)})
        print(f"\nnodes = {n}")
        for r in out["ranked"]:
            if r.get("skipped"):
                print(f"  {r['algorithm']:25s}  skipped ({r['reason']})")
            else:
                print(f"  {r['algorithm']:25s}  total={r['value']:6.1f}  "
                      f"runtime={r['runtime_ms']:8.4f}ms  "
                      f"ratio={r['approximation_ratio']}")


if __name__ == "__main__":
    report()
