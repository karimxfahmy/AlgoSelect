# Backend

FastAPI service that wraps the algorithm engine.

## Run it

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # on Windows; source .venv/bin/activate elsewhere
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs land at `http://localhost:8000/docs` once it's up.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Three suites:

- `tests/test_algorithms.py` — unit tests for each algorithm module.
- `tests/test_engine.py` — selector + experiment runner.
- `tests/test_api.py` — HTTP-level smoke tests through `httpx`.

## Benchmarks

The numbers in [`docs/algorithm-comparison.md`](../docs/algorithm-comparison.md)
come from this script:

```bash
python scripts/bench.py
```

It runs every applicable algorithm on the same seeded inputs at a few sizes
and prints a comparison table. Re-run it after any algorithm change to
refresh the report.

## Endpoints

| Method | Path                | What it does                                       |
| ------ | ------------------- | -------------------------------------------------- |
| GET    | `/api/health`       | Liveness check.                                    |
| GET    | `/api/algorithms`   | List of supported algorithms grouped by family.    |
| POST   | `/api/select`       | Returns the selector's choice + decision trace.    |
| POST   | `/api/solve`        | Selects + runs the chosen algorithm.               |
| POST   | `/api/experiment`   | Runs every applicable algorithm and ranks them.    |

Full OpenAPI schema lives at `/docs` (Swagger UI) and `/redoc`.

## Layout

- `app/algorithms/` — the four algorithm families. Each one is a
  self-contained module so they're easy to test in isolation.
- `app/engine/` — the rule-based selector and the experiment runner.
- `app/api/` — request/response schemas and the FastAPI route handlers.
- `tests/` — pytest tests for the algorithms, the engine, and the HTTP API.
- `scripts/bench.py` — reproducible benchmark used by the comparison report.
