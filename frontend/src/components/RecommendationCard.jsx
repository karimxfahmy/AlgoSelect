// shows the chosen algorithm + a one-paragraph justification.
// designed to be glanceable — heading, then the small print.

import { memo } from 'react'

const ALGO_LABELS = {
  knapsack_dp: 'Dynamic Programming — 0/1 Knapsack',
  brute_force_knapsack: 'Brute Force — Subset Enumeration',
  dijkstra_greedy: "Greedy — Dijkstra's Shortest Path",
  brute_force_routing: 'Brute Force — Permutation Routing',
  merge_sort: 'Divide & Conquer — Merge Sort',
  brute_force_sort: 'Brute Force — Permutation Sort',
  binary_search: 'Divide & Conquer — Binary Search',
  brute_force_search: 'Brute Force — Linear Search',
  fast_exponent: 'Divide & Conquer — Fast Exponentiation',
  naive_exponent: 'Brute Force — Repeated Multiplication',
  unsupported: 'No fitting algorithm available',
}

function RecommendationCardImpl({ selection, runtimeMs }) {
  if (!selection) return null
  const label = ALGO_LABELS[selection.algorithm] || selection.algorithm

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-500">Recommended</div>
          <h2 className="text-xl font-semibold mt-0.5">{label}</h2>
        </div>
        {/* runtime badge — only present after we actually ran the algo */}
        {runtimeMs !== undefined && runtimeMs !== null && (
          <div className="bg-slate-800 rounded px-2 py-1 text-xs text-emerald-300 whitespace-nowrap">
            {runtimeMs.toFixed(2)} ms
          </div>
        )}
      </div>

      <p className="text-slate-300 mt-3 leading-relaxed">{selection.justification}</p>

      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div className="bg-slate-800/60 rounded p-2">
          <div className="text-slate-500 text-xs">Expected complexity</div>
          <div className="font-mono text-slate-200">{selection.expected_complexity}</div>
        </div>
        <div className="bg-slate-800/60 rounded p-2">
          <div className="text-slate-500 text-xs">Quality guarantee</div>
          <div className="text-slate-200">{selection.quality_guarantee}</div>
        </div>
      </div>
    </div>
  )
}

export default memo(RecommendationCardImpl)
