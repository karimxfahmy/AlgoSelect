// thin wrapper around the FastAPI backend.
// uses VITE_API_BASE when set (production builds), falls back to the local
// dev backend so `npm run dev` works without any env file.
const BASE = (import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000') + '/api'

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    // try to surface the FastAPI detail field if it's there
    let detail = `${res.status} ${res.statusText}`
    try {
      const j = await res.json()
      if (j.detail) detail = j.detail
    } catch { /* not JSON, stick with status text */ }
    throw new Error(detail)
  }
  return res.json()
}

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const api = {
  health: () => get('/health'),
  algorithms: () => get('/algorithms'),
  select: (spec, payload) => post('/select', { spec, payload }),
  solve: (spec, payload) => post('/solve', { spec, payload }),
  experiment: (problem_type, payload) => post('/experiment', { problem_type, payload }),
}
