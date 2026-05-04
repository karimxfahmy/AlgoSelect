# Frontend

React + Vite + Tailwind v4 + Chart.js. Talks to the FastAPI backend on
`http://localhost:8000`.

## Run it

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`. The dev server expects the backend to
already be up — start it in another terminal first.

## Layout

- `src/api.js` — tiny fetch wrapper around the backend
- `src/components/` — one file per UI panel (input, recommendation card,
  solution viz, comparison table, decision flowchart)
- `src/App.jsx` — top-level layout; holds the active problem state
