"""
0/1 knapsack solved with the classic bottom-up DP table.

The DP recurrence is the standard one:
    dp[i][w] = max value using items 0..i-1 with capacity w
    dp[i][w] = dp[i-1][w]                              if weight[i-1] > w
             = max(dp[i-1][w],
                   dp[i-1][w - weight[i-1]] + value[i-1])  otherwise

After filling the table we backtrack to figure out which items were taken.
We return the table itself in the trace so the UI can render it.

Note: only practical when n * capacity is small enough to fit in memory.
The selector enforces that — this module assumes the inputs are sane.
"""

from __future__ import annotations

from typing import Any

from .common import AlgoResult, Timer


def solve(
    weights: list[int],
    values: list[int],
    capacity: int,
) -> AlgoResult:
    n = len(weights)
    if len(values) != n:
        raise ValueError("weights and values must have the same length")
    if capacity < 0:
        raise ValueError("capacity must be >= 0")

    with Timer() as t:
        # dp is (n+1) by (capacity+1). Row 0 is the base case (no items).
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            wi = weights[i - 1]
            vi = values[i - 1]
            for w in range(capacity + 1):
                # default: don't take item i-1
                best = dp[i - 1][w]
                # try taking it if it fits
                if wi <= w:
                    take = dp[i - 1][w - wi] + vi
                    if take > best:
                        best = take
                dp[i][w] = best

        # backtrack to recover which items we kept
        chosen: list[int] = []
        w = capacity
        for i in range(n, 0, -1):
            # if the cell differs from the row above, item i-1 was taken
            if dp[i][w] != dp[i - 1][w]:
                chosen.append(i - 1)
                w -= weights[i - 1]
        chosen.reverse()

    optimal_value = dp[n][capacity]

    # we only ship the full table back when it's small. for big tables we
    # just send the last row + a downsampled version so the UI doesn't choke.
    # TODO: tune the size limit if the front-end starts to lag
    table_payload: Any
    if (n + 1) * (capacity + 1) <= 5000:
        table_payload = dp
    else:
        table_payload = {"truncated": True, "last_row": dp[n]}

    return AlgoResult(
        algorithm="knapsack_dp",
        problem_type="knapsack",
        solution={
            "value": optimal_value,
            "items": chosen,
            "weight_used": sum(weights[i] for i in chosen),
        },
        value=float(optimal_value),
        runtime_ms=t.ms,
        trace={
            "dp_table": table_payload,
            "n": n,
            "capacity": capacity,
            "cells_filled": (n + 1) * (capacity + 1),
        },
        note="Exact optimum via bottom-up DP.",
    )
