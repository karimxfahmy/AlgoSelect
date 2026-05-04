// renders the actual algorithm output. each problem family gets its own
// little sub-component; the wrapper just dispatches on problem_type.

import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  Title, Tooltip, Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)


export default function SolutionView({ result, payload }) {
  if (!result) return null
  const t = result.problem_type

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Solution</h2>
        <div className="text-xs text-slate-500">
          {result.algorithm} · {result.runtime_ms.toFixed(3)} ms
        </div>
      </div>

      {t === 'knapsack' && <KnapsackView result={result} payload={payload} />}
      {t === 'routing'  && <RoutingView result={result} />}
      {t === 'sorting'  && <SortingView result={result} payload={payload} />}
      {t === 'search'   && <SearchView result={result} payload={payload} />}
      {t === 'exponent' && <ExponentView result={result} payload={payload} />}

      {result.note && (
        <p className="text-xs text-slate-500 italic border-t border-slate-800 pt-3">
          {result.note}
        </p>
      )}
    </div>
  )
}


// ---------- knapsack ----------

function KnapsackView({ result, payload }) {
  const { value, items, weight_used } = result.solution
  const cap = payload?.capacity
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-2 text-center text-sm">
        <Stat label="Total value" value={value} accent="text-emerald-400" />
        <Stat label="Weight used" value={`${weight_used}${cap ? ` / ${cap}` : ''}`} />
        <Stat label="Items chosen" value={items.length} />
      </div>

      {/* selected items as little cards */}
      <div className="flex flex-wrap gap-2">
        {items.map((idx) => (
          <div key={idx} className="bg-slate-800 rounded px-2 py-1 text-xs">
            <div className="text-slate-500">item #{idx}</div>
            <div className="text-slate-200">
              w={payload?.weights?.[idx]} · v={payload?.values?.[idx]}
            </div>
          </div>
        ))}
      </div>

      {/* DP table preview if we have one */}
      {result.trace?.dp_table && Array.isArray(result.trace.dp_table) && (
        <DpTable table={result.trace.dp_table} />
      )}
    </div>
  )
}

function DpTable({ table }) {
  // big tables get clamped — readability beats completeness here
  const maxRows = 12
  const maxCols = 16
  const rows = table.slice(0, maxRows)
  return (
    <div className="text-xs overflow-auto border border-slate-800 rounded">
      <div className="text-slate-500 px-2 py-1 border-b border-slate-800">
        DP table {table.length > maxRows && `(showing first ${maxRows} rows)`}
      </div>
      <table className="font-mono">
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {row.slice(0, maxCols).map((cell, j) => (
                <td
                  key={j}
                  className={`px-2 py-0.5 ${i === 0 || j === 0 ? 'text-slate-500' : 'text-slate-200'}`}
                >
                  {cell}
                </td>
              ))}
              {row.length > maxCols && <td className="px-2 text-slate-600">…</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


// ---------- routing ----------

function RoutingView({ result }) {
  const { distances, paths, source } = result.solution
  const rows = Object.keys(distances).filter((n) => n !== source)
  return (
    <div className="space-y-3">
      <div className="text-sm text-slate-400">
        Source: <span className="text-slate-100 font-medium">{source}</span>
      </div>
      <div className="overflow-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-500 text-xs uppercase">
            <tr>
              <th className="text-left py-1">Target</th>
              <th className="text-left py-1">Distance</th>
              <th className="text-left py-1">Path</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((n) => (
              <tr key={n} className="border-t border-slate-800">
                <td className="py-1.5 font-medium">{n}</td>
                <td className="py-1.5">{distances[n] === null ? '∞' : distances[n]}</td>
                <td className="py-1.5 font-mono text-slate-300">
                  {paths[n].length ? paths[n].join(' → ') : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


// ---------- sorting ----------

function SortingView({ result, payload }) {
  const sorted = result.solution.sorted
  const original = payload?.array || []
  // bar chart helps eyeball the change
  const data = {
    labels: sorted.map((_, i) => i.toString()),
    datasets: [
      { label: 'sorted', data: sorted, backgroundColor: '#34d399' },
    ],
  }
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 text-xs">
        <ArrayStrip label="Original" arr={original} />
        <ArrayStrip label="Sorted" arr={sorted} highlight />
      </div>
      <div className="bg-slate-950/40 rounded p-2">
        <Bar
          data={data}
          options={{
            plugins: { legend: { display: false } },
            scales: {
              x: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
              y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
            },
          }}
          height={120}
        />
      </div>
    </div>
  )
}

function ArrayStrip({ label, arr, highlight }) {
  // truncate so the strip stays readable
  const shown = arr.slice(0, 24)
  return (
    <div>
      <div className="text-slate-500 mb-1">{label}</div>
      <div className="flex flex-wrap gap-1 font-mono">
        {shown.map((x, i) => (
          <span
            key={i}
            className={`px-1.5 py-0.5 rounded text-[11px] ${highlight ? 'bg-emerald-900/40 text-emerald-200' : 'bg-slate-800 text-slate-300'}`}
          >
            {x}
          </span>
        ))}
        {arr.length > shown.length && (
          <span className="text-slate-500 text-[11px]">+{arr.length - shown.length} more</span>
        )}
      </div>
    </div>
  )
}


// ---------- search ----------

function SearchView({ result, payload }) {
  const idx = result.solution.index
  const target = result.solution.target
  const arr = payload?.array || []
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 text-center text-sm">
        <Stat label="Target" value={target} />
        <Stat
          label="Index"
          value={idx === -1 ? 'not found' : idx}
          accent={idx === -1 ? 'text-amber-400' : 'text-emerald-400'}
        />
      </div>
      <div className="text-xs flex flex-wrap gap-1 font-mono">
        {arr.slice(0, 50).map((x, i) => (
          <span
            key={i}
            className={`px-1.5 py-0.5 rounded ${i === idx ? 'bg-emerald-700 text-white' : 'bg-slate-800 text-slate-400'}`}
          >
            {x}
          </span>
        ))}
        {arr.length > 50 && <span className="text-slate-600">+{arr.length - 50} more</span>}
      </div>
    </div>
  )
}


// ---------- exponent ----------

function ExponentView({ result, payload }) {
  const { result: value, base, exp } = result.solution
  const trace = result.trace || {}
  // fast_exponent records the recursion `levels`, naive_exponent records
  // a single `states_evaluated` count. handle both.
  const levels = trace.levels || []
  const states = trace.states_evaluated

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-2 text-center text-sm">
        <Stat label="Base" value={base} />
        <Stat label="Exponent" value={exp} />
        <Stat label="Result" value={formatBig(value)} accent="text-emerald-400" />
      </div>

      {/* recursion trace for fast_exponent */}
      {levels.length > 0 && (
        <div>
          <div className="text-slate-500 text-xs mb-1">
            Recursion trace (depth {trace.recursion_depth})
          </div>
          <div className="bg-slate-950/40 rounded p-2 text-xs font-mono space-y-0.5 max-h-48 overflow-auto">
            {levels.map((lvl, i) => (
              <div key={i} className="text-slate-300">
                <span className="text-slate-500">depth {lvl.depth}:</span>{' '}
                {formatBig(lvl.base)}^{lvl.exp}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* state count for naive_exponent */}
      {states !== undefined && (
        <div className="text-xs text-slate-400">
          Multiplications performed: <span className="text-slate-200">{states}</span>
        </div>
      )}
    </div>
  )
}

// big numbers are easier to read with a thousands separator,
// but very big floats fall back to exponential notation
function formatBig(x) {
  if (typeof x !== 'number') return String(x)
  if (Math.abs(x) > 1e15) return x.toExponential(3)
  return Number.isInteger(x) ? x.toLocaleString() : x.toString()
}


// ---------- shared mini stat tile ----------

function Stat({ label, value, accent }) {
  return (
    <div className="bg-slate-800/60 rounded p-2">
      <div className="text-slate-500 text-xs">{label}</div>
      <div className={`text-lg font-semibold ${accent || 'text-slate-100'}`}>{value}</div>
    </div>
  )
}
