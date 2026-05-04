// experiment-mode results table. one row per algorithm, ranked best-first.
// shows runtime, value, approximation ratio, and any skipped reasons.

import { memo } from 'react'

function ComparisonTableImpl({ experiment }) {
  if (!experiment) return null
  const { ranked, problem_type, best_value } = experiment

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">Algorithm comparison</h2>
        {best_value !== null && best_value !== undefined && (
          <div className="text-xs text-slate-500">
            best value: <span className="text-slate-200">{best_value}</span>
          </div>
        )}
      </div>

      <div className="overflow-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-500 text-xs uppercase">
            <tr>
              <th className="text-left py-1">#</th>
              <th className="text-left py-1">Algorithm</th>
              <th className="text-left py-1">Value</th>
              <th className="text-left py-1">Runtime</th>
              <th className="text-left py-1">Approx ratio</th>
              <th className="text-left py-1">Notes</th>
            </tr>
          </thead>
          <tbody>
            {ranked.map((r, i) => {
              if (r.skipped) {
                return (
                  <tr key={r.algorithm} className="border-t border-slate-800 opacity-60">
                    <td className="py-1.5">—</td>
                    <td className="py-1.5">{r.algorithm}</td>
                    <td colSpan={4} className="py-1.5 text-slate-500 italic">
                      skipped — {r.reason}
                    </td>
                  </tr>
                )
              }
              const isBest = i === 0
              return (
                <tr key={r.algorithm} className="border-t border-slate-800">
                  <td className="py-1.5 text-slate-500">{i + 1}</td>
                  <td className={`py-1.5 font-medium ${isBest ? 'text-emerald-400' : ''}`}>
                    {r.algorithm}
                    {isBest && <span className="ml-2 text-xs text-emerald-500">★ best</span>}
                  </td>
                  <td className="py-1.5">{formatValue(problem_type, r.value)}</td>
                  <td className="py-1.5">{r.runtime_ms?.toFixed(3)} ms</td>
                  <td className="py-1.5">
                    {r.approximation_ratio !== null && r.approximation_ratio !== undefined
                      ? r.approximation_ratio.toFixed(3)
                      : '—'}
                  </td>
                  <td className="py-1.5 text-xs text-slate-400">{r.note}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default memo(ComparisonTableImpl)


// sorting/search use length / index as "value" which isn't very meaningful —
// hide it when it doesn't add information.
function formatValue(problem_type, v) {
  if (v === null || v === undefined) return '—'
  if (problem_type === 'sorting' || problem_type === 'search') return '—'
  return typeof v === 'number' ? v.toFixed(2).replace(/\.00$/, '') : v
}
