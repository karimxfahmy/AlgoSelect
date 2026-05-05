# Frontend

React + Vite + Tailwind v4 + Chart.js. Talks to the FastAPI backend on
`http://localhost:8000` by default.

## Run it

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`. The dev server expects the backend to
already be up — start it in another terminal first.

## Build for production

```bash
npm run build
```

Output goes to `dist/`. Serve it as a static site (Netlify, Vercel, Railway
static, S3 + CloudFront — anything that serves static files works).

```bash
npm run preview
```

…serves the built `dist/` locally so you can sanity-check the production
bundle before shipping it.

## Configuration

The only knob is the backend URL.

| Variable        | Default                   | What it does                       |
| --------------- | ------------------------- | ---------------------------------- |
| `VITE_API_BASE` | `http://127.0.0.1:8000`   | Backend origin used by `api.js`.   |

For local dev the default is fine. For a deployed frontend, point
`VITE_API_BASE` at the deployed backend's URL (the `https://` scheme matters)
and run `npm run build` — Vite bakes the value into the bundle at build
time, not at runtime.

## Layout

- `src/api.js` — tiny fetch wrapper around the backend.
- `src/samples.js` — deterministic per-family sample generators (seeded so
  the same `n` always produces the same input).
- `src/components/` — one file per UI panel: `ProblemInput`,
  `RecommendationCard`, `SolutionView`, `ComparisonTable`, `DecisionFlow`.
- `src/App.jsx` — top-level layout; holds the active problem state, kicks
  off backend calls, and snapshots the payload at run time so dragging the
  size slider doesn't churn the result panels.
