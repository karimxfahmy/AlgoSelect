# AlgoSelect

A small problem-solving assistant that picks the right algorithm for the job.

You feed it a problem (knapsack, MST/routing, sorting, search, exponentiation),
tell it how big the input is and how long you're willing to wait, and it
figures out which of its four algorithm families is the best fit — Dynamic
Programming, Greedy, Divide and Conquer, or plain old Brute Force.

It then runs the chosen one and shows you why it picked it. There's also an
experiment mode that runs every applicable algorithm side by side so you can
compare them on the exact same input.

## Stack

- **Engine**: Python (pure, no heavy deps for the algorithms themselves)
- **API**: FastAPI
- **UI**: React + Tailwind v4
- **Charts**: Chart.js
- **Tests**: pytest

## What's implemented

### Algorithm families

- **Dynamic Programming** — 0/1 Knapsack (bottom-up table)
- **Greedy** — Dijkstra's shortest path
- **Divide and Conquer** — Merge Sort, Binary Search, Fast Exponentiation
- **Brute Force** — Subset-enumeration knapsack, permutation routing,
  permutation sort, linear search, naive O(n) exponent

### Engine

- Rule-based selector that picks an algorithm from `(problem_type, n,
  time_budget, quality, ...)` and returns a step-by-step decision trace.
- Experiment runner that runs every applicable algorithm on the same input
  and ranks them by runtime + approximation ratio.
- Hard caps on the brute-force solvers so the experiment runner can't lock
  up on combinatorial inputs.

### UI

- Problem-input panel with a per-family slider that resizes its range and
  step to the algorithm being tested.
- Recommendation card with the chosen algorithm, runtime, and a one-line
  justification.
- Per-family solution view (knapsack picks list, shortest-path table,
  sorted array, search index, exponent recursion trace) backed by Chart.js
  where it makes sense.
- Experiment-mode comparison table showing every applicable algorithm
  ranked by runtime, plus an SVG decision flowchart of the selector's path.

### Known gap

Matrix multiplication is in the spec's "trigger Divide & Conquer" list, but
no `matmul` solver was implemented. Strassen's algorithm would slot in
cleanly later — see [`docs/challenges.md`](docs/challenges.md) (item 4) for
the honest version.

## Quick start

You'll need two terminals — one for the backend, one for the frontend.

**Terminal 1 — backend (FastAPI on port 8000):**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # on Windows; source .venv/bin/activate elsewhere
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend (Vite on port 5173):**

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The interactive API docs land at
`http://localhost:8000/docs`.

See [`backend/README.md`](backend/README.md) and
[`frontend/README.md`](frontend/README.md) for the per-side details
(tests, build, configuration).

## Project structure

```
backend/
  app/
    algorithms/   # the four algorithm families, each self-contained
    engine/       # selector + experiment runner
    api/          # FastAPI routes + Pydantic schemas
  tests/          # pytest suite (algorithms, engine, http endpoints)
  scripts/
    bench.py      # benchmark used to produce the comparison report
frontend/
  src/
    components/   # one file per UI panel
    api.js        # fetch wrapper around the backend
    samples.js    # deterministic sample generators per problem type
docs/
  algorithm-comparison.md   # empirical DP-vs-brute-force-etc. report
  challenges.md             # build diary: real problems hit + how I fixed them
```

## Documentation

- [Algorithm comparison report](docs/algorithm-comparison.md) — empirical
  numbers behind the selector's thresholds.
- [Build diary](docs/challenges.md) — the real bugs, wrong turns, and fixes
  from building this.

## Team

- Karim Fahmy — [@karimxfahmy](https://github.com/karimxfahmy)
- Mahmoud Walid — [@Mahmoudeldeeb1](https://github.com/Mahmoudeldeeb1)
- Marwan Hassan — [@mrwanrakha](https://github.com/mrwanrakha)
