"""
Minimal HTTP-level checks for the FastAPI app.

Uses fastapi.testclient (which under the hood uses httpx). These exist
mainly so a regression in the request/response schemas fails loudly
instead of only showing up in the browser.
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_algorithms_listing():
    r = client.get("/api/algorithms")
    assert r.status_code == 200
    body = r.json()
    assert "knapsack" in body
    assert "knapsack_dp" in body["knapsack"]


def test_solve_knapsack():
    r = client.post("/api/solve", json={
        "spec": {
            "problem_type": "knapsack",
            "n": 4, "time_budget_ms": 500, "quality": "best-effort",
        },
        "payload": {
            "weights": [2, 3, 4, 5],
            "values": [3, 4, 5, 6],
            "capacity": 5,
        },
    })
    assert r.status_code == 200
    body = r.json()
    assert body["selection"]["algorithm"] == "knapsack_dp"
    assert body["result"]["solution"]["value"] == 7


def test_solve_unsupported_returns_clean_error():
    # negative weights -> selector marks unsupported, API returns 200 with
    # an error string rather than a 500
    r = client.post("/api/solve", json={
        "spec": {
            "problem_type": "routing",
            "n": 3, "time_budget_ms": 100,
            "has_negative_weights": True,
        },
        "payload": {
            "graph": {
                "nodes": ["A", "B"],
                "edges": [{"u": "A", "v": "B", "w": -1}],
                "source": "A",
            },
        },
    })
    assert r.status_code == 200
    body = r.json()
    assert body["selection"]["algorithm"] == "unsupported"
    assert body["error"] is not None


def test_solve_exponent():
    r = client.post("/api/solve", json={
        "spec": {
            "problem_type": "exponent",
            "n": 10, "time_budget_ms": 100, "quality": "exact",
        },
        "payload": {"base": 2, "exp": 10},
    })
    assert r.status_code == 200
    body = r.json()
    assert body["selection"]["algorithm"] == "fast_exponent"
    assert body["result"]["solution"]["result"] == 1024


def test_experiment_routing_ranks():
    r = client.post("/api/experiment", json={
        "problem_type": "routing",
        "payload": {
            "graph": {
                "nodes": ["A", "B", "C"],
                "edges": [
                    {"u": "A", "v": "B", "w": 1},
                    {"u": "B", "v": "C", "w": 2},
                ],
                "source": "A",
            },
        },
    })
    assert r.status_code == 200
    body = r.json()
    assert body["problem_type"] == "routing"
    assert len(body["ranked"]) >= 1
