// the left-hand control panel.
// problem type dropdown, n + time-budget sliders, quality radios,
// and a couple of toggles for the per-family flags (negative weights,
// already sorted, force brute force).

export default function ProblemInput({ spec, onChange, onRun, onExperiment, busy }) {
  // helper to keep the parent's state update tidy
  const set = (patch) => onChange({ ...spec, ...patch })

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-5">
      <h2 className="text-lg font-semibold">Problem</h2>

      {/* problem type */}
      <label className="block">
        <span className="text-sm text-slate-400">Type</span>
        <select
          className="mt-1 w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5"
          value={spec.problem_type}
          onChange={(e) => set({ problem_type: e.target.value })}
        >
          <option value="knapsack">Knapsack (0/1)</option>
          <option value="routing">Routing (shortest paths)</option>
          <option value="sorting">Sorting</option>
          <option value="search">Search</option>
        </select>
      </label>

      {/* input size */}
      <label className="block">
        <div className="flex justify-between text-sm text-slate-400">
          <span>Input size n</span>
          <span className="text-slate-200">{spec.n}</span>
        </div>
        <input
          type="range"
          min={spec.problem_type === 'routing' ? 3 : 2}
          max={spec.problem_type === 'routing' ? 12 : 200}
          value={spec.n}
          onChange={(e) => set({ n: Number(e.target.value) })}
          className="w-full mt-1"
        />
        {/* small hint so users understand the brute-force ceilings */}
        <p className="text-xs text-slate-500 mt-1">
          {spec.problem_type === 'knapsack' && 'brute force capped at n=20'}
          {spec.problem_type === 'routing' && 'brute force capped at 8 nodes'}
          {spec.problem_type === 'sorting' && 'brute force capped at n=8'}
          {spec.problem_type === 'search' && 'binary search needs sorted input'}
        </p>
      </label>

      {/* time budget */}
      <label className="block">
        <div className="flex justify-between text-sm text-slate-400">
          <span>Time budget T</span>
          <span className="text-slate-200">{spec.time_budget_ms} ms</span>
        </div>
        <input
          type="range"
          min={1} max={5000} step={1}
          value={spec.time_budget_ms}
          onChange={(e) => set({ time_budget_ms: Number(e.target.value) })}
          className="w-full mt-1"
        />
      </label>

      {/* quality radios */}
      <fieldset>
        <legend className="text-sm text-slate-400 mb-1">Quality</legend>
        <div className="flex gap-3 text-sm">
          {['exact', 'approximate', 'best-effort'].map((q) => (
            <label key={q} className="flex items-center gap-1 cursor-pointer">
              <input
                type="radio" name="quality"
                checked={spec.quality === q}
                onChange={() => set({ quality: q })}
              />
              {q}
            </label>
          ))}
        </div>
      </fieldset>

      {/* problem-specific flags */}
      <div className="space-y-2 text-sm">
        {spec.problem_type === 'routing' && (
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={spec.has_negative_weights}
              onChange={(e) => set({ has_negative_weights: e.target.checked })}
            />
            Graph has negative edge weights
          </label>
        )}
        {spec.problem_type === 'search' && (
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={spec.is_sorted}
              onChange={(e) => set({ is_sorted: e.target.checked })}
            />
            Input is already sorted
          </label>
        )}
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={spec.force_brute_force}
            onChange={(e) => set({ force_brute_force: e.target.checked })}
          />
          Force brute force (correctness check)
        </label>
      </div>

      {/* action buttons */}
      <div className="flex gap-2 pt-2">
        <button
          onClick={onRun}
          disabled={busy}
          className="flex-1 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 transition rounded px-3 py-2 text-sm font-medium"
        >
          Run recommendation
        </button>
        <button
          onClick={onExperiment}
          disabled={busy}
          className="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 transition rounded px-3 py-2 text-sm font-medium"
        >
          Experiment mode
        </button>
      </div>
    </div>
  )
}
