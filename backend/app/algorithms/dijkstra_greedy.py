"""
Dijkstra's shortest-path algorithm — the greedy classic.

Greedy works here because every edge weight is non-negative, so once a
vertex is popped from the min-heap with a tentative distance d, no shorter
path can ever be found later. That's the property that makes the local
choice (always extend the closest unvisited node) safe.

Graph format we accept:
    {
        "nodes": ["A", "B", "C"],
        "edges": [
            {"u": "A", "v": "B", "w": 5},
            ...
        ],
        "source": "A",
        "directed": false      # optional, defaults to false
    }

We return distances + the actual paths (reconstructed from predecessors)
so the UI can draw them. If the graph has a negative edge we raise — the
selector should never have picked us in that case, but better safe.
"""

from __future__ import annotations

import heapq
from typing import Any

from .common import AlgoResult, Timer


def solve(graph: dict[str, Any]) -> AlgoResult:
    nodes: list[str] = list(graph["nodes"])
    edges: list[dict[str, Any]] = graph["edges"]
    source: str = graph["source"]
    directed: bool = bool(graph.get("directed", False))

    if source not in nodes:
        raise ValueError(f"source {source!r} not in nodes list")

    # build an adjacency list. doing it once up front keeps the main loop tidy.
    adj: dict[str, list[tuple[str, float]]] = {n: [] for n in nodes}
    for e in edges:
        u, v, w = e["u"], e["v"], float(e["w"])
        if w < 0:
            # dijkstra silently fails on negative edges, so refuse loudly
            raise ValueError("dijkstra cannot handle negative edge weights")
        adj[u].append((v, w))
        if not directed:
            adj[v].append((u, w))

    INF = float("inf")
    dist: dict[str, float] = {n: INF for n in nodes}
    prev: dict[str, str | None] = {n: None for n in nodes}
    dist[source] = 0.0

    # heap holds (current_best_distance, node). standard trick.
    heap: list[tuple[float, str]] = [(0.0, source)]
    visit_order: list[str] = []          # for the trace / animation
    settled: set[str] = set()

    with Timer() as t:
        while heap:
            d, u = heapq.heappop(heap)
            if u in settled:
                # stale entry left over from a relaxation. skip it.
                continue
            settled.add(u)
            visit_order.append(u)

            for v, w in adj[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))

    # rebuild paths from predecessor pointers
    paths: dict[str, list[str]] = {}
    for n in nodes:
        if dist[n] == INF:
            paths[n] = []
            continue
        chain: list[str] = []
        cur: str | None = n
        while cur is not None:
            chain.append(cur)
            cur = prev[cur]
        chain.reverse()
        paths[n] = chain

    # JSON cannot represent inf, so swap to None on the wire
    safe_dist = {k: (None if v == INF else v) for k, v in dist.items()}

    # objective value = sum of finite distances. lower is better for routing.
    total = sum(v for v in dist.values() if v != INF)

    return AlgoResult(
        algorithm="dijkstra_greedy",
        problem_type="routing",
        solution={
            "distances": safe_dist,
            "paths": paths,
            "source": source,
        },
        value=float(total),
        runtime_ms=t.ms,
        trace={
            "visit_order": visit_order,
            "settled_count": len(settled),
            "edge_count": len(edges),
        },
        note="Greedy choice is optimal because all edge weights are non-negative.",
    )
