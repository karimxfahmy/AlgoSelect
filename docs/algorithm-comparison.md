# Algorithm Comparison Report

This is a small empirical look at how the four algorithm families behave on
the same problem instances. Numbers come from `backend/scripts/bench.py`,
single runs on a Windows laptop, no warm-up. Take the absolute timings with
a grain of salt — what matters is the *shape*.

## How to reproduce

```bash
cd backend
python scripts/bench.py
```

## Knapsack — DP vs Brute Force

Both algorithms are exact, so the value column is identical and the
approximation ratio is always `1.0`. Only the runtime moves.

| n  | DP runtime | Brute runtime | Brute / DP slowdown |
| -- | ---------- | ------------- | ------------------- |
| 5  | 0.015 ms   | 0.014 ms      | ~1×                 |
| 10 | 0.033 ms   | 0.55 ms       | ~17×                |
| 15 | 0.057 ms   | 25.2 ms       | ~440×               |
| 18 | 0.085 ms   | 247 ms        | ~2900×              |

**Takeaway.** Brute force is briefly competitive at `n = 5` (the DP table
itself has overhead) and then collapses. By `n = 18` the gap is roughly
three orders of magnitude. This is the curve the selector relies on: if `n
≤ 15` and the user wants *exact*, brute force is still tolerable; past
that, DP is the only sane choice.

## Routing — Dijkstra vs Brute Force

Same story: both exact, only runtime differs. Brute force here means
"enumerate every permutation of intermediate nodes for every destination".

| nodes | Dijkstra runtime | Brute runtime | Brute / Dijkstra slowdown |
| ----- | ---------------- | ------------- | ------------------------- |
| 4     | 0.008 ms         | 0.019 ms      | ~2×                       |
| 6     | 0.004 ms         | 0.118 ms      | ~30×                      |
| 8     | 0.005 ms         | 4.09 ms       | ~770×                     |

**Takeaway.** Dijkstra's runtime barely moves with the small graph sizes
shown. Brute force grows as `O(n!)` per destination. Eight nodes is
already enough that the comparison is one-sided; the engine caps brute
force at `n ≤ 8` for exactly this reason.

## Sorting — Merge Sort vs Permutation Sort

Permutation sort (`O(n!)`) is included only as a teaching tool. For any
`n > 8` the experiment runner skips it cleanly. Merge sort is `O(n log n)`
and stable. There's no meaningful "value" column for sorting — both
algorithms produce the same sorted array, so the comparison is purely
about runtime.

## Search — Binary Search vs Linear Scan

Binary search is the obvious win when the input is sorted. The selector
checks the `is_sorted` flag and falls back to linear scan when it isn't,
so we never call binary search on input that would silently mis-behave.

| n     | Binary search | Linear scan |
| ----- | ------------- | ----------- |
| 1 000 | ~0.005 ms     | ~0.05 ms    |

(Numbers vary; both are essentially free at this size.)

## What the engine does with this

The thresholds in `app/engine/selector.py` (`DP_N_LIMIT`,
`BRUTE_FORCE_KNAPSACK_LIMIT`, etc.) are tuned against the curves above.
They aren't magic numbers — they're the rough crossover points where one
algorithm starts to make the other look silly.

If you change the algorithms (e.g. add a knapsack-greedy with a known
approximation bound), redo this report and re-tune the thresholds.
