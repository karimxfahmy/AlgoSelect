# Backend

FastAPI service that wraps the algorithm engine.

## Run it

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs land at `http://localhost:8000/docs` once it's up.

## Layout

- `app/algorithms/` — the four algorithm families. Each one is a self-contained
  module so they're easy to test in isolation.
- `app/engine/` — the rule-based selector and the experiment runner.
- `app/api/` — request/response schemas and the FastAPI route handlers.
- `tests/` — pytest tests for the algorithms and the selector.
