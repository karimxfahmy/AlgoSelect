// renders the selector's decision trace as a top-down flowchart.
// purely SVG — no graph layout library needed since it's always a chain
// of nodes (one per question) ending in the chosen algorithm.

export default function DecisionFlow({ selection }) {
  if (!selection || !selection.trace || selection.trace.length === 0) return null

  const steps = selection.trace
  const NODE_W = 320
  const NODE_H = 64
  const GAP = 28
  const PAD = 20
  // last node = chosen algorithm. add an implicit terminal step.
  const totalNodes = steps.length + 1
  const height = PAD * 2 + totalNodes * NODE_H + (totalNodes - 1) * GAP
  const width = PAD * 2 + NODE_W

  const nodes = steps.map((s, i) => ({
    x: PAD,
    y: PAD + i * (NODE_H + GAP),
    title: s.question,
    sub: s.answer,
    branch: s.branch,
    isTerminal: false,
  }))
  // terminal node
  nodes.push({
    x: PAD,
    y: PAD + steps.length * (NODE_H + GAP),
    title: 'Selected algorithm',
    sub: selection.algorithm,
    branch: '',
    isTerminal: true,
  })

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
      <h2 className="text-lg font-semibold mb-3">Decision flow</h2>
      <div className="overflow-auto">
        <svg width={width} height={height} className="block">
          {/* arrows between consecutive nodes */}
          {nodes.slice(0, -1).map((n, i) => {
            const next = nodes[i + 1]
            const x1 = n.x + NODE_W / 2
            const y1 = n.y + NODE_H
            const x2 = next.x + NODE_W / 2
            const y2 = next.y
            return (
              <g key={`edge-${i}`}>
                <line
                  x1={x1} y1={y1} x2={x2} y2={y2}
                  stroke="#475569" strokeWidth="1.5" markerEnd="url(#arrow)"
                />
                {/* edge label = branch taken */}
                {n.branch && (
                  <text
                    x={x1 + 8} y={(y1 + y2) / 2 + 4}
                    fontSize="11" fill="#94a3b8"
                  >
                    {n.branch}
                  </text>
                )}
              </g>
            )
          })}

          {/* arrow marker definition */}
          <defs>
            <marker
              id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
              markerWidth="6" markerHeight="6" orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569" />
            </marker>
          </defs>

          {/* nodes */}
          {nodes.map((n, i) => (
            <g key={`node-${i}`} transform={`translate(${n.x}, ${n.y})`}>
              <rect
                width={NODE_W} height={NODE_H} rx="8"
                fill={n.isTerminal ? '#065f46' : '#1e293b'}
                stroke={n.isTerminal ? '#10b981' : '#334155'}
              />
              <text x="12" y="22" fill="#cbd5e1" fontSize="12">
                {n.title}
              </text>
              <text x="12" y="44" fill={n.isTerminal ? '#a7f3d0' : '#f1f5f9'}
                    fontSize="14" fontWeight="600">
                {n.sub}
              </text>
            </g>
          ))}
        </svg>
      </div>
    </div>
  )
}
