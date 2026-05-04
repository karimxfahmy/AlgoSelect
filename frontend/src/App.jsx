// top-level layout. holds the active problem spec, kicks off backend calls,
// and lays out the four panels: input on the left, results on the right.

import { useState, useMemo, useCallback } from 'react'
import { api } from './api'
import ProblemInput from './components/ProblemInput'
import RecommendationCard from './components/RecommendationCard'
import SolutionView from './components/SolutionView'
import ComparisonTable from './components/ComparisonTable'
import DecisionFlow from './components/DecisionFlow'
import {
  knapsackSample, routingSample, sortingSample, searchSample,
} from './samples'


// build the per-family payload from the current spec.
// kept here (not in the input component) because samples depend on n.
function buildPayload(spec) {
  switch (spec.problem_type) {
    case 'knapsack': return knapsackSample(spec.n)
    case 'routing':  return { graph: routingSample(spec.n) }
    case 'sorting':  return { array: sortingSample(spec.n) }
    case 'search':   return searchSample(spec.n)
    default: return {}
  }
}


export default function App() {
  const [spec, setSpec] = useState({
    problem_type: 'knapsack',
    n: 8,
    time_budget_ms: 500,
    quality: 'best-effort',
    has_negative_weights: false,
    is_sorted: true,           // sensible default for the search family
    force_brute_force: false,
  })
  const [solveResp, setSolveResp] = useState(null)
  const [experiment, setExperiment] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  // payload is derived, not stored — re-computed whenever spec changes.
  // keeps the UI in sync without an extra useEffect.
  const payload = useMemo(() => buildPayload(spec), [spec])

  const onRun = useCallback(async () => {
    setBusy(true); setError(null); setExperiment(null)
    try {
      const resp = await api.solve(spec, payload)
      setSolveResp(resp)
    } catch (e) {
      setError(e.message)
      setSolveResp(null)
    } finally {
      setBusy(false)
    }
  }, [spec, payload])

  const onExperiment = useCallback(async () => {
    setBusy(true); setError(null)
    try {
      const exp = await api.experiment(spec.problem_type, payload)
      setExperiment(exp)
      // also refresh the recommendation card so the user sees what would
      // have been picked if they'd hit "Run" instead.
      const sel = await api.select(spec, payload)
      setSolveResp({ selection: sel, result: null, error: null })
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }, [spec, payload])

  // also pull the result currently shown on the right (single-run preferred,
  // otherwise the top-ranked experiment row)
  const activeResult = solveResp?.result
    ?? experiment?.ranked?.find((r) => !r.skipped)
    ?? null

  return (
    <div className="min-h-screen">
      {/* header */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight">AlgoSelect</h1>
            <p className="text-xs text-slate-400">
              Multi-algorithm decision engine
            </p>
          </div>
          <a
            className="text-xs text-slate-400 hover:text-slate-200"
            href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer"
          >
            API docs ↗
          </a>
        </div>
      </header>

      {/* main grid */}
      <main className="max-w-7xl mx-auto px-6 py-6 grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6">
        <div className="space-y-4">
          <ProblemInput
            spec={spec} onChange={setSpec}
            onRun={onRun} onExperiment={onExperiment}
            busy={busy}
          />
          {error && (
            <div className="bg-rose-950/60 border border-rose-900 text-rose-200 text-sm rounded p-3">
              {error}
            </div>
          )}
          {/* show the decision flow on the left under the inputs — keeps the
              right column free for solution output */}
          <DecisionFlow selection={solveResp?.selection} />
        </div>

        <div className="space-y-4">
          {!solveResp && !experiment && (
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-10 text-center text-slate-400">
              Configure a problem on the left and hit "Run recommendation" to
              see what AlgoSelect picks for you.
            </div>
          )}

          <RecommendationCard
            selection={solveResp?.selection}
            runtimeMs={activeResult?.runtime_ms}
          />
          <SolutionView result={activeResult} payload={payload} />
          <ComparisonTable experiment={experiment} />
        </div>
      </main>

      <footer className="text-center text-xs text-slate-600 py-6">
        DP · Greedy · Divide &amp; Conquer · Brute Force
      </footer>
    </div>
  )
}
